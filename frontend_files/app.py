# Streamlit frontend that talks to the Flask backend for online and batch sales predictions

import streamlit as st
import pandas as pd
import requests
import os

st.set_page_config(page_title="SuperKart Sales Predictor", layout="centered")
st.title("SuperKart Sales Prediction")
st.write("Predict the total sales revenue of a product at a given store.")

# The backend's address inside the Docker network (the two containers are connected
# via a shared Docker network and can reach each other by container name)
BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:8000")

tab1, tab2 = st.tabs(["Single Prediction", "Batch Prediction"])

# ---------------------- Online (single) inference ----------------------
with tab1:
    st.subheader("Enter Product & Store Details")

    col1, col2 = st.columns(2)
    with col1:
        product_weight = st.number_input("Product Weight", min_value=0.0, value=12.66)
        product_sugar_content = st.selectbox(
            "Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"]
        )
        product_allocated_area = st.number_input(
            "Product Allocated Area", min_value=0.0, max_value=1.0, value=0.027, format="%.3f"
        )
        product_mrp = st.number_input("Product MRP", min_value=0.0, value=117.08)
        product_id_char = st.selectbox("Product Id Prefix", ["FD", "DR", "NC"])
    with col2:
        store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
        store_location = st.selectbox(
            "Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"]
        )
        store_type = st.selectbox(
            "Store Type",
            ["Food Mart", "Supermarket Type1", "Supermarket Type2", "Departmental Store"],
        )
        store_age = st.number_input("Store Age (Years)", min_value=0, value=16)
        product_type_category = st.selectbox(
            "Product Type Category", ["Perishables", "Non Perishables"]
        )

    if st.button("Predict Sales"):
        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar_content,
            "Product_Allocated_Area": product_allocated_area,
            "Product_MRP": product_mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": store_location,
            "Store_Type": store_type,
            "Product_Id_char": product_id_char,
            "Store_Age_Years": store_age,
            "Product_Type_Category": product_type_category,
        }
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=15)
            response.raise_for_status()
            st.success(f"Predicted Sales: {response.json()['predicted_sales']}")
        except Exception as e:
            st.error(f"Prediction failed: {e}")

# ---------------------- Batch inference ----------------------
with tab2:
    st.subheader("Upload a CSV for Batch Prediction")
    st.caption(
        "The CSV must contain the columns: Product_Weight, Product_Sugar_Content, "
        "Product_Allocated_Area, Product_MRP, Store_Size, Store_Location_City_Type, "
        "Store_Type, Product_Id_char, Store_Age_Years, Product_Type_Category"
    )
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        preview_df = pd.read_csv(uploaded_file)
        st.dataframe(preview_df.head())
        uploaded_file.seek(0)

        if st.button("Run Batch Prediction"):
            try:
                files = {"file": uploaded_file.getvalue()}
                response = requests.post(
                    f"{BACKEND_URL}/v1/predictbatch", files=files, timeout=30
                )
                response.raise_for_status()
                preds = response.json()
                result_df = preview_df.copy()
                result_df["Predicted_Sales"] = [preds[str(i)] for i in range(len(preview_df))]
                st.write(result_df)
            except Exception as e:
                st.error(f"Batch prediction failed: {e}")
