<div align="center">

<img src="https://img.shields.io/badge/AI%20Powered-DenseNet121-blueviolet?style=for-the-badge&logo=tensorflow&logoColor=white"/>
<img src="https://img.shields.io/badge/Flask-3.x-black?style=for-the-badge&logo=flask&logoColor=white"/>
<img src="https://img.shields.io/badge/MongoDB-Atlas-47A248?style=for-the-badge&logo=mongodb&logoColor=white"/>
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/TensorFlow-2.x-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white"/>

#  Chest X-Ray AI Diagnosis System
### *JRS Eduzone Radiology AI Centre — Advanced Diagnostic Platform*

> A full-stack clinical AI web application that classifies chest X-ray images into **6 disease categories** using a **DenseNet121** deep learning model, complete with **Grad-CAM heatmap visualization**, **automated PDF report generation**, and a **secure multi-user doctor portal**.

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Disease Classification](#-disease-classification)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [How It Works](#-how-it-works)
- [Grad-CAM Visualization](#-grad-cam-visualization)
- [PDF Report Generation](#-pdf-report-generation)
- [Database Schema](#-database-schema)
- [API Routes](#-api-routes)
- [Screenshots Preview](#-screenshots-preview)
- [Configuration](#-configuration)
- [Future Enhancements](#-future-enhancements)
- [Author](#-author)

---

## 🧠 Overview

The **Chest X-Ray AI Diagnosis System** is a clinical-grade AI-powered radiology platform built for radiologists and doctors to analyze chest X-ray scans with speed and precision. Doctors upload a patient's X-ray image, and the system instantly:

1. **Validates** whether the image is a real chest X-ray using pixel-level grayscale analysis
2. **Enhances** the image using contrast and sharpness boosting via Pillow
3. **Predicts** the disease class using a fine-tuned DenseNet121 model
4. **Visualizes** model attention regions using Grad-CAM in 3 colormap styles
5. **Generates** a downloadable clinical PDF report with findings and doctor recommendations

All data is stored in **MongoDB**, with a complete per-doctor scan history, dashboard statistics, and patient management system.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔐 **Secure Authentication** | Doctor login/register with bcrypt password hashing and Flask-Login session management |
| 📤 **Smart X-Ray Upload** | File validation, X-ray authenticity check, UUID-based storage, and auto image enhancement |
| 🤖 **AI Diagnosis Engine** | DenseNet121 model predicts across 6 chest disease classes with confidence scores |
| 🌡️ **Grad-CAM Heatmaps** | 3 colormap variants (JET, HOT, TURBO) show exactly where the AI is "looking" |
| 📋 **Clinical PDF Reports** | Auto-generated professional reports with X-ray images, heatmaps, findings, and doctor signature |
| 📊 **Analytics Dashboard** | Per-doctor statistics — total scans, urgent cases, disease distribution charts |
| 🗂️ **Scan History** | Full history with search by patient name/ID/disease and filter by disease class |
| 👤 **Doctor Profile** | Profile picture upload, designation, and account settings |
| ⚠️ **Urgent Flagging** | Auto-flags scans as urgent when confidence > 85% for non-Normal predictions |
| 📱 **Responsive UI** | Clean, hospital-grade UI with dedicated CSS per module |

---

## 🦠 Disease Classification

The DenseNet121 model classifies chest X-rays into **6 categories**:

| # | Disease | Color Code | Description |
|---|---|---|---|
| 1 | ✅ Normal | `#2ecc71` (Green) | Healthy lung X-ray |
| 2 | 🔴 Pneumonia | `#e74c3c` (Red) | Bacterial/viral lung infection |
| 3 | 🟠 Tuberculosis | `#e67e22` (Orange) | Mycobacterium TB infection |
| 4 | 🟣 COVID-19 | `#9b59b6` (Purple) | SARS-CoV-2 lung manifestation |
| 5 | 🔵 Cardiomegaly | `#3498db` (Blue) | Enlarged heart shadow |
| 6 | 🟢 Pleural Effusion | `#1abc9c` (Teal) | Fluid buildup around lungs |

> **Urgent Threshold:** Any non-Normal prediction with confidence > **85%** is automatically flagged as an urgent case on the dashboard.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DOCTOR (Web Browser)                         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP
┌──────────────────────────────▼──────────────────────────────────────┐
│                         Flask Web Server                             │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │  /auth   │  │ /upload  │  │ /heatmap │  │    /report       │   │
│  │  Routes  │  │  Routes  │  │  Routes  │  │    Routes        │   │
│  └──────────┘  └────┬─────┘  └────┬─────┘  └────────┬─────────┘   │
│                     │              │                  │              │
│         ┌───────────▼──────────────▼──────────────────▼──────────┐ │
│         │                 Core Utilities Layer                    │ │
│         │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │ │
│         │  │  predictor   │  │   gradcam    │  │  pdf_report  │ │ │
│         │  │  (DenseNet)  │  │  (Grad-CAM)  │  │  (ReportLab) │ │ │
│         │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │ │
│         └─────────┼─────────────────┼─────────────────┼─────────┘ │
│                   │                 │                  │            │
│         ┌─────────▼─────────────────▼─────────────────▼─────────┐ │
│         │                   DenseNet121 Model                    │ │
│         │              (model_converted.h5 — ~32MB)              │ │
│         └─────────────────────────────────────────────────────── ┘ │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                         MongoDB Database                             │
│         Collections: users │ scans │ reports                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

**Backend**
- **Python 3.11** — Core language
- **Flask** — Web framework with Blueprint-based modular routing
- **TensorFlow / Keras** — DenseNet121 model loading and inference
- **OpenCV (cv2)** — Grad-CAM heatmap computation and colormap rendering
- **Pillow (PIL)** — Image enhancement, validation, profile picture processing
- **ReportLab** — Clinical PDF report generation
- **PyMongo** — MongoDB driver for all database operations
- **Flask-Login** — Session-based authentication
- **Flask-Bcrypt** — Secure password hashing
- **Gunicorn** — Production WSGI server

**Frontend**
- **Jinja2 Templates** — Server-side HTML rendering
- **Vanilla CSS** — Module-specific stylesheets (login, dashboard, upload, report, heatmap, etc.)
- **Vanilla JS** — Client-side interactivity (dashboard charts, profile updates, report editor)

**Database**
- **MongoDB** — NoSQL document store (users, scans, reports)

**AI Model**
- **DenseNet121** — Pre-trained on ImageNet, fine-tuned on chest X-ray dataset
- **Grad-CAM** — Gradient-weighted Class Activation Mapping for explainability

---

## 📁 Project Structure

```
xray-identification-main/
│
├── app.py                      # Flask app factory — registers all blueprints
├── config.py                   # All config: paths, DB, labels, colors, thresholds
├── requirements.txt            # Python dependencies
├── convert_model.py            # Utility to convert .keras → .h5 format
│
├── ml_model/
│   ├── chest_xray_densenet_model.keras   # Original Keras model
│   └── model_converted.h5               # Production-ready H5 model (~32MB)
│
├── models/                     # MongoDB data models (ORM-style static methods)
│   ├── user_model.py           # User registration, login, profile, scan count
│   ├── scan_model.py           # Scan CRUD, statistics, search, filter
│   └── report_model.py        # Report creation, signing, update, stats
│
├── routes/                     # Flask Blueprints (one per feature)
│   ├── auth_routes.py          # /auth — login, register, logout
│   ├── dashboard_routes.py     # /dashboard — stats, recent scans
│   ├── upload_routes.py        # /upload — X-ray upload + AI prediction
│   ├── heatmap_routes.py       # /heatmap — Grad-CAM visualization
│   ├── report_routes.py        # /report — editor + PDF generation + download
│   ├── history_routes.py       # /history — scan history, search, filter
│   └── profile_routes.py      # /profile — doctor profile + photo upload
│
├── utils/                      # Core utility layer
│   ├── predictor.py            # DenseNet121 inference engine (model caching)
│   ├── gradcam.py              # Full Grad-CAM pipeline + colormap variants
│   ├── image_processor.py      # Upload handling, enhancement, X-ray validation
│   └── pdf_report.py          # ReportLab PDF builder
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Base layout with navbar/sidebar
│   ├── auth/                   # login.html, register.html
│   ├── dashboard/              # index.html — stats + charts
│   ├── upload/                 # index.html — upload form + prediction result
│   ├── heatmap/                # index.html — JET / HOT / TURBO colormap viewer
│   ├── report/                 # index.html + pdf_template.html
│   ├── history/                # index.html — paginated scan list
│   ├── profile/                # index.html — doctor profile editor
│   └── errors/                 # 404.html, 500.html
│
└── static/
    ├── css/                    # Module-specific stylesheets
    ├── js/                     # Module-specific JavaScript
    └── uploads/
        ├── xrays/              # Original + enhanced X-ray images
        ├── heatmaps/           # Grad-CAM output images (7 variants per scan)
        ├── reports/            # Generated PDF reports
        └── profiles/           # Doctor profile pictures
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- MongoDB running locally on port `27017`
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/xray-identification.git
cd xray-identification
```

### 2. Create and Activate Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify MongoDB is Running

```bash
# Start MongoDB service (if not already running)
mongod --dbpath /data/db

# Or on Windows
net start MongoDB
```

### 5. Add Your Model

Ensure the DenseNet121 model file exists at:
```
ml_model/model_converted.h5
```

> If you have the `.keras` format, run:
> ```bash
> python convert_model.py
> ```

### 6. Run the Application

```bash
python app.py
```

Visit **http://localhost:5000** in your browser.

### 7. Production Deployment (Gunicorn)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## ⚙️ Configuration

All configuration lives in `config.py`:

```python
# Key Settings
SECRET_KEY       = 'your-secret-key-here'
MONGO_URI        = 'mongodb://localhost:27017/'
DB_NAME          = 'chest_xray_db'
MODEL_PATH       = 'ml_model/model_converted.h5'
URGENT_THRESHOLD = 70.0   # % confidence to flag as urgent
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload

# Hospital Branding
HOSPITAL_NAME    = 'JRS Eduzone Radiology AI Centre'
HOSPITAL_SUBTITLE = 'Advanced Chest X-Ray Diagnostic System Powered by DenseNet121'

# Supported File Types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp'}
```

---

## 🔄 How It Works

### Complete Scan Workflow

```
Doctor Uploads X-Ray
        │
        ▼
File Validation (extension check)
        │
        ▼
X-Ray Authenticity Check
(pixel grayscale ratio analysis)
        │
        ▼
Image Enhancement
(contrast ×1.4, sharpness ×1.3, edge enhance)
        │
        ▼
DenseNet121 Inference
(224×224 input → 6-class softmax output)
        │
        ▼
Prediction Result Stored in MongoDB
(patient info + confidence scores + all_scores array)
        │
        ▼
Doctor Requests Grad-CAM  ──→  Heatmap saved (7 variants)
        │
        ▼
Doctor Writes Findings + Recommendation
        │
        ▼
PDF Report Generated (ReportLab)
        │
        ▼
Report Stored in MongoDB + Available for Download
```

---

## 🌡️ Grad-CAM Visualization

Grad-CAM (Gradient-weighted Class Activation Mapping) produces visual explanations of the AI's predictions by highlighting the lung regions that most influenced the classification decision.

**Saved Outputs per Scan (7 images):**

| File | Description |
|---|---|
| `{id}_original.jpg` | Clean resized X-ray (224×224) |
| `{id}_heatmap.jpg` | Raw activation heatmap |
| `{id}_overlay.jpg` | Heatmap blended over X-ray (JET, 45% alpha) |
| `{id}_jet.jpg` | JET colormap variant overlay |
| `{id}_hot.jpg` | HOT colormap variant overlay |
| `{id}_turbo.jpg` | TURBO colormap variant overlay |
| `{id}_comparison.jpg` | Side-by-side: Original │ Heatmap │ Overlay |

**Implementation:**
- Taps into the `relu` layer of DenseNet121 (last convolutional block)
- Computes gradients of the predicted class w.r.t. convolution output
- Pools gradients over spatial dimensions (Global Average Pooling)
- Weights feature maps by gradient importance
- Normalizes and overlays using OpenCV `addWeighted()`

---

## 📋 PDF Report Generation

The system generates a fully structured clinical PDF report using **ReportLab**, containing:

- Hospital header with branding (JRS Eduzone Radiology AI Centre)
- Patient demographics (name, age, gender, patient ID)
- Scan date and unique Report ID (format: `RPT-XXXXXXXX`)
- AI diagnosis: predicted disease + confidence percentage
- Full confidence score table for all 6 classes
- Embedded X-ray image + Grad-CAM heatmap + overlay image
- Doctor's clinical findings (free-text)
- Recommendations section
- Doctor name and designation footer
- Urgent case flag (when confidence > 85% for pathological findings)

> Reports are stored in `static/uploads/reports/` and tracked in the `reports` MongoDB collection.

---

## 🗄️ Database Schema

### `users` Collection
```json
{
  "_id": ObjectId,
  "name": "Dr. Arivumathi",
  "email": "doctor@jrs.com",
  "password": "<bcrypt_hash>",
  "role": "Radiologist",
  "designation": "Senior Radiologist",
  "profile_pic": "profile_uuid.png",
  "scan_count": 42,
  "last_login": ISODate,
  "created_at": ISODate
}
```

### `scans` Collection
```json
{
  "_id": ObjectId,
  "user_id": "doctor_object_id",
  "patient_name": "John Doe",
  "patient_age": "45",
  "patient_gender": "Male",
  "patient_id": "PAT-001",
  "original_filename": "uuid.jpg",
  "predicted_label": "Pneumonia",
  "confidence": 92.45,
  "all_scores": [
    { "class": "Pneumonia", "confidence": 92.45, "color": "#e74c3c" },
    ...
  ],
  "heatmap_paths": {
    "original": "path/to/original.jpg",
    "heatmap": "...", "overlay": "...",
    "jet": "...", "hot": "...", "turbo": "...",
    "side_by_side": "..."
  },
  "report_path": "path/to/report.pdf",
  "findings": "Bilateral infiltrates observed...",
  "recommendation": "Recommend immediate antibiotics...",
  "status": "reported",
  "is_urgent": true,
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### `reports` Collection
```json
{
  "_id": ObjectId,
  "report_id": "RPT-A3F92B1C",
  "scan_id": "scan_object_id",
  "user_id": "doctor_object_id",
  "patient_name": "John Doe",
  "predicted_label": "Pneumonia",
  "confidence": 92.45,
  "findings": "...",
  "recommendation": "...",
  "report_path": "static/uploads/reports/report_xxx.pdf",
  "doctor_name": "Dr. Arivumathi",
  "is_signed": false,
  "is_urgent": true,
  "created_at": ISODate,
  "updated_at": ISODate
}
```

---

## 🗺️ API Routes

| Method | Route | Description |
|---|---|---|
| `GET/POST` | `/auth/login` | Doctor login |
| `GET/POST` | `/auth/register` | New doctor registration |
| `GET` | `/auth/logout` | Session logout |
| `GET` | `/dashboard` | Analytics dashboard + recent scans |
| `GET/POST` | `/upload` | Upload X-ray + get AI prediction |
| `GET/POST` | `/heatmap/<scan_id>` | Generate + view Grad-CAM heatmaps |
| `GET/POST` | `/report/<scan_id>` | Write findings + generate PDF |
| `GET` | `/report/download/<scan_id>` | Download generated PDF |
| `GET` | `/history` | All scans for current doctor |
| `GET` | `/history/search?q=` | Search by patient/disease |
| `GET/POST` | `/profile` | View and update doctor profile |

---

## 📸 Screenshots Preview

> The application includes the following pages, each with its own dedicated CSS theme:

- **Login / Register** — Clean medical-grade authentication screen
- **Dashboard** — Stats cards (Total Scans, Urgent Cases, Normal, Reported) + disease distribution chart + recent scans table
- **Upload** — Drag-and-drop X-ray upload with patient info form → instant AI results with confidence bar chart
- **Heatmap Viewer** — Side-by-side JET / HOT / TURBO colormap comparison with the original X-ray
- **Report Editor** — Structured findings and recommendation form with live PDF preview
- **Scan History** — Filterable, searchable table of all past scans with status badges
- **Doctor Profile** — Profile picture upload and designation management

---

## 🔮 Future Enhancements

- [ ] **DICOM Support** — Accept `.dcm` DICOM files directly from radiology equipment
- [ ] **Multi-Model Ensemble** — Combine DenseNet121 + EfficientNet for higher accuracy
- [ ] **REST API** — Expose prediction endpoint for integration with Hospital Information Systems (HIS)
- [ ] **Real-time Notifications** — Alert doctors via email/SMS for urgent case flags
- [ ] **Audit Trail** — Full activity log for HIPAA/regulatory compliance
- [ ] **Mobile App** — React Native companion app for on-the-go scan review
- [ ] **Cloud Storage** — AWS S3 / Google Cloud Storage integration for scan files
- [ ] **Doctor Collaboration** — Shared scan access and second-opinion request workflow

---

## 👨‍💻 Author

<div align="center">

**Arivumathi S -**
**SNS College Of Technology**

Built with using Python, Flask, TensorFlow, and MongoDB

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/arivumathi-s/)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github)](https://github.com/4RIVX)

</div>

---

<div align="center">


*This project is part of my professional portfolio — showcasing end-to-end AI application development in the medical domain.*

</div>
