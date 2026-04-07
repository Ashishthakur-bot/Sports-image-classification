import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from flask import Flask, request, jsonify
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from PIL import Image
import numpy as np
import json

app = Flask(__name__)

# ✅ CORS FIX (IMPORTANT)
CORS(app, resources={r"/*": {"origins": "*"}})

# 🔹 Ensure headers always added
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# 🔹 Load model
model = load_model("model/image_classifier.h5")

# ✅ LOAD CLASS NAMES (BEST METHOD)
try:
    with open("model/classes.json") as f:
        classes = json.load(f)
    print("✅ Loaded class names from classes.json")
except:
    # 🔹 fallback if file not found
    num_classes = model.output_shape[1]
    classes = [f"Class {i}" for i in range(num_classes)]
    print("⚠️ Using default class names")

print("Model output shape:", model.output_shape)
print("Total classes:", len(classes))


# 🔹 Preprocessing (MobileNetV2)
def preprocess_image(image):
    image = image.resize((224, 224))
    image = np.array(image).astype("float32") / 255.0   # ✅ normalize
    image = np.expand_dims(image, axis=0)
    return image


@app.route("/predict", methods=["POST"])
def predict():
    try:
        file = request.files["file"]
        image = Image.open(file).convert("RGB")

        processed = preprocess_image(image)
        prediction = model.predict(processed)

        print("Prediction:", prediction)

        class_index = int(np.argmax(prediction))
        confidence = float(np.max(prediction))

        # ❌ Safety check
        if class_index >= len(classes):
            return jsonify({
                "error": "Class mismatch",
                "model_classes": prediction.shape[1],
                "your_classes": len(classes),
                "predicted_index": class_index
            })

        # ✅ TOP-3 PREDICTIONS
        top3_idx = prediction[0].argsort()[-3:][::-1]
        top3 = []

        for i in top3_idx:
            if i < len(classes):
                top3.append({
                    "class": classes[i],
                    "confidence": round(float(prediction[0][i]) * 100, 2)
                })

        return jsonify({
            "prediction": classes[class_index],
            "confidence": round(confidence * 100, 2),
            "top3": top3
        })

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)