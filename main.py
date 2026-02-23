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
    
    # --- ARREGLO DE SEGURIDAD ---
    user_val = session.get('user')
    if user_val and '@' in user_val:
        usuario = user_val.split('@')[0]
    else:
        usuario = 'usuario_desconocido'
    # ----------------------------

    if not files or files[0].filename == '':
        flash("No seleccionaste ningún archivo.")
        return redirect(url_for('main.dashboard'))

    exitos = 0
    if not os.path.exists('uploads'): 
        os.makedirs('uploads')

    for file in files:
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

    return render_template('success.html', cantidad=exitos, ruta=f"{usuario}/{cultivo}/{estado}/")

@main_bp.route('/galeria')
@login_required
def galeria():
    # --- ARREGLO DE SEGURIDAD ---
    user_val = session.get('user')
    if user_val and '@' in user_val:
        usuario_id = user_val.split('@')[0]
    else:
        usuario_id = 'usuario_desconocido'
    # ----------------------------

    es_admin = session.get('is_admin', False) 
    prefijo_busqueda = "" if es_admin else f"{usuario_id}/"

    try:
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET,
            Prefix=prefijo_busqueda
        )

        imagenes = []
        if 'Contents' in response:
            for obj in response['Contents']:
                url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': S3_BUCKET, 'Key': obj['Key']},
                    ExpiresIn=3600
                )
                imagenes.append({
                    'url': url,
                    'key': obj['Key'],
                    'fecha': obj['LastModified']
                })
        
        if imagenes:
            imagenes = sorted(imagenes, key=lambda x: x['fecha'], reverse=True)

        # --- LÓGICA DE AGRUPAMIENTO PARA EL ADMIN ---
        imagenes_agrupadas = {}
        if es_admin:
            for img in imagenes:
                # Extraemos el nombre del usuario (el primer prefijo antes del '/')
                # Si la imagen está en la raíz, usamos 'General'
                partes = img['key'].split('/')
                usuario = partes[0] if len(partes) > 1 else "General"
                
                if usuario not in imagenes_agrupadas:
                    imagenes_agrupadas[usuario] = []
                imagenes_agrupadas[usuario].append(img)

        # Enviamos tanto la lista plana como el diccionario agrupado
        return render_template(
            'galeria.html', 
            imagenes=imagenes, 
            imagenes_agrupadas=imagenes_agrupadas, 
            admin=es_admin
        )

    except Exception as e:
        print(f"Error listando S3: {e}")
        flash("Error al cargar la galería.")
        return redirect(url_for('main.dashboard'))