from flask_restx import Namespace, Resource, reqparse
from werkzeug.datastructures import FileStorage
from auth.auth import auth
import base64

ns = Namespace('toBase64', description='Base64 operations')

parser = reqparse.RequestParser()
parser.add_argument('bizDoc', location='files', type=FileStorage, required=True, help='The file to upload')
parser.add_argument('filename', location='form', type=str, required=True, help='Name of the file being uploaded')

@ns.route('')
class Base64Converter(Resource):
    @ns.doc(security='basicAuth', parser=parser, description='Encode any file to Base64. This can be useful for transmitting binary data over mediums that only support text content.')
    @auth.login_required
    def post(self):
        """Encode file to Base64"""
        args = parser.parse_args()
        file = args['bizDoc']
        filename = args['filename']
        if file:
            file_content = file.read()
            encoded_content = base64.b64encode(file_content).decode('utf-8')
            return {
                'filename': filename,
                'base64': encoded_content
            }, 200
        return {'message': 'Something went wrong'}, 400

