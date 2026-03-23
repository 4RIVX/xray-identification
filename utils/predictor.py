import numpy as np
import tensorflow as tf
import os
from config import Config  # Your JRS config.py

# Global model cache (loads once)
_model = None

def get_model():
    global _model
    if _model is None:
        print("🔍 Loading DenseNet121 chest X-ray model...")
        model_path = Config.MODEL_PATH  # Uses your config: ml_model/model_converted.h5
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}\n"
                                  f"Expected: {Config.BASE_DIR}/ml_model/model_converted.h5")
        
        _model = tf.keras.models.load_model(model_path, compile=False)
        print(f"✅ Model loaded! Params: {_model.count_params():,}")
    return _model

def predict_xray(img_path):
    """Flask-ready: img_path → full prediction dict"""
    model = get_model()
    
    if not os.path.exists(img_path):
        raise FileNotFoundError(f"Image not found: {img_path}")
    
    # DenseNet121 preprocess (224x224 + DenseNet input)
    img = tf.keras.utils.load_img(img_path, target_size=(224, 224))
    img_array = tf.keras.utils.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = tf.keras.applications.densenet.preprocess_input(img_array)  # Correct normalization
    
    # Predict
    predictions = model.predict(img_array, verbose=0)[0]
    predicted_index = np.argmax(predictions)
    confidence = float(np.max(predictions) * 100)
    predicted_label = Config.CLASS_LABELS[predicted_index]
    
    # All scores (top-to-bottom)
    all_scores = []
    for i, score in enumerate(predictions):
        all_scores.append({
            "class": Config.CLASS_LABELS[i],
            "confidence": round(float(score) * 100, 2),
            "color": Config.CLASS_COLORS.get(Config.CLASS_LABELS[i], '#ffffff')
        })
    all_scores.sort(key=lambda x: x["confidence"], reverse=True)
    
    return {
        "predicted_label": predicted_label,
        "confidence": round(confidence, 2),
        "predicted_index": int(predicted_index),
        "all_scores": all_scores,
        "color": Config.CLASS_COLORS.get(predicted_label, '#ffffff'),
        "urgent": confidence > Config.URGENT_THRESHOLD
    }

# VS Code Test (run directly)
if __name__ == "__main__":
    print("🚀 JRS Eduzone Chest X-ray Tester")
    try:
        # Test your model
        result = predict_xray("test_xray.jpg")  # Update path
        print(f"🎯 {result['predicted_label']}: {result['confidence']}%")
        for score in result['all_scores'][:3]:
            print(f"   {score['class']}: {score['confidence']}%")
    except Exception as e:
        print(f"❌ Error: {e}")
