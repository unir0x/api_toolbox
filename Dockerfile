# Basera på den officiella Python-bilden från Docker Hub
FROM python:3.12-alpine

# Uppdatera paketindex och uppgradera befintliga paket
RUN apk update && \
    apk upgrade && \
    # Rensa cache för att minska storleken på den slutliga bilden
    rm -rf /var/cache/apk/*

# Sätt /app som arbetskatalog i containern
WORKDIR /app

# Kopiera över requirements.txt-filen och installera Python-beroenden
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Kopiera resten av applikationens källkod till /app i containern
COPY . .

# Exponera port 8000 för att kunna nås utanför containern
EXPOSE 8000

# Skapa sökväg för logfiler
RUN mkdir -p /app/logs

# Define environment variable
ENV APP_TITLE "File Conversion API v0.1.4"
ENV APP_CREDENTIALS="user1:passwrd1,user2:passwrd2"
ENV GUNICORN_WORKERS=5
ENV GUNICORN_LOG_LEVEL=info
ENV GUNICORN_TIMEOUT=120

# Ange startkommando för att köra applikationen med gunicorn
CMD ["gunicorn", "-c", "gunicorn_config.py", "main:app"]
