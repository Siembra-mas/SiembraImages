import os
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
from datetime import datetime
from PIL import Image # Asegúrate de tener instalado: pip install pillow

app = Flask(__name__)

# Configuración básica
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024 # Límite de 20MB
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- PASO 1: DEFINIR LA FUNCIÓN (Primero se define) ---
def procesar_y_guardar_imagen(file_storage, path_destino):
    """
    Toma la foto, la encoge si es muy grande y la guarda como JPEG.
    """
    img = Image.open(file_storage)
    
    # Convertir a RGB (evita errores con PNGs transparentes)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Redimensionar si pasa de 1600px
    max_width = 1600
    if img.width > max_width:
        ratio = max_width / float(img.width)
        new_height = int(float(img.height) * float(ratio))
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

    # Guardar optimizado
    img.save(path_destino, "JPEG", optimize=True, quality=85)

# --- PASO 2: LAS RUTAS (Aquí se usa la función) ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    cultivo = request.form.get('cultivo')
    enfermedad = request.form.get('enfermedad')
    file = request.files.get('file')

    if file and cultivo and enfermedad:
        # Crear ruta de carpetas
        path_carpetas = os.path.join(app.config['UPLOAD_FOLDER'], cultivo, enfermedad)
        os.makedirs(path_carpetas, exist_ok=True)

        # Nombre final
        filename = secure_filename(file.filename).rsplit('.', 1)[0] + ".jpg"
        final_path = os.path.join(path_carpetas, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}")

        try:
            # Llamada a la función
            procesar_y_guardar_imagen(file, final_path)
            return render_template('success.html')
        except Exception as e:
            print(f"Error al guardar: {e}")
            return f"Error al procesar la imagen: {e}", 500
    
    return "Faltan datos", 400

if __name__ == '__main__':
    # host='0.0.0.0' le dice a Flask que escuche a cualquier dispositivo en la red
    app.run(debug=True, host='0.0.0.0', port=5000)