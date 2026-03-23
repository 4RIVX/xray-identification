import os

class Config:
    BASE_DIR   = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = 'jrs-xray-secret-2026'

    # MongoDB
    MONGO_URI = 'mongodb://localhost:27017/'
    DB_NAME   = 'chest_xray_db'

    # Model ✅ FIXED
    MODEL_PATH = os.path.join(BASE_DIR, 'ml_model', 'model_converted.h5')

    # Folders ✅
    UPLOAD_FOLDER      = os.path.join(BASE_DIR, 'static', 'uploads', 'xrays')
    HEATMAP_FOLDER     = os.path.join(BASE_DIR, 'static', 'uploads', 'heatmaps')
    REPORT_FOLDER      = os.path.join(BASE_DIR, 'static', 'uploads', 'reports')
    PROFILE_FOLDER     = os.path.join(BASE_DIR, 'static', 'uploads', 'profiles')
    BACKGROUND_FOLDER  = os.path.join(BASE_DIR, 'static', 'uploads', 'backgrounds')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # Flask Requirements ✅ ALL FIXED
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp'}
    WTF_CSRF_ENABLED   = True

    # JRS Eduzone Branding ✅ HOSPITAL_SUBTITLE ADDED
    HOSPITAL_NAME      = 'JRS Eduzone Radiology AI Centre'
    HOSPITAL_SUBTITLE  = 'Advanced Chest X-Ray Diagnostic System Powered by DenseNet121'
    URGENT_THRESHOLD   = 70.0

    # Chest X-ray Classes ✅ 6 classes
    CLASS_LABELS = [
        'Normal',
        'Pneumonia',
        'Tuberculosis',
        'COVID-19',
        'Cardiomegaly',
        'Pleural Effusion'
    ]

    CLASS_COLORS = {
        'Normal':           '#2ecc71',
        'Pneumonia':        '#e74c3c',
        'Tuberculosis':     '#e67e22',
        'COVID-19':         '#9b59b6',
        'Cardiomegaly':     '#3498db',
        'Pleural Effusion': '#1abc9c'
    }
