from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config
from pymongo import MongoClient
from models.user_model import User
from bson import ObjectId

# ─────────────────────────────────────────────
# APP INITIALIZATION
# ─────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)

# Extensions
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = "Please login to access this page."
login_manager.login_message_category = "warning"

# ─────────────────────────────────────────────
# MONGODB CONNECTION
# ─────────────────────────────────────────────
client = MongoClient(app.config['MONGO_URI'])
db = client[app.config['DB_NAME']]

# Make db accessible everywhere
app.db = db

# ─────────────────────────────────────────────
# USER LOADER FOR FLASK-LOGIN
# ─────────────────────────────────────────────
@login_manager.user_loader
def load_user(user_id):
    user_data = db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

# ─────────────────────────────────────────────
# REGISTER ALL BLUEPRINTS (ROUTES)
# ─────────────────────────────────────────────
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.upload_routes import upload_bp
from routes.heatmap_routes import heatmap_bp
from routes.report_routes import report_bp
from routes.history_routes import history_bp
from routes.profile_routes import profile_bp

app.register_blueprint(auth_bp,      url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(upload_bp,    url_prefix='/upload')
app.register_blueprint(heatmap_bp,   url_prefix='/heatmap')
app.register_blueprint(report_bp,    url_prefix='/report')
app.register_blueprint(history_bp,   url_prefix='/history')
app.register_blueprint(profile_bp,   url_prefix='/profile')

# ─────────────────────────────────────────────
# ROOT ROUTE
# ─────────────────────────────────────────────
@app.route('/')
def index():
    return redirect(url_for('auth.login'))

# ─────────────────────────────────────────────
# CUSTOM ERROR PAGES
# ─────────────────────────────────────────────
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('errors/500.html'), 500

# ─────────────────────────────────────────────
# RUN APP
# ─────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
