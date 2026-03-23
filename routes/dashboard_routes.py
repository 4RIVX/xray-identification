from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from models.scan_model import ScanModel
from models.report_model import ReportModel

dashboard_bp = Blueprint('dashboard', __name__)

# ─────────────────────────────────────────────
# DASHBOARD HOME
# ─────────────────────────────────────────────
@dashboard_bp.route('/')
@login_required
def index():
    db           = current_app.db
    stats        = ScanModel.get_dashboard_stats(db, current_user.id)
    recent_scans = ScanModel.get_recent_scans(db, current_user.id, limit=5)
    report_stats = ReportModel.get_report_stats(db, current_user.id)

    # Prepare Chart.js data
    disease_labels  = [d['_id'] for d in stats['disease_stats']]
    disease_counts  = [d['count'] for d in stats['disease_stats']]
    disease_colors  = {
        'Covid-19':            '#e74c3c',
        'Emphysema':           '#e67e22',
        'Normal':              '#2ecc71',
        'Pneumonia-Bacterial': '#9b59b6',
        'Pneumonia-Viral':     '#3498db',
        'Tuberculosis':        '#c0392b'
    }
    chart_colors = [disease_colors.get(l, '#aaaaaa') for l in disease_labels]

    return render_template('dashboard/index.html',
        stats         = stats,
        recent_scans  = recent_scans,
        report_stats  = report_stats,
        disease_labels= disease_labels,
        disease_counts= disease_counts,
        chart_colors  = chart_colors
    )
