from datetime import datetime
from bson import ObjectId
import uuid


class ReportModel:
    """
    Manages generated PDF report records in MongoDB.
    """

    COLLECTION = 'reports'

    # ─────────────────────────────────────────
    # CREATE REPORT RECORD
    # ─────────────────────────────────────────
    @staticmethod
    def create_report(db, scan_id, user_id, patient_name,
                      predicted_label, confidence,
                      findings, recommendation,
                      report_path, doctor_name):
        """
        Creates a report document linked to a scan.
        Returns report ID.
        """
        report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"

        report_doc = {
            "report_id":        report_id,
            "scan_id":          scan_id,
            "user_id":          user_id,
            "patient_name":     patient_name,
            "predicted_label":  predicted_label,
            "confidence":       confidence,
            "findings":         findings,
            "recommendation":   recommendation,
            "report_path":      report_path,
            "doctor_name":      doctor_name,
            "is_signed":        False,
            "is_urgent":        predicted_label != 'Normal' and confidence > 85,
            "created_at":       datetime.now(),
            "updated_at":       datetime.now()
        }

        result = db[ReportModel.COLLECTION].insert_one(report_doc)
        return str(result.inserted_id), report_id

    # ─────────────────────────────────────────
    # GET REPORT BY SCAN ID
    # ─────────────────────────────────────────
    @staticmethod
    def get_report_by_scan(db, scan_id):
        return db[ReportModel.COLLECTION].find_one({"scan_id": scan_id})

    # ─────────────────────────────────────────
    # GET REPORT BY REPORT ID
    # ─────────────────────────────────────────
    @staticmethod
    def get_report_by_id(db, report_id):
        return db[ReportModel.COLLECTION].find_one({"_id": ObjectId(report_id)})

    # ─────────────────────────────────────────
    # GET ALL REPORTS FOR USER
    # ─────────────────────────────────────────
    @staticmethod
    def get_user_reports(db, user_id, limit=50):
        return list(db[ReportModel.COLLECTION].find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(limit))

    # ─────────────────────────────────────────
    # MARK REPORT AS SIGNED
    # ─────────────────────────────────────────
    @staticmethod
    def sign_report(db, report_id):
        db[ReportModel.COLLECTION].update_one(
            {"_id": ObjectId(report_id)},
            {"$set": {
                "is_signed":  True,
                "signed_at":  datetime.now(),
                "updated_at": datetime.now()
            }}
        )

    # ─────────────────────────────────────────
    # UPDATE FINDINGS
    # ─────────────────────────────────────────
    @staticmethod
    def update_findings(db, report_id, findings, recommendation):
        db[ReportModel.COLLECTION].update_one(
            {"_id": ObjectId(report_id)},
            {"$set": {
                "findings":       findings,
                "recommendation": recommendation,
                "updated_at":     datetime.now()
            }}
        )

    # ─────────────────────────────────────────
    # DELETE REPORT
    # ─────────────────────────────────────────
    @staticmethod
    def delete_report(db, report_id):
        db[ReportModel.COLLECTION].delete_one({"_id": ObjectId(report_id)})

    # ─────────────────────────────────────────
    # REPORT STATISTICS
    # ─────────────────────────────────────────
    @staticmethod
    def get_report_stats(db, user_id):
        total        = db[ReportModel.COLLECTION].count_documents({"user_id": user_id})
        signed       = db[ReportModel.COLLECTION].count_documents({"user_id": user_id, "is_signed": True})
        urgent       = db[ReportModel.COLLECTION].count_documents({"user_id": user_id, "is_urgent": True})
        return {
            "total_reports":  total,
            "signed_reports": signed,
            "urgent_reports": urgent,
            "pending_sign":   total - signed
        }
