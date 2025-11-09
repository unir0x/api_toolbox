import os
import json
import secrets
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from flask import Flask, session, send_from_directory, request
from flask_restx import Api, Resource, Namespace, reqparse
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_session import Session
import redis

# Import the new auth methods and the config object
from auth.auth import api_auth, admin_auth
from config import Config, SETTINGS_PATH
from services.base64 import ns as ns_base64
from services.csv_to_xls import ns as ns_csv2xls
from version import __version__, __app_title__, __last_updated__, __author__

load_dotenv(".env")

# --- Application Setup ---
# Serve the admin UI from a static folder
app = Flask(__name__, static_folder='admin', static_url_path='/admin')
app.wsgi_app = ProxyFix(app.wsgi_app)

# --- Configuration ---
app.config["SECRET_KEY"] = Config.SECRET_KEY.get_secret_value()
app.config["SESSION_TYPE"] = Config.SESSION_TYPE
app.config["SESSION_PERMANENT"] = Config.SESSION_PERMANENT
app.config["SESSION_REDIS"] = redis.Redis(
    host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=Config.REDIS_DB
)
Session(app)



# --- Logging Setup ---
log_file_path = Config.LOG_FILE
log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)

# Ensure log directory exists
log_dir = os.path.dirname(log_file_path)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Setup RotatingFileHandler for app.log
handler = RotatingFileHandler(
    log_file_path,
    maxBytes=Config.MAX_BYTES,
    backupCount=Config.BACKUP_COUNT
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s'
))

# Apply handler to Flask's app logger and the root logger
app.logger.addHandler(handler)
app.logger.setLevel(log_level)
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(log_level)

# --- API Setup ---
authorizations = {
    'apiKey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-Token'
    }
}

api = Api(
    app,
    version=__version__,
    title=__app_title__,
    description=f"Maintainer: {__author__} · Last revision: {__last_updated__}",
    doc='/swagger/',
    authorizations=authorizations
)

# --- Namespaces ---
ns_status = Namespace('Status', description='Status and health checks')
api.add_namespace(ns_status)
api.add_namespace(ns_base64)
api.add_namespace(ns_csv2xls)

@ns_status.route('/ping')
class Ping(Resource):
    @api.doc(security='apiKey')
    @api_auth.login_required
    def get(self):
        """Checks if the API is running and the user is authenticated via API Token."""
        return {'message': 'pong', 'authenticated_as': api_auth.current_user()}

# --- Health Check Endpoint ---
@app.route('/health')
def health_check():
    """A simple health check endpoint for Docker."""
    return {'status': 'ok'}, 200

# --- Admin UI and API ---
@app.route('/admin')
@app.route('/admin/')
def admin_index():
    """Serves the admin index.html page."""
    return send_from_directory(app.static_folder, 'index.html')

# Admin endpoints are protected by Basic Auth, not API Key.
ns_admin = Namespace('Admin', description='Admin operations', security=None)
api.add_namespace(ns_admin, path='/admin/api')

def write_settings(new_data):
    """Helper function to write updated data to settings.json."""
    with open(SETTINGS_PATH, 'w') as f:
        json.dump(new_data, f, indent=4)

@ns_admin.route('/tokens')
@ns_admin.doc(False) # Hide from Swagger UI
class AdminTokenManager(Resource):
    @admin_auth.login_required
    def get(self):
        """[Admin] List all API tokens."""
        # Convert Pydantic objects to JSON-serializable dicts before returning
        return {
            token_hash: token_data.model_dump()
            for token_hash, token_data in Config.API_TOKENS.items()
        }

    @admin_auth.login_required
    def post(self):
        """[Admin] Create a new API token."""
        parser = reqparse.RequestParser()
        parser.add_argument('description', type=str, required=True, help='Description for the new token')
        args = parser.parse_args()

        description = args['description']

        # Check if description already exists
        for token_data in Config.API_TOKENS.values():
            if token_data.description == description:
                return {'message': f'Description \'{description}\' already exists. Please use a unique description.'}, 409

        new_token = secrets.token_urlsafe(32)
        
        from auth.auth import hash_api_token
        from config import ApiToken
        
        hashed_token = hash_api_token(new_token)

        new_token_data = {
            "description": description,
            "last_used": None
        }

        with open(SETTINGS_PATH, 'r+') as f:
            settings_data = json.load(f)
            settings_data['API_TOKENS'][hashed_token] = new_token_data
            f.seek(0)
            json.dump(settings_data, f, indent=4)
            f.truncate()

        # Update in-memory config
        Config.API_TOKENS[hashed_token] = ApiToken(**new_token_data)
        
        # Return the original, unhashed token to the user
        return {'token': new_token, 'description': description}, 201

@ns_admin.route('/tokens/<string:token_hash>')
@ns_admin.doc(False) # Hide from Swagger UI
class AdminTokenDeleter(Resource):
    @admin_auth.login_required
    def delete(self, token_hash):
        """[Admin] Delete an API token by its hash."""
        try:
            with open(SETTINGS_PATH, 'r+') as f:
                settings_data = json.load(f)
                
                if token_hash in settings_data['API_TOKENS']:
                    # Delete from dictionary
                    del settings_data['API_TOKENS'][token_hash]
                    
                    # Go to start of file and write updated data
                    f.seek(0)
                    json.dump(settings_data, f, indent=4)
                    f.truncate()
                    
                    # Also delete from in-memory config
                    if token_hash in Config.API_TOKENS:
                        del Config.API_TOKENS[token_hash]
                        
                    return {'message': 'Token deleted'}, 200
                else:
                    return {'message': 'Token not found'}, 404
        except (IOError, json.JSONDecodeError) as e:
            logging.error(f"Error processing settings file during token deletion: {e}")
            return {'message': 'Server error while trying to delete token'}, 500

password_parser = reqparse.RequestParser()
password_parser.add_argument('old_password', type=str, required=True)
password_parser.add_argument('new_password', type=str, required=True)
password_parser.add_argument('confirm_password', type=str, required=True)

@ns_admin.route('/change-password')
@ns_admin.doc(False) # Hide from Swagger UI
class AdminPasswordChanger(Resource):
    @admin_auth.login_required
    def post(self):
        """[Admin] Change the admin password."""
        args = password_parser.parse_args()
        username = admin_auth.current_user()

        if args['new_password'] != args['confirm_password']:
            return {'message': 'New passwords do not match'}, 400
        
        from auth.auth import verify_admin_password, hash_password
        
        # Verify the old password is correct
        if not verify_admin_password(username, args['old_password']):
            return {'message': 'Old password is not correct'}, 403

        # Hash the new password and save it
        new_hashed_password = hash_password(args['new_password'])
        with open(SETTINGS_PATH, 'r') as f:
            settings_data = json.load(f)
        
        settings_data['ADMIN_CREDENTIALS'][username] = new_hashed_password
        write_settings(settings_data)
        Config.ADMIN_CREDENTIALS[username] = new_hashed_password

        return {'message': f'Password for user {username} changed successfully.'}, 200

if __name__ == '__main__':
    import logging
    # When running directly, listen on all interfaces and port 8000
    app.run(
        host='0.0.0.0', 
        port=8000, 
        debug=os.getenv("DEBUG", "false").lower() == "true"
    )

