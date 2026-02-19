from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from pycognito import Cognito
from functools import wraps
import os

auth_bp = Blueprint('auth', __name__)

USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')

# Decorador para proteger rutas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("Inicia sesión para continuar.")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Cambié 'username' por 'email' para que coincida con tu signup
        email = request.form.get('email') 
        password = request.form.get('password')
        try:
            u = Cognito(USER_POOL_ID, CLIENT_ID, username=email)
            u.authenticate(password=password)
            session['user'] = email
            return redirect(url_for('main.dashboard')) # <--- Nota el 'main.'
        except Exception as e:
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
            flash("¡Registro exitoso! Revisa tu código.")
            return redirect(url_for('auth.confirm')) # <--- Nota el 'auth.'
        except Exception as e:
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
            flash(f"Error: {str(e)}")
    return render_template('confirm.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada.")
    return redirect(url_for('main.welcome'))