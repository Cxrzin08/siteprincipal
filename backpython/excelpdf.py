import os
from flask import Flask, request, render_template, send_file, url_for
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pdfplumber
import pandas as pd
from openpyxl import Workbook

app = Flask(__name__)

# Configuração da pasta e tamanho máximo do arquivo
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # Limite de 10 MB

def is_valid_extension(filename, valid_extensions):
    """Verifica se o arquivo possui uma extensão válida."""
    return any(filename.lower().endswith(ext) for ext in valid_extensions)

@app.route("/", methods=["GET"])
def index():
    """Página inicial com formulário de upload."""
    return render_template("index.html", download_link=None)

@app.route("/convert", methods=["POST"])
def convert():
    """Converte arquivos entre PDF e Excel ou vice-versa."""
    file = request.files.get("file")
    conversion_type = request.form.get("conversionType")

    if not file or not conversion_type:
        return "Arquivo ou tipo de conversão não selecionado.", 400

    input_filename = secure_filename(file.filename)
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], input_filename)
    file.save(input_path)

    output_filename = f"converted_{os.path.splitext(input_filename)[0]}"
    output_path = None

    try:
        if conversion_type == "pdf-to-excel":
            if not is_valid_extension(input_filename, [".pdf"]):
                return "Erro: Para PDF para Excel, o arquivo enviado deve ser um PDF.", 400
            output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_filename + ".xlsx")
            convert_pdf_to_excel(input_path, output_path)
        elif conversion_type == "excel-to-pdf":
            if not is_valid_extension(input_filename, [".xlsx"]):
                return "Erro: Para Excel para PDF, o arquivo enviado deve ser um Excel (.xlsx).", 400
            output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_filename + ".pdf")
            convert_excel_to_pdf(input_path, output_path)
        else:
            return "Tipo de conversão inválido.", 400
    except Exception as e:
        return f"Erro inesperado: {str(e)}", 500

    download_link = url_for("download_file", filename=os.path.basename(output_path))
    return render_template("index.html", download_link=download_link)

@app.route("/download/<filename>")
def download_file(filename):
    """Baixa o arquivo convertido."""
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(file_path):
        return "Arquivo não encontrado.", 404
    return send_file(file_path, as_attachment=True)

def convert_pdf_to_excel(input_path, output_path):
    """Converte PDF para Excel mantendo layout básico."""
    try:
        # Lista para armazenar dados de todas as páginas
        all_data = []

        with pdfplumber.open(input_path) as pdf:
            for page in pdf.pages:
                # Extrair tabelas (se existirem) na página
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        # Adicionar cada tabela encontrada aos dados
                        all_data.extend(table)
                else:
                    # Caso não haja tabelas, extrair texto básico
                    lines = page.extract_text().split("\n")
                    all_data.append(lines)

        # Criar DataFrame a partir dos dados coletados
        df = pd.DataFrame(all_data)

        # Remover colunas e linhas que contenham apenas NaN
        df.dropna(how="all", inplace=True)
        df.dropna(axis=1, how="all", inplace=True)

        # Salvar em Excel
        df.to_excel(output_path, index=False, header=False)
    except Exception as e:
        raise Exception(f"Erro ao converter PDF para Excel: {str(e)}")

def convert_excel_to_pdf(input_path, output_path):
    """Converte Excel para PDF."""
    try:
        wb = pd.ExcelFile(input_path)
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        y = height - 50
        line_height = 12

        for sheet in wb.sheet_names:
            df = wb.parse(sheet)
            df = df.dropna(how="all", axis=0)
            df = df.dropna(how="all", axis=1)

            for _, row in df.iterrows():
                row_text = ", ".join([str(value) for value in row.values if pd.notna(value)])
                if y < 50:
                    c.showPage()
                    y = height - 50
                c.drawString(50, y, row_text)
                y -= line_height

        c.save()
    except Exception as e:
        raise Exception(f"Erro ao converter Excel para PDF: {str(e)}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)