"""
Image Processing Utilities for Flask App
Works with Flask FileStorage uploads
"""

import os
import uuid
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image, ImageEnhance, ImageFilter


# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
class Config:
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
    UPLOAD_FOLDER = "uploads"
    PROFILE_FOLDER = "profiles"


# ─────────────────────────────────────────────
# CHECK FILE EXTENSION
# ─────────────────────────────────────────────
def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


# ─────────────────────────────────────────────
# SAVE UPLOADED X-RAY IMAGE
# ─────────────────────────────────────────────
def save_uploaded_file(file, folder: str = Config.UPLOAD_FOLDER) -> Tuple[str, str]:

    folder_path = Path(folder)
    folder_path.mkdir(parents=True, exist_ok=True)

    original_name = file.filename
    ext = Path(original_name).suffix.lower()

    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_path = folder_path / unique_name

    file.save(save_path)

    return unique_name, str(save_path)


# ─────────────────────────────────────────────
# PREPROCESS IMAGE FOR AI MODEL
# ─────────────────────────────────────────────
def preprocess_for_model(img_path: str, target_size=(224, 224)):

    img = Image.open(img_path).convert("RGB")
    img = img.resize(target_size, Image.Resampling.LANCZOS)

    return img


# ─────────────────────────────────────────────
# ENHANCE X-RAY IMAGE
# ─────────────────────────────────────────────
def enhance_xray(img_path: str, save_path: Optional[str] = None) -> str:

    img = Image.open(img_path).convert("RGB")

    img = ImageEnhance.Contrast(img).enhance(1.4)
    img = ImageEnhance.Sharpness(img).enhance(1.3)
    img = img.filter(ImageFilter.EDGE_ENHANCE)

    if save_path is None:
        folder = Path(Config.UPLOAD_FOLDER) / "enhanced"
        folder.mkdir(parents=True, exist_ok=True)
        save_path = folder / f"enhanced_{Path(img_path).stem}.jpg"

    img.save(save_path, quality=95)

    return str(save_path)


# ─────────────────────────────────────────────
# PROFILE PICTURE UPLOAD
# ─────────────────────────────────────────────
def save_profile_picture(file, folder: str = Config.PROFILE_FOLDER):

    folder_path = Path(folder)
    folder_path.mkdir(parents=True, exist_ok=True)

    filename = file.filename
    ext = Path(filename).suffix.lower()

    unique_name = f"profile_{uuid.uuid4().hex}{ext}"
    save_path = folder_path / unique_name

    img = Image.open(file).convert("RGB")

    width, height = img.size
    min_dim = min(width, height)

    left = (width - min_dim) // 2
    top = (height - min_dim) // 2

    img = img.crop((left, top, left + min_dim, top + min_dim))
    img = img.resize((300, 300), Image.Resampling.LANCZOS)

    img.save(save_path, quality=95)

    return unique_name, str(save_path)


# ─────────────────────────────────────────────
# VALIDATE IF IMAGE LOOKS LIKE X-RAY
# ─────────────────────────────────────────────
def is_valid_xray(img_path: str, grey_threshold: float = 0.55) -> bool:

    try:
        img = Image.open(img_path).convert("RGB")
        img = img.resize((50, 50))

        pixels = list(img.getdata())

        grey_count = sum(
            1 for r, g, b in pixels
            if abs(r - g) < 30 and abs(g - b) < 30
        )

        return grey_count / len(pixels) > grey_threshold

    except Exception:
        return True


# ─────────────────────────────────────────────
# QUICK LOCAL TEST
# ─────────────────────────────────────────────
if __name__ == "__main__":

    if not os.path.exists("test_image.jpg"):
        img = Image.new('RGB', (400, 300), color='gray')
        img.save("test_image.jpg")

    print("Testing image processor...")

    img = preprocess_for_model("test_image.jpg")
    print("Model image size:", img.size)

    enhanced = enhance_xray("test_image.jpg")
    print("Enhanced saved:", enhanced)

    print("Valid X-ray:", is_valid_xray("test_image.jpg"))

    print("✅ All functions working!")