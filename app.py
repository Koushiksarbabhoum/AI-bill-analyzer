import streamlit as st
import pandas as pd
import numpy as np
import pytesseract
import cv2
from PIL import Image
import io
import os

# ---------------- CONFIGURE TESSERACT PATH ----------------
if os.name == "nt":  # Windows
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:  # Linux (Streamlit Cloud)
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# ---------------- STREAMLIT APP CONFIG ----------------
st.set_page_config(page_title="AI Bill Analyzer", layout="wide")

st.title("💡 AI Bill Analyzer & Insights Dashboard")
st.caption("Upload your invoices and let AI extract, analyze, and visualize insights automatically.")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("📄 Upload an invoice image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Invoice", use_container_width=True)

    # Convert image to grayscale for better OCR accuracy
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    text = pytesseract.image_to_string(gray)

    st.subheader("🧾 Extracted Text")
    st.text_area("OCR Output", text, height=200)

    # Try to extract useful fields
    data = {
        "Date": [],
        "Item": [],
        "Amount": [],
    }

    lines = text.split("\n")
    for line in lines:
        if "202" in line or "20/" in line:  # Detect date-like patterns
            data["Date"].append(line.strip())
        elif any(char.isdigit() for char in line) and any(char.isalpha() for char in line):
            data["Item"].append(line.strip())
        elif any(c.isdigit() for c in line) and "." in line:
            data["Amount"].append(line.strip())

    # Create DataFrame
    df = pd.DataFrame.from_dict(data, orient="index").transpose()
    st.subheader("📊 Extracted Data Table")
    st.dataframe(df, width='stretch')

    # ---------------- ANALYTICS SECTION ----------------
    st.subheader("📈 Bill Analytics & Insights")

    if not df.empty:
        # Convert Amount column
        def extract_amount(val):
            try:
                val = str(val)
                val = ''.join(ch for ch in val if ch.isdigit() or ch == '.')
                return float(val)
            except:
                return np.nan

        df["Amount"] = df["Amount"].apply(extract_amount)
        total = df["Amount"].sum()
        avg = df["Amount"].mean()

        st.metric("💰 Total Amount", f"₹ {total:,.2f}")
        st.metric("📉 Average Amount per Item", f"₹ {avg:,.2f}")

        # Monthly trend (dummy grouping if no dates)
        st.bar_chart(df["Amount"].dropna())

        # AI-based suggestion
        st.subheader("🤖 AI Insights")
        if avg > 5000:
            st.success("Your spending this month seems high. Consider reviewing big-ticket purchases.")
        elif avg > 1000:
            st.info("Your spending pattern looks moderate. Keep tracking recurring expenses.")
        else:
            st.warning("Your bills are quite low — great job managing your finances!")

    else:
        st.warning("No structured data detected. Try uploading a clearer image.")

# ---------------- FOOTER ----------------
st.divider()
st.caption("🚀 Built by Koushik — AI-powered Bill Analysis with OCR, NLP & Data Visualization")
