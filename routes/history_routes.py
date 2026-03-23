from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models.scan_model import ScanModel
from config import Config

history_bp = Blueprint('history', __name__)

# ─────────────────────────────────────────────
# HISTORY — ALL SCANS
# ─────────────────────────────────────────────
@history_bp.route('/')
@login_required
def index():
    db      = current_app.db
    query   = request.args.get('q', '').strip()
    disease = request.args.get('disease', '').strip()
    page    = int(request.args.get('page', 1))
    per_page = 10
    skip    = (page - 1) * per_page

    if query:
        scans = ScanModel.search_scans(db, current_user.id, query)
    elif disease:
        scans = ScanModel.filter_by_disease(db, current_user.id, disease)
    else:
        scans = ScanModel.get_user_scans(db, current_user.id, limit=per_page, skip=skip)

    total_scans = db.scans.count_documents({'user_id': current_user.id})
    total_pages = (total_scans + per_page - 1) // per_page

    return render_template('history/index.html',
        scans        = scans,
        query        = query,
        disease      = disease,
        page         = page,
        total_pages  = total_pages,
        class_labels = Config.CLASS_LABELS  # It's already a list!

    )


# ─────────────────────────────────────────────
# DELETE A SCAN
# ─────────────────────────────────────────────
@history_bp.route('/delete/<scan_id>', methods=['POST'])
@login_required
def delete(scan_id):
    db = current_app.db
    ScanModel.delete_scan(db, scan_id, current_user.id)
    flash('Scan record deleted.', 'info')
    return redirect(url_for('history.index'))
