from flask_login import UserMixin
from bson import ObjectId
from datetime import datetime

class User(UserMixin):
    """
    Flask-Login compatible User class wrapping MongoDB document.
    """
    def __init__(self, user_data):
        self.id            = str(user_data['_id'])
        self.name          = user_data.get('name', '')
        self.email         = user_data.get('email', '')
        self.password      = user_data.get('password', '')
        self.role          = user_data.get('role', 'Radiologist')
        self.profile_pic   = user_data.get('profile_pic', 'default.png')
        self.designation   = user_data.get('designation', '')
        self.hospital      = user_data.get('hospital', '')
        self.phone         = user_data.get('phone', '')
        self.bio           = user_data.get('bio', '')
        self.created_at    = user_data.get('created_at', datetime.now())
        self.total_scans   = user_data.get('total_scans', 0)
        self.is_verified   = user_data.get('is_verified', False)

    def get_id(self):
        return self.id

    @staticmethod
    def create_user_document(name, email, hashed_password, role,
                              designation='', hospital='', phone='',
                              profile_pic='default.png'):
        """
        Returns a clean MongoDB document dict for inserting a new user.
        """
        return {
            "name":          name,
            "email":         email.lower().strip(),
            "password":      hashed_password,
            "role":          role,
            "designation":   designation,
            "hospital":      hospital,
            "phone":         phone,
            "bio":           '',
            "profile_pic":   profile_pic,
            "total_scans":   0,
            "is_verified":   False,
            "created_at":    datetime.now(),
            "last_login":    datetime.now(),
            "preferences": {
                "theme":          "dark",
                "notifications":  True,
                "report_footer":  True
            }
        }

    @staticmethod
    def update_last_login(db, user_id):
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_login": datetime.now()}}
        )

    @staticmethod
    def increment_scan_count(db, user_id):
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$inc": {"total_scans": 1}}
        )

    @staticmethod
    def get_all_users(db):
        return list(db.users.find({}, {"password": 0}))

    def to_dict(self):
        return {
            "id":           self.id,
            "name":         self.name,
            "email":        self.email,
            "role":         self.role,
            "designation":  self.designation,
            "hospital":     self.hospital,
            "phone":        self.phone,
            "bio":          self.bio,
            "profile_pic":  self.profile_pic,
            "total_scans":  self.total_scans,
            "created_at":   self.created_at,
            "is_verified":  self.is_verified
        }
