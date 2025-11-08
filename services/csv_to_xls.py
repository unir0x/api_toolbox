from flask import send_file
from flask_restx import Namespace, Resource, reqparse, abort
from werkzeug.datastructures import FileStorage
import csv
import io
import os
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter
from auth.auth import api_auth # Import the new api_auth
import logging

ns = Namespace('csv2xls', description='CSV to XLS operations')

# Define available choices for API parameters
SEPARATOR_CHOICES = ('comma', 'semicolon', 'tab')
TABLE_STYLE_CHOICES = ('TableStyleMedium2', 'TableStyleMedium9', 'TableStyleMedium15', 'TableStyleLight1', 'TableStyleDark1')
LANG_CHOICES = ('SV', 'DA', 'FI', 'NO', 'EN')

parser = reqparse.RequestParser()
parser.add_argument('file', location='files', type=FileStorage, required=True, help='The CSV file to upload')
parser.add_argument('separator', type=str, required=False, default='semicolon', choices=SEPARATOR_CHOICES, help='The separator used in the CSV file.')
parser.add_argument('create_table', type=lambda x: str(x).lower() in ['true', '1', 't', 'yes'], required=False, default=False, help='Indicates whether to create a table in the Excel file.')
parser.add_argument('table_style', type=str, required=False, default='TableStyleMedium9', choices=TABLE_STYLE_CHOICES, help='The visual style to apply to the Excel table.')
parser.add_argument('lang', type=str, required=False, default='SV', choices=LANG_CHOICES, help='Language code to determine the default sheet name (e.g., Blad1 for SV).')
parser.add_argument('author', type=str, required=False, default='NorthXL.se', help='The author property to set in the Excel file metadata.')
parser.add_argument('title', type=str, required=False, default='', help='The title property to set in the Excel file metadata.')
parser.add_argument('company', type=str, required=False, default='', help='The company property to set in the Excel file metadata.')

# --- Mappings ---
SEPARATOR_MAP = {'comma': ',', 'semicolon': ';', 'tab': '\t'}
SHEET_NAME_MAP = {'SV': 'Blad1', 'DA': 'Ark1', 'FI': 'Taulukko1', 'NO': 'Ark1', 'EN': 'Sheet1'}

@ns.route('')
class CsvToXlsConverter(Resource):
    @ns.expect(parser)
    @ns.doc(security='apiKey')
    @api_auth.login_required
    def post(self):
        """Convert CSV file to Excel with optional table formatting and custom metadata."""
        args = parser.parse_args()
        file = args['file']
        
        if not (file and file.filename.endswith('.csv')):
            abort(400, 'Invalid file format. Only .csv files are supported.')

        sep = SEPARATOR_MAP.get(args['separator'], ';')
        sheet_name = SHEET_NAME_MAP.get(args['lang'], 'Sheet1')

        output = io.BytesIO()
        wb = Workbook()
        wb.properties.creator = args['author']
        wb.properties.title = args['title']
        wb.properties.company = args['company']
        company = args['company']
        ws = wb.active
        ws.title = sheet_name

        try:
            # The FileStorage object's stream is iterable. We decode each line
            # to utf-8 to create a list of strings for the csv.reader.
            decoded_lines = (line.decode('utf-8') for line in file.stream)
            reader = csv.reader(decoded_lines, delimiter=sep)
            
            column_widths = []
            is_first_row = True

            for row in reader:
                if not row: # Skip empty rows
                    continue
                
                if is_first_row:
                    # Initialize column widths based on header length
                    column_widths = [len(cell) for cell in row]
                    is_first_row = False
                else:
                    # Update column widths based on cell content
                    for i, cell in enumerate(row):
                        if i < len(column_widths):
                            column_widths[i] = max(column_widths[i], len(str(cell)))
                        else:
                            # Handle rows with more columns than the header
                            column_widths.append(len(str(cell)))
                
                ws.append(row)

            if is_first_row: # File was empty or only contained empty rows
                 abort(400, 'The provided CSV file is empty.')

        except Exception as e:
            logging.error(f"Error processing CSV file: {e}")
            abort(400, f"Could not process CSV file. Please check the file format and the selected separator. Error: {e}")

        adjust_column_widths(ws, column_widths)

        if args['create_table']:
            generate_table(ws, args['table_style'])
            
        wb.save(output)
        output.seek(0)
        
        original_filename_base = os.path.splitext(file.filename)[0]
        new_filename = f"{original_filename_base}.xlsx"

        return send_file(
            output, 
            mimetype='application/vnd.openpyxlformats-officedocument.spreadsheetml.sheet', 
            download_name=new_filename, 
            as_attachment=True
        )

def adjust_column_widths(ws, column_widths):
    """Adjust column widths based on the longest value found in each column."""
    extra_space = 4
    for i, width in enumerate(column_widths, 1):
        column_letter = get_column_letter(i)
        ws.column_dimensions[column_letter].width = width + extra_space

def generate_table(ws, table_style_name):
    """Create a table in the worksheet with the specified style."""
    # Check if worksheet is empty before creating a table
    if ws.max_row == 0:
        return
    tab = Table(displayName="DataTable", ref=f"A1:{get_column_letter(ws.max_column)}{ws.max_row}")
    style = TableStyleInfo(
        name=table_style_name, 
        showFirstColumn=False,
        showLastColumn=False, 
        showRowStripes=True, 
        showColumnStripes=False
    )
    tab.tableStyleInfo = style
    ws.add_table(tab)
