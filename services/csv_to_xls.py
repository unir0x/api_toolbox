from flask import send_file
from flask_restx import Namespace, Resource, reqparse, abort
from werkzeug.datastructures import FileStorage
import pandas as pd
import io
import os
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter
from auth.auth import auth

ns = Namespace('csv2xls', description='CSV to XLS operations')

# Uppdaterad parser utan table_style
parser = reqparse.RequestParser()
parser.add_argument('file', location='files', type=FileStorage, required=True, help='The CSV file to upload')
parser.add_argument(
    'create_table', 
    type=lambda x: x.lower() in ['true', '1', 't', 'yes'] if x else False,
    required=False, 
    default=False, 
    help='Indicates whether to create a table in the Excel file.'
)

@ns.route('')
class CsvToXlsConverter(Resource):
    @ns.expect(parser)
    @ns.doc(security='basicAuth')
    @auth.login_required
    def post(self):
        """Convert CSV file to Excel with optional table formatting."""
        args = parser.parse_args()
        file = args['file']
        create_table = args.get('create_table', False)

        if file and file.filename.endswith('.csv'):
            df = pd.read_csv(file.stream, sep=';')

            output = io.BytesIO()
            wb = Workbook()
            ws = wb.active

            for r in dataframe_to_rows(df, index=False, header=True):
                ws.append(r)

            adjust_column_widths(ws, df)

            # Skapa en tabell med standardstilen 'TableStyleMedium9'
            if create_table:
                generate_table(ws, 'TableStyleMedium2')
                
            wb.save(output)
            output.seek(0)
            
            original_filename_base = os.path.splitext(file.filename)[0]
            new_filename = f"{original_filename_base}.xlsx"

            return send_file(output, mimetype='application/vnd.openpyxlformats-officedocument.spreadsheetml.sheet', download_name=new_filename, as_attachment=True)
        
        ns.abort(400, 'Invalid file format. Only .csv files are supported.')

def adjust_column_widths(ws, df):
    extra_space = 2
    for column_cells in ws.columns:
        max_length = max(len(str(cell.value)) for cell in column_cells) + extra_space
        column_letter = get_column_letter(column_cells[0].column)
        ws.column_dimensions[column_letter].width = max_length

def generate_table(ws, table_style_name):
    """Skapar en tabell i ett Excel-ark med angiven stil."""
    tab = Table(displayName="Table1", ref=f"A1:{get_column_letter(ws.max_column)}{ws.max_row}")
    style = TableStyleInfo(name=table_style_name, showFirstColumn=False,
                           showLastColumn=False, showRowStripes=True, showColumnStripes=True)
    tab.tableStyleInfo = style
    ws.add_table(tab)
