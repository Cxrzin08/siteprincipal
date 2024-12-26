import os
from flask import Flask, request, render_template, send_file, url_for
from werkzeug.utils import secure_filename
from moviepy.editor import AudioFileClip

app = Flask(__name__)

# Configuração da pasta e tamanho máximo do arquivo
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
OUTPUT_FOLDER = os.path.join(os.getcwd(), "converted")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 1000 * 1024 * 1024  # Limite de 1 GB


def is_valid_extension(filename, valid_extensions):
    """Verifica se o arquivo possui uma extensão válida."""
    return any(filename.lower().endswith(ext) for ext in valid_extensions)


@app.route("/", methods=["GET"])
def index():
    """Página inicial com formulário de upload."""
    return render_template("index.html", download_link=None)


@app.route("/convert", methods=["POST"])
def convert():
    """Converte arquivos de vídeo para MP3."""
    file = request.files.get("file")
    conversion_type = request.form.get("conversionType")

    if not file:
        return "Nenhum arquivo enviado.", 400

    input_filename = secure_filename(file.filename)

    # Definir extensões válidas com base na seleção do usuário
    if conversion_type == "mp4-to-mp3":
        valid_extensions = [".mp4"]
    elif conversion_type == "m4v-to-mp3":
        valid_extensions = [".m4v"]
    else:
        return "Tipo de conversão inválido.", 400

    if not is_valid_extension(input_filename, valid_extensions):
        return f"Erro: O arquivo deve ser {', '.join(valid_extensions).upper()}.", 400

    input_path = os.path.join(app.config["UPLOAD_FOLDER"], input_filename)
    file.save(input_path)

    output_filename = f"converted_{os.path.splitext(input_filename)[0]}.mp3"
    output_path = os.path.join(app.config["OUTPUT_FOLDER"], output_filename)

    try:
        convert_video_to_audio(input_path, output_path)
    except Exception as e:
        return f"Erro inesperado: {str(e)}", 500

    download_link = url_for("download_file", filename=output_filename)
    return render_template("index.html", download_link=download_link)


@app.route("/download/<filename>")
def download_file(filename):
    """Baixa o arquivo convertido."""
    file_path = os.path.join(app.config["OUTPUT_FOLDER"], filename)
    if not os.path.exists(file_path):
        return "Arquivo não encontrado.", 404
    return send_file(file_path, as_attachment=True)


def convert_video_to_audio(input_path, output_path):
    """Converte um arquivo de vídeo (MP4 ou M4V) para áudio MP3."""
    try:
        audio_clip = AudioFileClip(input_path)
        audio_clip.write_audiofile(output_path)
        audio_clip.close()
    except Exception as e:
        raise Exception(f"Erro ao converter vídeo para áudio: {str(e)}")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)