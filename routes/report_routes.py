from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, current_app, send_file)
from flask_login import login_required, current_user
from utils.pdf_report import generate_pdf_report
from models.scan_model import ScanModel
from models.report_model import ReportModel
from config import Config
import os
from datetime import datetime

report_bp = Blueprint('report', __name__)


# ─────────────────────────────────────────────
# REPORT EDITOR PAGE (GET) + GENERATE PDF (POST)
# ─────────────────────────────────────────────
@report_bp.route('/<scan_id>', methods=['GET', 'POST'])
@login_required
def index(scan_id):
    db   = current_app.db
    scan = ScanModel.get_scan_by_id(db, scan_id)

    if not scan or scan['user_id'] != current_user.id:
        flash('Scan not found or access denied.', 'danger')
        return redirect(url_for('history.index'))

    existing_report = ReportModel.get_report_by_scan(db, scan_id)

    if request.method == 'POST':
        findings       = request.form.get('findings', '').strip()
        recommendation = request.form.get('recommendation', '').strip()

        report_folder   = current_app.config['REPORT_FOLDER']
        os.makedirs(report_folder, exist_ok=True)

        report_filename = f"report_{scan_id}.pdf"
        report_path     = os.path.join(report_folder, report_filename)

        # ── Build heatmap image paths ──────────
        heatmap_paths = scan.get('heatmap_paths', {}) or {}
        upload_folder = current_app.config['UPLOAD_FOLDER']

        original_img = heatmap_paths.get('original') or \
                       os.path.join(upload_folder, scan.get('original_filename', ''))
        heatmap_img  = heatmap_paths.get('heatmap', '')
        overlay_img  = heatmap_paths.get('overlay', '')

        # ── Assemble report data dict ──────────
        report_data = {
            'patient_name':      scan.get('patient_name',   'N/A'),
            'patient_age':       scan.get('patient_age',    'N/A'),
            'patient_gender':    scan.get('patient_gender', 'N/A'),
            'patient_id':        scan.get('patient_id',     'N/A'),
            'doctor_name':       current_user.name,
            'doctor_designation':current_user.designation or 'Radiologist',
            'scan_date':         scan['created_at'].strftime('%d %b %Y'),
            'scan_id':           scan_id,
            'predicted_label':   scan.get('predicted_label', 'Unknown'),
            'confidence':        scan.get('confidence', 0),
            'all_scores':        scan.get('all_scores', []),
            'original_img_path': original_img,
            'heatmap_img_path':  heatmap_img,
            'overlay_img_path':  overlay_img,
            'findings':          findings,
            'recommendation':    recommendation,
            'hospital_name':     Config.HOSPITAL_NAME,
            'hospital_subtitle': Config.HOSPITAL_SUBTITLE,
        }

        # ── Generate PDF via ReportLab ─────────
        try:
            generate_pdf_report(report_data, report_path)
        except Exception as e:
            flash(f'PDF generation failed: {str(e)}', 'danger')
            return redirect(url_for('report.index', scan_id=scan_id))

        # ── Save report path + findings to scan ─
        ScanModel.update_report_path(
            db, scan_id, report_path, findings, recommendation
        )

        # ── Create or update report record ──────
        if existing_report:
            ReportModel.update_findings(
                db, str(existing_report['_id']), findings, recommendation
            )
        else:
            ReportModel.create_report(
                db          = db,
                scan_id     = scan_id,
                user_id     = current_user.id,
                patient_name= scan.get('patient_name', 'N/A'),
                predicted_label = scan.get('predicted_label', 'Unknown'),
                confidence   = scan.get('confidence', 0),
                findings     = findings,
                recommendation = recommendation,
                report_path  = report_path,
                doctor_name  = current_user.name
            )

        flash('✅ PDF Report generated successfully!', 'success')
        return redirect(url_for('report.index', scan_id=scan_id))

    # ── GET: Reload scan + report fresh ────────
    scan            = ScanModel.get_scan_by_id(db, scan_id)
    existing_report = ReportModel.get_report_by_scan(db, scan_id)

    return render_template('report/index.html',
        scan            = scan,
        scan_id         = scan_id,
        existing_report = existing_report
    )


# ─────────────────────────────────────────────
# DOWNLOAD PDF (send_file)
# ─────────────────────────────────────────────
@report_bp.route('/download/<scan_id>')
@login_required
def download(scan_id):
    db   = current_app.db
    scan = ScanModel.get_scan_by_id(db, scan_id)

    if not scan or scan['user_id'] != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('history.index'))

    report_path = scan.get('report_path')

    if not report_path or not os.path.exists(report_path):
        flash('Report not generated yet. Please generate it first.', 'warning')
        return redirect(url_for('report.index', scan_id=scan_id))

    safe_name = scan.get('patient_name', 'Patient').replace(' ', '_')
    filename  = f"ChestXRay_Report_{safe_name}_{scan_id[:6]}.pdf"

    return send_file(
        report_path,
        as_attachment = True,
        download_name = filename,
        mimetype      = 'application/pdf'
    )


# ─────────────────────────────────────────────
# BROWSER PRINT / PDF TEMPLATE VIEW
# ─────────────────────────────────────────────
@report_bp.route('/view/<scan_id>')
@login_required
def view_pdf(scan_id):
    db   = current_app.db
    scan = ScanModel.get_scan_by_id(db, scan_id)

    if not scan or scan['user_id'] != current_user.id:
        flash('Scan not found.', 'danger')
        return redirect(url_for('history.index'))

    existing_report = ReportModel.get_report_by_scan(db, scan_id)

    return render_template('report/pdf_template.html',
        scan            = scan,
        scan_id         = scan_id,
        existing_report = existing_report,
        config          = Config
    )


# ─────────────────────────────────────────────
# SIGN REPORT
# ─────────────────────────────────────────────
@report_bp.route('/sign/<report_id>', methods=['POST'])
@login_required
def sign(report_id):
    db = current_app.db

    report = ReportModel.get_report_by_id(db, report_id)

    if not report or report['user_id'] != current_user.id:
        flash('Report not found or access denied.', 'danger')
        return redirect(url_for('history.index'))

    ReportModel.sign_report(db, report_id)
    flash('✅ Report signed successfully.', 'success')

    scan_id = report.get('scan_id')
    if scan_id:
        return redirect(url_for('report.index', scan_id=scan_id))
    return redirect(url_for('history.index'))


# ─────────────────────────────────────────────
# DELETE REPORT
# ─────────────────────────────────────────────
@report_bp.route('/delete/<report_id>', methods=['POST'])
@login_required
def delete_report(report_id):
    db     = current_app.db
    report = ReportModel.get_report_by_id(db, report_id)

    if not report or report['user_id'] != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('history.index'))

    # Delete PDF file from disk
    report_path = report.get('report_path')
    if report_path and os.path.exists(report_path):
        try:
            os.remove(report_path)
        except Exception:
            pass

    ReportModel.delete_report(db, report_id)
    flash('Report deleted.', 'info')
    return redirect(url_for('history.index'))
