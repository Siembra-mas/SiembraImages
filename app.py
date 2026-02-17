import os
import boto3
from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
from datetime import datetime
from PIL import Image
from dotenv import load_dotenv

load_dotenv() 

app = Flask(__name__)
#app.secret_key = 'siembrasnap-secret-key' # Clave para mensajes flash

# Configuración AWS
S3_BUCKET = "siembrasnap-nando-2026"
ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION = os.getenv('AWS_REGION', 'us-east-1')

s3_client = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist('file')
    cultivo = request.form.get('cultivo', 'general')
    enfermedad = request.form.get('enfermedad', 'desconocida')

    if not files or files[0].filename == '':
        flash("No seleccionaste ningún archivo")
        return index()

    if len(files) > 10:
        flash("¡Ey! Solo 10 fotos a la vez, no te me emociones")
        return index()

    exitos = 0
    if not os.path.exists('uploads'): os.makedirs('uploads')

    for file in files:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nuevo_nombre = f"{timestamp}_{filename.rsplit('.', 1)[0]}.jpg"
        ruta_temp = os.path.join("uploads", nuevo_nombre)

        try:
            img = Image.open(file).convert('RGB')
            img.save(ruta_temp, optimize=True, quality=85)

            ruta_s3 = f"{cultivo}/{enfermedad}/{nuevo_nombre}"
            s3_client.upload_file(ruta_temp, S3_BUCKET, ruta_s3)
            
            os.remove(ruta_temp)
            exitos += 1
        except Exception as e:
            print(f"Error: {e}")

    return render_template('success.html', cantidad=exitos)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    
    # Cambiamos host a 0.0.0.0 para Docker
    app.run(debug=True, host='0.0.0.0', port=5000)