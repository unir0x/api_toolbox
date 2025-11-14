# File Converter API

**Version:** 2.1.9  
**Maintainer:** FSV @ Salix Business Partner AB

This project provides a secure and scalable API toolbox for various file conversion and utility tasks, managed via a simple web interface and a RESTful API. The application is containerized with Docker for easy deployment and scaling.

---

## Features

- **Dual Authentication System:**
  - **API Access:** Secured with hashed `X-API-Token` headers for programmatic access.
  - **Admin UI Access:** Protected by Basic Authentication (username/password).
- **Web-Based Admin Panel:**
  - Secure login to manage the application.
  - Full lifecycle management for API tokens (create, list, delete).
  - **Secure Token Handling:** API tokens are hashed before being stored. The raw token is displayed only once upon creation.
  - **Token Usage Tracking:** The admin panel displays when each token was last used, making it easy to prune unused tokens.
  - **Unique Descriptions:** Enforces unique descriptions for each token to prevent confusion.
  - Securely change the admin password.
- **Available API Services:**
  - **Base64:** Encode files to Base64 and decode Base64 strings back to files.
- **CSV to XLS:** Convert one or multiple CSV files to Excel (.xlsx) with selectable separators, optional tables, custom sheet names, and automatic per-sheet numbering.
- **Postman Collection:** Import `postman/ApiToolbox.postman_collection.json` for ready-made requests covering the admin, Base64, and CSV services.
- **Configuration & Logging:**
  - Centralized configuration via a `settings.json` file, created from a template on first run.
  - **Rotating Log Files:** Application logs are automatically rotated to prevent them from growing indefinitely (max 10MB per file, 5 backups).
- **Scalability & Deployment:**
  - Uses Redis for session storage and rate limiting, enabling horizontal scaling with multiple workers.
  - Deployed as a multi-container application using Docker Compose (application + Redis).
  - Optimized, multi-platform Docker image (`linux/amd64` and `linux/arm64`) for production.

---

## Deployment with Portainer

This is the recommended method for deploying the application in a production environment.

### Prerequisites

- A server with Docker and Portainer installed.
- A local machine with `git` to clone the repository.

### Instructions

1.  **Prepare the Server:**
    - Create a directory on your server where you want to store the application's configuration and logs, for example:
      ```bash
      mkdir /opt/api-toolbox
      cd /opt/api-toolbox
      ```
    - Inside this directory, create two subdirectories:
      ```bash
      mkdir config
      mkdir logs
      ```

2.  **Deploy in Portainer:**
    - Log in to your Portainer instance.
    - Go to **Stacks** and click **Add stack**.
    - Give the stack a name (e.g., `api-toolbox-stack`).
    - In the **Web editor**, paste the contents of the `docker-compose.portainer.yml` file from this repository.
    - Under the **Environment variables** section, add a new variable for the application's secret key:
      - **Name:** `SECRET_KEY`
      - **Value:** Generate a strong, random string. You can use `openssl rand -base64 32` or a similar tool.
    - Click **Deploy the stack**.

3.  **First-Time Setup:**
    - The first time the application starts, it will create a `settings.json` file inside the `config` directory you created.
    - Access the admin panel by navigating to `http://<your-server-ip>:8000/admin`.
    - Log in with the default credentials:
      - **Username:** `admin`
      - **Password:** `change_me`
    - **Immediately change the admin password** using the "Admin Password Management" section.

---

## Local Development

These instructions are for running the application on a local machine for development and testing.

### Prerequisites

- Docker and Docker Compose installed on your local machine.

### Instructions

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd api_toolbox
    ```

2.  **Create Environment File:**
    - Create a file named `.env` in the project root.
    - Add a `SECRET_KEY` to this file. Generate a strong, random string for this value.
      ```
      SECRET_KEY='your_super_secret_random_string_here'
      ```

3.  **Build and Run:**
    - Use the standard `docker-compose.yml` file to build and run the containers:
      ```bash
      docker-compose up --build -d
      ```

4.  **Access the Application:**
    - **Admin Panel:** `http://localhost:8000/admin`
    - **Swagger UI:** `http://localhost:8000/swagger/`
    - The same first-time setup steps as in the Portainer deployment apply.

### Postman Collection

- A curated Postman collection lives in `postman/ApiToolbox.postman_collection.json`. Import it and configure an environment with:
  - `base_url` (e.g., `http://localhost:8000`)
  - `api_token` for API requests
  - `admin_auth_header` (`Basic <base64(admin:password)>`) for the admin endpoints
- The collection demonstrates health checks, Base64 tools, multi-file CSV⇢XLSX conversion, and admin token management.
