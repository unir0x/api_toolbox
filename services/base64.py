from flask_restx import Namespace, Resource, reqparse
from flask import send_file
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from auth.auth import api_auth # Import the new api_auth
import base64
import binascii
from io import BytesIO
from config import Config
import logging

ns = Namespace('Base64', description='Base64 operations')

parser_encode = reqparse.RequestParser()
parser_encode.add_argument('bizDoc', location='files', type=FileStorage, required=True, help='The file to upload')
parser_encode.add_argument('filename', location='form', type=str, required=False, help='Name of the file being uploaded')

parser_decode = reqparse.RequestParser()
parser_decode.add_argument('base64', location='form', type=str, required=True, help='Base64-encoded file')
parser_decode.add_argument('filename', location='form', type=str, required=True, help='Name of the file')

@ns.route('/encode')
class Base64Encoder(Resource):
    @ns.expect(parser_encode)
    @ns.doc(security='apiKey')
    @api_auth.login_required
    def post(self):
        """Encode file to Base64"""
        args = parser_encode.parse_args()
        file = args['bizDoc']
        filename = args['filename']

        if not file:
            logging.warning("No file provided for encoding.")
            return {'message': 'No file provided'}, 400

        if not filename:
            filename = file.filename
        
        filename = secure_filename(filename)

        if file.content_length > Config.MAX_UPLOAD_FILE_SIZE:
            logging.warning(f"File too large for encoding: {filename}. Size: {file.content_length} bytes.")
            return {'message': f'File too large. Max size is {Config.MAX_UPLOAD_FILE_SIZE / (1024 * 1024)} MB'}, 413

        if not self.allowed_file(filename):
            logging.warning(f"File type not allowed for encoding: {filename}.")
            return {'message': 'File type not allowed'}, 400

        try:
            file_content = file.read()
            if not file_content:
                logging.warning(f"Empty file provided for encoding: {filename}.")
                return {'message': 'File is empty'}, 400
            encoded_content = base64.b64encode(file_content).decode('utf-8')
            logging.info(f"Successfully encoded file: {filename}.")
            return {
                'filename': filename,
                'base64': encoded_content
            }, 200
        except Exception as e:
            logging.error(f"Error encoding file {filename} to Base64: {e}", exc_info=True)
            return {'message': 'Error encoding file to Base64'}, 500

    def allowed_file(self, filename):
        ext = filename.rsplit('.', 1)[-1].lower()
        return ext in Config.ALLOWED_EXTENSIONS

@ns.route('/decode')
class Base64Decoder(Resource):
    @ns.expect(parser_decode)
    @ns.doc(security='apiKey')
    @api_auth.login_required
    def post(self):
        """Decode Base64 to a file"""
        args = parser_decode.parse_args()
        base64_content = args['base64']
        filename = args['filename']

        filename = secure_filename(filename)

        try:
            decoded_content = base64.b64decode(base64_content)
            stream = BytesIO(decoded_content)
            logging.info(f"Successfully decoded Base64 content to file: {filename}.")
            return send_file(
                stream,
                as_attachment=True,
                download_name=filename,
                mimetype='application/octet-stream'
            )
        except binascii.Error as e:
            logging.warning(f"Invalid Base64 content provided for decoding {filename}: {e}")
            return {'message': 'Invalid Base64 content'}, 400
        except Exception as e:
            logging.error(f"Error decoding Base64 content to file {filename}: {e}", exc_info=True)
            return {'message': 'Error decoding Base64'}, 500