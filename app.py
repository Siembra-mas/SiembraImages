import os
import boto3
from flask import Flask, render_template, request, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
from datetime import datetime
from PIL import Image
from dotenv import load_dotenv
from pycognito import Cognito
from functools import wraps

load_dotenv() 

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'siembrasnap-secret-key')

# --- CONFIGURACIÓN AWS ---
S3_BUCKET = os.getenv('AWS_S3_BUCKET', "siembrasnap-nando-2026")
ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION = os.getenv('AWS_REGION', 'us-east-1')
USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')

s3_client = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION
)

# --- SEGURIDAD: DECORADOR ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("Acceso restringido. Por favor inicia sesión.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- RUTAS DE ACCESO ---

@app.route('/')
def welcome():
    # Si ya está logueado, lo saltamos al dashboard
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('welcome.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            u = Cognito(USER_POOL_ID, CLIENT_ID)
            u.register(email, password)
            
            # 1. Mensaje de éxito
            flash("¡Registro exitoso! Por favor, ingresa el código que enviamos a tu correo.")
            
            # 2. Redirección DIRECTA a la pantalla de confirmación
            return redirect(url_for('confirm')) 
            
        except Exception as e:
            # Si algo falla (ej. contraseña muy corta), se queda en signup y avisa
            flash(f"Error al registrar: {str(e)}")
            return render_template('signup.html')
            
    return render_template('signup.html')

@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    if request.method == 'POST':
        email = request.form.get('email')
        code = request.form.get('code')
        try:
            # Inicializamos el objeto Cognito
            u = Cognito(USER_POOL_ID, CLIENT_ID, username=email)
            
            # EL CAMBIO ESTÁ AQUÍ: El método correcto en pycognito es confirm_sign_up
            u.confirm_sign_up(code)
            
            flash("¡Cuenta activada con éxito! Ya puedes iniciar sesión.")
            return redirect(url_for('login'))
        except Exception as e:
            # Esto te dirá exactamente qué falló si el código es incorrecto
            print(f"Error detallado: {e}")
            flash(f"Error: {str(e)}")
            
    return render_template('confirm.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username') 
        password = request.form.get('password')
        try:
            u = Cognito(USER_POOL_ID, CLIENT_ID, username=username)
            u.authenticate(password=password)
            session['user'] = username
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash("Credenciales incorrectas o cuenta no confirmada.")
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() # Esto borra al usuario de la memoria del servidor
    flash("Has cerrado sesión correctamente.")
    return redirect(url_for('welcome')) # Te manda de vuelta a la entrada

# --- RUTAS DE LA APLICACIÓN (PROTEGIDAS) ---

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    files = request.files.getlist('file')
    cultivo = request.form.get('cultivo', 'general')
    estado = request.form.get('estado', 'desconocido')
    
    # Extraemos el nombre del usuario para la carpeta en S3 (ej: nando@gmail.com -> nando)
    usuario = session.get('user', 'anonimo').split('@')[0]

    if not files or files[0].filename == '':
        flash("No seleccionaste archivos.")
        return redirect(url_for('dashboard'))

    exitos = 0
    if not os.path.exists('uploads'): os.makedirs('uploads')

    for file in files:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_final = f"img_{timestamp}_{exitos}.jpg"
        ruta_temp = os.path.join("uploads", nombre_final)

        try:
            img = Image.open(file).convert('RGB')
            img.save(ruta_temp, optimize=True, quality=85)

            # RUTA: usuario/cultivo/estado/archivo
            ruta_s3 = f"{usuario}/{cultivo}/{estado}/{nombre_final}"
            
            s3_client.upload_file(ruta_temp, S3_BUCKET, ruta_s3)
            os.remove(ruta_temp)
            exitos += 1
        except Exception as e:
            print(f"Error: {e}")

    return render_template('success.html', cantidad=exitos, ruta=f"{usuario}/{cultivo}/{estado}/")

if __name__ == '__main__':
    if not os.path.exists('uploads'): os.makedirs('uploads')
    app.run(debug=True, host='0.0.0.0', port=5000)