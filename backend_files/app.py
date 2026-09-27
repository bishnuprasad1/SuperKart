# Flask backend that serves online and batch sales predictions using the trained pipeline

from flask import Flask, request, jsonify
import pandas as pd
import joblib
import os

# Initializing the Flask application
superkart_api = Flask(__name__)

# Loading the serialized pipeline (preprocessing steps + trained XGBoost model) once, at startup
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "superkart_model.joblib")
model_pipeline = joblib.load(MODEL_PATH)

# Feature columns expected by the pipeline, in the same order used during training
FEATURE_COLUMNS = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]


@superkart_api.get("/")
def home():
    # Simple health-check endpoint
    return jsonify({"message": "SuperKart Sales Prediction API is up and running."})


@superkart_api.post("/v1/predict")
def predict():
    """
    Online (single-record) inference endpoint.
    Expects a JSON body with the feature columns listed above and
    returns the model's predicted Product_Store_Sales_Total.
    """
    payload = request.get_json(force=True)

    # Wrapping the single record in a one-row DataFrame, in the expected column order
    input_df = pd.DataFrame([payload], columns=FEATURE_COLUMNS)

    prediction = model_pipeline.predict(input_df)[0]

    return jsonify({"predicted_sales": round(float(prediction), 2)})


@superkart_api.post("/v1/predictbatch")
def predict_batch():
    """
    Batch inference endpoint.
    Expects a CSV file uploaded under the form-data key 'file', containing
    the feature columns listed above (one row per product/store combination),
    and returns a JSON object mapping each row index to its predicted sales value.
    """
    uploaded_file = request.files["file"]
    input_df = pd.read_csv(uploaded_file)

    # Making sure the columns are in the order the pipeline expects
    input_df = input_df[FEATURE_COLUMNS]

    predictions = model_pipeline.predict(input_df)

    result = {str(idx): round(float(pred), 2) for idx, pred in enumerate(predictions)}

    return jsonify(result)


if __name__ == "__main__":
    # Running on port 8000 inside the container; this is mapped to the outside world via Docker
    superkart_api.run(host="0.0.0.0", port=8000, debug=False)
