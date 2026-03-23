from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from utils.gradcam import save_gradcam_outputs, generate_colormap_variants, get_gradcam_heatmap
from utils.predictor import get_model
from models.scan_model import ScanModel
import tensorflow as tf
import numpy as np
import os

heatmap_bp = Blueprint('heatmap', __name__)

# ─────────────────────────────────────────────
# GENERATE & VIEW GRAD-CAM HEATMAP
# ─────────────────────────────────────────────
@heatmap_bp.route('/<scan_id>')
@login_required
def index(scan_id):
    db   = current_app.db
    scan = ScanModel.get_scan_by_id(db, scan_id)

    if not scan or scan['user_id'] != current_user.id:
        flash('Scan not found.', 'danger')
        return redirect(url_for('history.index'))

    heatmap_folder  = current_app.config['HEATMAP_FOLDER']
    upload_folder   = current_app.config['UPLOAD_FOLDER']
    original_path   = os.path.join(upload_folder, scan['original_filename'])
    prefix          = scan_id

    # Generate Grad-CAM if not already done
    if not scan['heatmap_paths'].get('overlay'):
        model  = get_model()
        paths, _, _ = save_gradcam_outputs(original_path, model, heatmap_folder, prefix)

        # Generate colormap variants
        img    = tf.keras.preprocessing.image.load_img(original_path, target_size=(224, 224))
        arr    = tf.keras.preprocessing.image.img_to_array(img)
        arr    = np.expand_dims(arr, axis=0) / 255.0
        from utils.gradcam import get_gradcam_heatmap
        heatmap, _, _ = get_gradcam_heatmap(model, arr)
        variants = generate_colormap_variants(original_path, heatmap, heatmap_folder, prefix)
        paths.update(variants)

        ScanModel.update_heatmap_paths(db, scan_id, paths)
        scan = ScanModel.get_scan_by_id(db, scan_id)

    return render_template('heatmap/index.html', scan=scan, scan_id=scan_id)
