# File Conversion API

Welcome to the File Conversion API, a Flask-based web service designed to offer simple and efficient ways to convert files and encode them to Base64. 
This API currently supports two main functionalities: converting CSV files to XLSX format and encoding files to Base64 strings.

## Features:

Base64 Encoding: Upload any file to get its contents encoded in Base64. This is particularly useful for transferring binary data over media that only supports text content.
CSV to XLSX Conversion: Converts CSV files with semicolon separators to XLSX format. This is useful for working with tabular content in various applications that require Excel format.


### Usage
Authentication
This API requires basic authentication. Username and password must be included in every request.

> [!IMPORTANT]
Important to change the username and password in the APP_CREDENTIALS environment variables used for API requests.


Base64 Encoding
---
```
Endpoint: /toBase64
Method: POST
Description: Submit a file and its filename to get the file's contents encoded in Base64.
Formdata:
file: The file to be encoded.
filename: The name of the file being uploaded.
```

CSV to XLSX Conversion
---
```
Endpoint: /csv2xls
Method: POST
Description: Submit a CSV file to convert it to XLSX format.
Formdata:
bizDoc: The CSV file to be converted.
create_table: To choose if the xlsx file will creat an table. (True or False)
```

Swagger UI
----------
For a more detailed overview of the API and to test its endpoints, navigate to the Swagger UI at **_http://<your.domain>/swagger/_** after starting the server.


