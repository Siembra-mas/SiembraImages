from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from pycognito import Cognito
from functools import wraps
import os
import base64
import json
from dotenv import load_dotenv

load_dotenv(override=True)

auth_bp = Blueprint('auth', __name__)

USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
CLIENT_ID = os.getenv('COGNITO_APP_CLIENT_ID') or os.getenv('COGNITO_CLIENT_ID')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            session.clear() 
            flash("Inicia sesión para continuar.")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email') 
        password = request.form.get('password')
        
        if not email or not password:
            flash("Por favor, llena todos los campos.")
            return render_template('login.html')

        try:
            u = Cognito(USER_POOL_ID, CLIENT_ID, username=email)
            u.authenticate(password=password)
            
            # Decodificación manual del JWT para extraer permisos
            payload_b64 = u.id_token.split('.')[1]
            payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
            id_data = json.loads(base64.urlsafe_b64decode(payload_b64).decode('utf-8'))
            
            grupos = id_data.get('cognito:groups', [])
            
            session.clear() 
            session['user'] = email
            session['is_admin'] = 'Admins' in grupos 
            
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            print(f"Error en login: {str(e)}")
            flash("Credenciales incorrectas o cuenta no confirmada.")
            return render_template('login.html')
            
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            u = Cognito(USER_POOL_ID, CLIENT_ID)
            u.register(email, password)
            flash("¡Registro exitoso! Revisa tu código de confirmación.")
            return redirect(url_for('auth.confirm'))
        except Exception as e:
            print(f"Error en signup: {e}")
            flash(f"Error: {str(e)}")
    return render_template('signup.html')

@auth_bp.route('/confirm', methods=['GET', 'POST'])
def confirm():
    if request.method == 'POST':
        email = request.form.get('email')
        code = request.form.get('code')
        try:
            u = Cognito(USER_POOL_ID, CLIENT_ID, username=email)
            u.confirm_sign_up(code)
            flash("Cuenta activada. ¡Inicia sesión!")
            return redirect(url_for('auth.login'))
        except Exception as e:
            print(f"Error en confirmación: {e}")
            flash(f"Error: {str(e)}")
    return render_template('confirm.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada.")
    return redirect(url_for('main.welcome'))