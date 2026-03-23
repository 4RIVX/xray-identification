import numpy as np
import tensorflow as tf
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from PIL import Image
import os

# ─────────────────────────────────────────────
# CORE GRAD-CAM ENGINE
# ─────────────────────────────────────────────

def get_gradcam_heatmap(model, img_array, last_conv_layer_name="relu"):
    """
    Generates raw Grad-CAM heatmap from the last conv layer.
    Returns a 2D numpy array (heatmap).
    """
    grad_model = tf.keras.models.Model(
        inputs=model.inputs,
        outputs=[
            model.get_layer(last_conv_layer_name).output,
            model.output
        ]
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        predicted_class = tf.argmax(predictions[0])
        class_channel = predictions[:, predicted_class]

    # Gradients of the predicted class w.r.t. the conv layer output
    grads = tape.gradient(class_channel, conv_outputs)

    # Mean intensity of gradients over each feature map
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    # Multiply each feature map by its importance weight
    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)

    # Normalize between 0 and 1
    heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
    return heatmap.numpy(), int(predicted_class.numpy()), predictions.numpy()


# ─────────────────────────────────────────────
# OVERLAY HEATMAP ON ORIGINAL X-RAY
# ─────────────────────────────────────────────

def overlay_heatmap_on_image(original_img_path, heatmap, alpha=0.45, colormap=cv2.COLORMAP_JET):
    """
    Overlays the heatmap on the original X-ray image.
    Returns the final blended image as numpy array.
    """
    # Load original image
    original = cv2.imread(original_img_path)
    original = cv2.resize(original, (224, 224))

    # Resize heatmap to match original image
    heatmap_resized = cv2.resize(heatmap, (224, 224))

    # Apply colormap to heatmap
    heatmap_colored = np.uint8(255 * heatmap_resized)
    heatmap_colored = cv2.applyColorMap(heatmap_colored, colormap)

    # Blend original image with heatmap
    superimposed = cv2.addWeighted(original, 1 - alpha, heatmap_colored, alpha, 0)

    return superimposed, original, heatmap_colored


# ─────────────────────────────────────────────
# SAVE ALL 4 VERSIONS
# ─────────────────────────────────────────────

def save_gradcam_outputs(original_img_path, model, save_folder, filename_prefix):
    """
    Generates and saves:
    - original.jpg       (clean resized original)
    - heatmap.jpg        (pure colormap heatmap)
    - overlay.jpg        (blended heatmap on X-ray)
    - side_by_side.jpg   (comparison image for display)
    Returns dict of saved file paths.
    """
    os.makedirs(save_folder, exist_ok=True)

    # Preprocess image for model
    img = tf.keras.preprocessing.image.load_img(original_img_path, target_size=(224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    # Get Grad-CAM heatmap
    heatmap, predicted_class, predictions = get_gradcam_heatmap(model, img_array)

    # Overlay heatmap on original
    overlay, original, heatmap_colored = overlay_heatmap_on_image(original_img_path, heatmap)

    # Define save paths
    paths = {
        "original":     os.path.join(save_folder, f"{filename_prefix}_original.jpg"),
        "heatmap":      os.path.join(save_folder, f"{filename_prefix}_heatmap.jpg"),
        "overlay":      os.path.join(save_folder, f"{filename_prefix}_overlay.jpg"),
        "side_by_side": os.path.join(save_folder, f"{filename_prefix}_comparison.jpg"),
    }

    # Save individual images
    cv2.imwrite(paths["original"], original)
    cv2.imwrite(paths["heatmap"], heatmap_colored)
    cv2.imwrite(paths["overlay"], overlay)

    # Create premium side-by-side comparison
    gap = np.ones((224, 10, 3), dtype=np.uint8) * 30
    side_by_side = np.hstack([original, gap, heatmap_colored, gap, overlay])
    cv2.imwrite(paths["side_by_side"], side_by_side)

    return paths, predicted_class, predictions


# ─────────────────────────────────────────────
# CONFIDENCE SCORES PER CLASS
# ─────────────────────────────────────────────

def get_confidence_scores(predictions, class_indices):
    """
    Returns sorted list of (class_name, confidence%) for display.
    """
    class_names = {v: k for k, v in class_indices.items()}
    scores = []
    for i, score in enumerate(predictions[0]):
        scores.append({
            "class":      class_names.get(i, f"Class {i}"),
            "confidence": round(float(score) * 100, 2)
        })
    scores.sort(key=lambda x: x["confidence"], reverse=True)
    return scores


# ─────────────────────────────────────────────
# MATPLOTLIB COLORBAR HEATMAP (for PDF Report)
# ─────────────────────────────────────────────

def generate_matplotlib_heatmap(heatmap, save_path):
    """
    Saves a high-quality matplotlib heatmap with colorbar.
    Used for embedding inside the PDF report.
    """
    plt.figure(figsize=(6, 5))
    plt.imshow(heatmap, cmap='jet', interpolation='bilinear')
    plt.colorbar(label='Activation Intensity')
    plt.title('Grad-CAM Activation Map', fontsize=13, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    return save_path


# ─────────────────────────────────────────────
# MULTI-COLORMAP HEATMAP VARIANTS
# ─────────────────────────────────────────────

def generate_colormap_variants(original_img_path, heatmap, save_folder, prefix):
    """
    Generates 3 colormap variants for display on heatmap page:
    - JET (classic red-blue)
    - HOT (white-yellow-red)
    - VIRIDIS-style (TURBO)
    """
    os.makedirs(save_folder, exist_ok=True)
    colormaps = {
        "jet":   cv2.COLORMAP_JET,
        "hot":   cv2.COLORMAP_HOT,
        "turbo": cv2.COLORMAP_TURBO,
    }
    original = cv2.imread(original_img_path)
    original = cv2.resize(original, (224, 224))
    heatmap_resized = cv2.resize(heatmap, (224, 224))
    heatmap_uint8 = np.uint8(255 * heatmap_resized)

    saved_paths = {}
    for name, cmap in colormaps.items():
        colored = cv2.applyColorMap(heatmap_uint8, cmap)
        blended = cv2.addWeighted(original, 0.55, colored, 0.45, 0)
        path = os.path.join(save_folder, f"{prefix}_{name}.jpg")
        cv2.imwrite(path, blended)
        saved_paths[name] = path

    return saved_paths
