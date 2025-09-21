# streamlit_app.py
import joblib
import streamlit as st
import numpy as np
import features
import time

# -------------------------------
# Load trained model
# -------------------------------
rf_model = joblib.load("Model/rf_model.pkl")

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="Phishing URL Detector", page_icon="🔍", layout="centered")

st.title("Phishing URL Detection App")
st.write("This tool predicts whether a given URL is **SAFE** or **HARMFUL** using a trained Random Forest model.")

# Define feature names
feature_names = [
    "having_IP_Address",
    "URL_Length",
    "Shortining_Service",
    "having_At_Symbol",
    "double_slash_redirecting",
    "Prefix_Suffix",
    "having_Sub_Domain",
    "SSLfinal_State",
    "Domain_registeration_length",
    "Favicon",
    "port",
    "HTTPS_token",
    "Request_URL",
    "URL_of_Anchor",
    "Links_in_tags",
    "SFH",
    "Submitting_to_email",
    "Abnormal_URL",
    "RightClick",
    "popUpWidnow",
    "Iframe",
    "age_of_domain",
    "DNSRecord",
    "Google_Index"
]

# Input field
url = st.text_input("Enter a URL to check:")

if st.button("Check URL"):
    if url.strip() == "":
        st.warning("⚠️ Please enter a valid URL first.")
    else:
        try:
            # -------------------------------
            # Loader while processing
            # -------------------------------
            with st.spinner("🔄 Extracting features and making prediction..."):

                # -------------------------------
                # Extract features
                # -------------------------------
                extracted_features = features.url_features(url)   # must return 24 values in correct order
                extracted_features = np.array(extracted_features).reshape(1, -1)

                # -------------------------------
                # Prediction
                # -------------------------------
                prediction = rf_model.predict(extracted_features)[0]
                proba = rf_model.predict_proba(extracted_features)[0] * 100

            # -------------------------------
            # Display results
            # -------------------------------
            st.subheader("🔎 Prediction Result")

            st.write(f"**Chances of being SAFE (-1):** {proba[0]:.2f}%")
            st.write(f"**Chances of being PHISHING (1):** {proba[1]:.2f}%")

            if prediction == 1:
                st.error(f"🚨 This link is predicted as **HARMFUL** with {proba[1]:.2f}% confidence.")
            else:
                st.success(f"✅ This link is predicted as **SAFE** with {proba[0]:.2f}% confidence.")

            # -------------------------------
            # Show extracted features with names
            # -------------------------------
            with st.expander("See extracted feature values"):
                feature_dict = {name: float(value) for name, value in zip(feature_names, extracted_features[0])}
                st.json(feature_dict)

        except Exception as e:
            st.error(f"❌ Error processing the URL: {e}")
