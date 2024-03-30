from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template
from flask_restx import Api
from werkzeug.middleware.proxy_fix import ProxyFix
import logging

from auth.auth import auth

from services.to_base64 import ns as ns_base64
from services.csv_to_xls import ns as ns_csv2xls

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

@app.route('/')
def home():
    return render_template('index.html')

authorizations = {
    'basicAuth': {
        'type': 'basic',
        'in': 'header',
        'name': 'Authorization'
    }
}

api = Api(app, version='0.1.4', title='File Conversion API',
          description='API for converting files and encoding to Base64',
          doc='/swagger/',
          authorizations=authorizations,
          security='basicAuth')

api.add_namespace(ns_base64)
api.add_namespace(ns_csv2xls)

# Gunicorn loggningsintegration
if __name__ != '__main__':
    # Endast utföra detta om appen körs med Gunicorn
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    # Applicera samma loggkonfiguration till alla bibliotek som använder standardlogging
    logging.getLogger().handlers = gunicorn_logger.handlers
    logging.getLogger().setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    app.run(debug=False)
