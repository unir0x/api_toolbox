import logging
import json
from datetime import datetime, timezone
from flask import session
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config, SETTINGS_PATH

# --- API Authentication (X-API-Token Header) ---
# This tells flask-httpauth to look for the token in the 'X-API-Token' header
# and to not expect a scheme like 'Bearer'.
api_auth = HTTPTokenAuth(header='X-API-Token')

def hash_api_token(token):
    """Generates a hash for an API token for secure storage."""
    return generate_password_hash(token)

@api_auth.verify_token
def verify_api_token(token):
    """
    Verify an API token from the X-API-Token header.
    The incoming token is hashed and compared against stored hashed tokens.
    If valid, the 'last_used' timestamp is updated.
    Returns the description of the token if valid, otherwise None.
    """
    logging.debug(f"--- Verifying API Token ---")
    logging.debug(f"Incoming raw token: {token[:8]}...")
    for stored_hash, token_data in Config.API_TOKENS.items():
        logging.debug(f"Comparing with stored hash: {stored_hash[:15]}... for desc: '{token_data.description}'")
        is_match = check_password_hash(stored_hash, token)
        logging.debug(f"Result of check_password_hash: {is_match}")
        if is_match:
            # Token is valid, update last_used timestamp
            now_utc = datetime.now(timezone.utc).isoformat()
            
            # Update in-memory config first
            token_data.last_used = now_utc
            
            # Asynchronously update the settings.json file
            try:
                with open(SETTINGS_PATH, 'r+') as f:
                    settings_data = json.load(f)
                    if stored_hash in settings_data['API_TOKENS']:
                        settings_data['API_TOKENS'][stored_hash]['last_used'] = now_utc
                        f.seek(0)
                        json.dump(settings_data, f, indent=4)
                        f.truncate()
            except (IOError, json.JSONDecodeError) as e:
                logging.error(f"Failed to update last_used for token: {e}")

            logging.info(f"API access by token: {token_data.description}")
            return token_data.description # Return the description for the current user context

    logging.warning(f"❌ Invalid API token provided: {token[:8]}...") # Log only a truncated token
    return None

# --- Admin UI Authentication (Basic Auth) ---
admin_auth = HTTPBasicAuth()

@admin_auth.verify_password
def verify_admin_password(username, password):
    """
    Verify admin credentials for the web UI.
    """
    expected_password = Config.ADMIN_CREDENTIALS.get(username)
    logging.debug(f"DEBUG: verify_admin_password - username: {username}")
    
    if not expected_password:
        logging.warning(f"❌ Invalid admin login attempt for non-existent user: {username}")
        return None

    is_valid = False
    if expected_password == "change_me":
        if password == "change_me":
            is_valid = True
    else:
        if check_password_hash(expected_password, password):
            is_valid = True
    
    if is_valid:
        session['admin_user'] = username
        return username

    logging.warning(f"❌ Invalid admin password for user: {username}")
    return None

# --- Password Hashing Utility ---
def hash_password(password):
    """Generates a salted and hashed password."""
    return generate_password_hash(password)
