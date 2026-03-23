import os, json, zipfile, tempfile, shutil
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf

MODEL_PATH  = 'ml_model/chest_xray_densenet_model.keras'
OUTPUT_PATH = 'ml_model/model_converted.h5'

print("Step 1: Extracting .keras zip...")
tmpdir = tempfile.mkdtemp()
with zipfile.ZipFile(MODEL_PATH, 'r') as z:
    z.extractall(tmpdir)

print("Step 2: Reading metadata.json...")
with open(os.path.join(tmpdir, 'metadata.json')) as f:
    meta = json.load(f)
print("Keras version used to save:", meta.get('keras_version'))

print("Step 3: Reading config.json...")
with open(os.path.join(tmpdir, 'config.json')) as f:
    cfg = json.load(f)

print("Step 4: Rebuilding model from config...")
model = tf.keras.models.model_from_json(json.dumps(cfg))

print("Step 5: Loading weights...")
model.load_weights(os.path.join(tmpdir, 'model.weights.h5'))

print("Step 6: Saving as legacy .h5...")
model.save(OUTPUT_PATH)
shutil.rmtree(tmpdir)

print(f"\n✅ Done! Saved → {OUTPUT_PATH}")
print(f"Params: {model.count_params():,}")
