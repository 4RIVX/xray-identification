from flask import Blueprint, render_template, request, redirect, flash, current_app
from flask_login import login_required, current_user
from utils.image_processor import allowed_file, save_uploaded_file, enhance_xray, is_valid_xray
from utils.predictor import predict_xray
from models.scan_model import ScanModel
from models.user_model import User
import os

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():

    if request.method == 'POST':

        db = current_app.db

        patient_name = request.form.get('patient_name', 'Unknown')
        patient_age = request.form.get('patient_age', 'N/A')
        patient_gender = request.form.get('patient_gender', 'N/A')
        patient_id = request.form.get('patient_id', 'N/A')

        # check file exists
        if 'xray_file' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(request.url)

        file = request.files['xray_file']

        # check valid filename
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('Invalid file type. Upload PNG, JPG, JPEG or WEBP.', 'danger')
            return redirect(request.url)

        # save uploaded file
        upload_folder = current_app.config['UPLOAD_FOLDER']
        fname, fpath = save_uploaded_file(file, upload_folder)

        # validate xray
        if not is_valid_xray(fpath):
            os.remove(fpath)
            flash('Uploaded image does not appear to be a chest X-ray.', 'warning')
            return redirect(request.url)

        # enhance image for display
        enhanced_path = fpath.replace(fname, f'enhanced_{fname}')
        enhance_xray(fpath, enhanced_path)

        # AI prediction
        result = predict_xray(fpath)

        # save to database
        scan_id = ScanModel.create_scan(
            db,
            current_user.id,
            patient_name,
            patient_age,
            patient_gender,
            patient_id,
            fname,
            result['predicted_label'],
            result['confidence'],
            result['all_scores']
        )

        User.increment_scan_count(db, current_user.id)

        flash('Scan analysed successfully!', 'success')

        return render_template(
            'upload/index.html',
            result=result,
            scan_id=scan_id,
            patient_name=patient_name,
            patient_age=patient_age,
            patient_gender=patient_gender,
            patient_id=patient_id,
            img_filename=fname
        )

    return render_template('upload/index.html', result=None)