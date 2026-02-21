from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import boto3
import os
from datetime import datetime
from werkzeug.utils import secure_filename # Para limpiar nombres de archivos
from PIL import Image                       # Para procesar imágenes
from auth import login_required             # Importas el decorador que creamos en auth.py

main_bp = Blueprint('main', __name__)

# --- CONFIGURACIÓN AWS ---
S3_BUCKET = os.getenv('AWS_S3_BUCKET', "siembrasnap-prod-2026")
ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION = os.getenv('AWS_REGION', 'us-east-1')


s3_client = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION
)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/')
def welcome():
    return render_template('welcome.html')

@main_bp.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    return render_template('index.html')

@main_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    files = request.files.getlist('file')
    cultivo = request.form.get('cultivo', 'general')
    estado = request.form.get('estado', 'desconocido')
    
    usuario = session.get('user', 'anonimo').split('@')[0]

    # 1. Validación inicial: ¿Vino algo en la petición?
    if not files or files[0].filename == '':
        flash("No seleccionaste ningún archivo.")
        return redirect(url_for('main.dashboard'))

    exitos = 0
    if not os.path.exists('uploads'): 
        os.makedirs('uploads')

    # 2. Procesamiento real
    for file in files:
        # Solo procesamos si la extensión es permitida
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_final = f"img_{timestamp}_{exitos}.jpg"
            ruta_temp = os.path.join("uploads", nombre_final)

            try:
                img = Image.open(file).convert('RGB')
                img.save(ruta_temp, "JPEG", optimize=True, quality=85)

                ruta_s3 = f"{usuario}/{cultivo}/{estado}/{nombre_final}"
                
                s3_client.upload_file(ruta_temp, S3_BUCKET, ruta_s3)
                os.remove(ruta_temp)
                exitos += 1
            except Exception as e:
                print(f"Error procesando archivo {filename}: {e}")
        else:
            print(f"Archivo omitido por extensión no válida: {file.filename}")

    # 3. Respuesta final (esto es lo que recibe el AJAX para mostrar success.html)
    return render_template('success.html', cantidad=exitos, ruta=f"{usuario}/{cultivo}/{estado}/")
