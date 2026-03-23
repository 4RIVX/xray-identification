from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from flask_bcrypt import Bcrypt
from utils.image_processor import save_profile_picture
from bson import ObjectId

profile_bp = Blueprint('profile', __name__)
bcrypt = Bcrypt()

# ─────────────────────────────────────────────
# PROFILE VIEW & EDIT
# ─────────────────────────────────────────────
@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    db = current_app.db

    if request.method == 'POST':
        updates = {
            'name':        request.form.get('name', current_user.name).strip(),
            'designation': request.form.get('designation', '').strip(),
            'hospital':    request.form.get('hospital', '').strip(),
            'phone':       request.form.get('phone', '').strip(),
            'bio':         request.form.get('bio', '').strip(),
        }

        # Profile picture update
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename:
                profile_folder = current_app.config['PROFILE_FOLDER']
                fname, _ = save_profile_picture(file, profile_folder)
                updates['profile_pic'] = fname

        # Password change
        new_password = request.form.get('new_password', '').strip()
        if new_password:
            current_pw = request.form.get('current_password', '')
            user_data  = db.users.find_one({'_id': ObjectId(current_user.id)})
            if bcrypt.check_password_hash(user_data['password'], current_pw):
                updates['password'] = bcrypt.generate_password_hash(new_password).decode('utf-8')
                flash('Password updated successfully.', 'success')
            else:
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('profile.index'))

        db.users.update_one(
            {'_id': ObjectId(current_user.id)},
            {'$set': updates}
        )
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.index'))

    return render_template('profile/index.html')
