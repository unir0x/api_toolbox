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

workers = int(os.getenv('GUNICORN_WORKERS', 5))  # Använder miljövariabeln eller standardvärdet 5 om variabeln inte finns
bind = '0.0.0.0:8000'
timeout = int(os.getenv('GUNICORN_TIMEOUT', 120))
worker_class = 'gevent'
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
accesslog = '/app/logs/access.log'  # Access loggfilens sökväg
errorlog = '/app/logs/error.log'  # Error loggfilens sökväg
