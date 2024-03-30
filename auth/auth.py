from flask_httpauth import HTTPBasicAuth
from config import Config

auth = HTTPBasicAuth()
users = dict(item.split(':') for item in Config.APP_CREDENTIALS.split(','))

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username
