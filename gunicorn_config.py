# debug:    Loggar mycket detaljerad debug-information. 
#           Användbar för utveckling och felsökning, men kan generera en stor mängd loggdata, vilket kan påverka prestandan.
#
# info:     Loggar grundläggande informationsmeddelanden som standard. 
#           Detta inkluderar startmeddelanden samt begäranden och responsinformation vid standardnivå.
#
# warning:  Loggar varningar och allt som är mer kritiskt. 
#           Detta inkluderar potentiella problem som inte stoppar applikationen men som bör uppmärksammas.
#
# error:    Loggar endast felmeddelanden som indikerar problem som förhindrar vissa funktioner från att köras som förväntat.
#
# critical: Loggar endast de meddelanden som indikerar allvarliga problem som kan påverka applikationens tillgänglighet eller stabilitet.

import os
import logging
from logging.handlers import RotatingFileHandler

#workers = int(os.getenv('GUNICORN_WORKERS', 5))  # Använder miljövariabeln eller standardvärdet 5 om variabeln inte finns
#bind = '0.0.0.0:8000'
#timeout = int(os.getenv('GUNICORN_TIMEOUT', 120))
#worker_class = 'gevent'
#loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
#accesslog = '/app/logs/access.log'  # Access loggfilens sökväg
#errorlog = '/app/logs/error.log'  # Error loggfilens sökväg

def ensure_logfile_directory_exists(path):
    # Säkerställer att mappen för loggfilen finns. Skapar mappen om nödvändigt.
    os.makedirs(os.path.dirname(path), exist_ok=True)

def custom_rotating_file_handler(path, maxBytes=10485760, backupCount=5):
    # Skapar en anpassad RotatingFileHandler.
    # maxBytes: Maximal storlek för en loggfil i bytes, standard är 10MB.
    # backupCount: Antalet backup-filer att behålla, standard är 5.
    ensure_logfile_directory_exists(path)
    return RotatingFileHandler(path, maxBytes=maxBytes, backupCount=backupCount)

# Loggkonfiguration
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
accesslog_path = '/app/logs/access.log'
errorlog_path = '/app/logs/error.log'

# Använd anpassade RotatingFileHandlers för access och error loggar
access_log_handler = custom_rotating_file_handler(accesslog_path)
error_log_handler = custom_rotating_file_handler(errorlog_path)

# Övriga Gunicorn-inställningar
workers = int(os.getenv('GUNICORN_WORKERS', 5))
bind = '0.0.0.0:8000'
timeout = int(os.getenv('GUNICORN_TIMEOUT', 20))
worker_class = 'gevent'
