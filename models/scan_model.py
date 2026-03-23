from datetime import datetime
from bson import ObjectId


class ScanModel:
    """
    Manages all chest X-ray scan records in MongoDB.
    """

    COLLECTION = 'scans'

    # ─────────────────────────────────────────
    # CREATE NEW SCAN RECORD
    # ─────────────────────────────────────────
    @staticmethod
    def create_scan(db, user_id, patient_name, patient_age,
                    patient_gender, patient_id,
                    original_filename, predicted_label,
                    confidence, all_scores):
        """
        Inserts a new scan document into MongoDB.
        Returns the inserted scan ID.
        """
        scan_doc = {
            "user_id":           user_id,
            "patient_name":      patient_name,
            "patient_age":       patient_age,
            "patient_gender":    patient_gender,
            "patient_id":        patient_id,
            "original_filename": original_filename,
            "predicted_label":   predicted_label,
            "confidence":        confidence,
            "all_scores":        all_scores,
            "heatmap_paths": {
                "original":     None,
                "heatmap":      None,
                "overlay":      None,
                "side_by_side": None,
                "jet":          None,
                "hot":          None,
                "turbo":        None
            },
            "report_path":       None,
            "findings":          "",
            "recommendation":    "",
            "status":            "pending",   # pending | reviewed | reported
            "is_urgent":         confidence > 85 and predicted_label != 'Normal',
            "created_at":        datetime.now(),
            "updated_at":        datetime.now()
        }
        result = db[ScanModel.COLLECTION].insert_one(scan_doc)
        return str(result.inserted_id)

    # ─────────────────────────────────────────
    # GET SCAN BY ID
    # ─────────────────────────────────────────
    @staticmethod
    def get_scan_by_id(db, scan_id):
        return db[ScanModel.COLLECTION].find_one({"_id": ObjectId(scan_id)})

    # ─────────────────────────────────────────
    # GET ALL SCANS FOR A USER
    # ─────────────────────────────────────────
    @staticmethod
    def get_user_scans(db, user_id, limit=50, skip=0):
        return list(db[ScanModel.COLLECTION].find(
            {"user_id": user_id}
        ).sort("created_at", -1).skip(skip).limit(limit))

    # ─────────────────────────────────────────
    # GET RECENT SCANS (for dashboard)
    # ─────────────────────────────────────────
    @staticmethod
    def get_recent_scans(db, user_id, limit=5):
        return list(db[ScanModel.COLLECTION].find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(limit))

    # ─────────────────────────────────────────
    # UPDATE HEATMAP PATHS AFTER GRAD-CAM
    # ─────────────────────────────────────────
    @staticmethod
    def update_heatmap_paths(db, scan_id, heatmap_paths):
        db[ScanModel.COLLECTION].update_one(
            {"_id": ObjectId(scan_id)},
            {"$set": {
                "heatmap_paths": heatmap_paths,
                "updated_at":    datetime.now()
            }}
        )

    # ─────────────────────────────────────────
    # UPDATE REPORT PATH
    # ─────────────────────────────────────────
    @staticmethod
    def update_report_path(db, scan_id, report_path, findings, recommendation):
        db[ScanModel.COLLECTION].update_one(
            {"_id": ObjectId(scan_id)},
            {"$set": {
                "report_path":    report_path,
                "findings":       findings,
                "recommendation": recommendation,
                "status":         "reported",
                "updated_at":     datetime.now()
            }}
        )

    # ─────────────────────────────────────────
    # SEARCH SCANS BY PATIENT NAME OR DISEASE
    # ─────────────────────────────────────────
    @staticmethod
    def search_scans(db, user_id, query):
        return list(db[ScanModel.COLLECTION].find({
            "user_id": user_id,
            "$or": [
                {"patient_name":    {"$regex": query, "$options": "i"}},
                {"predicted_label": {"$regex": query, "$options": "i"}},
                {"patient_id":      {"$regex": query, "$options": "i"}}
            ]
        }).sort("created_at", -1))

    # ─────────────────────────────────────────
    # FILTER BY DISEASE CLASS
    # ─────────────────────────────────────────
    @staticmethod
    def filter_by_disease(db, user_id, disease):
        return list(db[ScanModel.COLLECTION].find({
            "user_id":         user_id,
            "predicted_label": disease
        }).sort("created_at", -1))

    # ─────────────────────────────────────────
    # DASHBOARD STATISTICS
    # ─────────────────────────────────────────
    @staticmethod
    def get_dashboard_stats(db, user_id):
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id":          "$predicted_label",
                "count":        {"$sum": 1},
                "avg_conf":     {"$avg": "$confidence"}
            }},
            {"$sort": {"count": -1}}
        ]
        disease_stats = list(db[ScanModel.COLLECTION].aggregate(pipeline))

        total_scans  = db[ScanModel.COLLECTION].count_documents({"user_id": user_id})
        total_urgent = db[ScanModel.COLLECTION].count_documents({
            "user_id":   user_id,
            "is_urgent": True
        })
        total_normal = db[ScanModel.COLLECTION].count_documents({
            "user_id":         user_id,
            "predicted_label": "Normal"
        })
        total_reported = db[ScanModel.COLLECTION].count_documents({
            "user_id": user_id,
            "status":  "reported"
        })

        return {
            "total_scans":    total_scans,
            "total_urgent":   total_urgent,
            "total_normal":   total_normal,
            "total_reported": total_reported,
            "disease_stats":  disease_stats
        }

    # ─────────────────────────────────────────
    # DELETE SCAN RECORD
    # ─────────────────────────────────────────
    @staticmethod
    def delete_scan(db, scan_id, user_id):
        db[ScanModel.COLLECTION].delete_one({
            "_id":     ObjectId(scan_id),
            "user_id": user_id
        })

    # ─────────────────────────────────────────
    # UPDATE SCAN STATUS
    # ─────────────────────────────────────────
    @staticmethod
    def update_status(db, scan_id, status):
        db[ScanModel.COLLECTION].update_one(
            {"_id": ObjectId(scan_id)},
            {"$set": {
                "status":     status,
                "updated_at": datetime.now()
            }}
        )
