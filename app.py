from flask import Flask
from dotenv import load_dotenv
import os

from auth import auth_bp
from main import main_bp

load_dotenv()

app = Flask(__name__)
# Configuración esencial
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'una_clave_muy_secreta_123')

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)