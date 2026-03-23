from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models.user_model import User
from utils.image_processor import save_profile_picture
import os

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        db       = current_app.db

        user_data = db.users.find_one({'email': email})
        if user_data and bcrypt.check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user, remember=True)
            User.update_last_login(db, user.id)
            flash(f'Welcome back, Dr. {user.name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html')


# ─────────────────────────────────────────────
# REGISTER
# ─────────────────────────────────────────────
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        name        = request.form.get('name', '').strip()
        email       = request.form.get('email', '').strip().lower()
        password    = request.form.get('password', '')
        role        = request.form.get('role', 'Radiologist')
        designation = request.form.get('designation', '')
        hospital    = request.form.get('hospital', '')
        phone       = request.form.get('phone', '')
        db          = current_app.db

        if db.users.find_one({'email': email}):
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('auth.login'))

        hashed_pw   = bcrypt.generate_password_hash(password).decode('utf-8')
        profile_pic = 'default.png'

        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename:
                profile_folder = current_app.config['PROFILE_FOLDER']
                fname, _ = save_profile_picture(file, profile_folder)
                profile_pic = fname

        user_doc = User.create_user_document(
            name, email, hashed_pw, role,
            designation, hospital, phone, profile_pic
        )
        db.users.insert_one(user_doc)
        flash('Account created! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


# ─────────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────────
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
