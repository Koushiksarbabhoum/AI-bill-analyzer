import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import io
import re
import numpy as np

# Path to Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Streamlit Page Configuration
st.set_page_config(page_title="🧾 AI Bill Analyzer", page_icon="🤖", layout="wide")

# Title Section
st.title("🧾 AI Bill Analyzer")
st.write("Upload your invoice or receipt image and get detailed insights automatically!")

# Session State Initialization
if "invoice_data" not in st.session_state:
    st.session_state["invoice_data"] = []

# Upload Section
uploaded_file = st.file_uploader("📤 Upload Invoice Image (JPG, PNG, or JPEG)", type=["jpg", "png", "jpeg"])

# OCR Processing
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="🧾 Uploaded Invoice", use_container_width=True)
    
    with st.spinner("Extracting text using AI OCR..."):
        text = pytesseract.image_to_string(image)

    st.subheader("🧠 Extracted Text")
    st.text_area("Invoice Text", text, height=200)

    # Basic Info Extraction
    amount_pattern = r"(?:INR|Rs\.?|₹)\s?([\d,]+\.?\d*)"
    date_pattern = r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
    total_pattern = r"total\s*(?:amount|bill)?[:\s]*([\d,]+\.?\d*)"

    amounts = re.findall(amount_pattern, text, re.IGNORECASE)
    dates = re.findall(date_pattern, text, re.IGNORECASE)
    totals = re.findall(total_pattern, text, re.IGNORECASE)

    total_amount = totals[-1] if totals else (amounts[-1] if amounts else "Not found")
    bill_date = dates[0] if dates else datetime.now().strftime("%d/%m/%Y")

    # Store to session
    st.session_state["invoice_data"].append({
        "File": uploaded_file.name,
        "Amount": total_amount,
        "Date": bill_date,
        "Uploaded_On": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # Summary Display
    st.success("✅ Invoice processed successfully!")
    st.metric(label="🧾 Total Amount", value=f"₹ {total_amount}")
    st.metric(label="📅 Bill Date", value=bill_date)

# Show Analytics
if len(st.session_state["invoice_data"]) > 0:
    st.subheader("📊 Expense Analytics")

    df = pd.DataFrame(st.session_state["invoice_data"])
    df["Amount"] = pd.to_numeric(df["Amount"].str.replace(",", ""), errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Monthly expense graph
    df_monthly = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum().reset_index()
    df_monthly["Date"] = df_monthly["Date"].astype(str)

    st.write("### 💸 Expense Trend Over Time")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df_monthly["Date"], df_monthly["Amount"], marker="o")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Spent (₹)")
    ax.set_title("Monthly Spending Trend")
    st.pyplot(fig)

    # Show table
    st.write("### 🧾 Processed Invoices")
    st.dataframe(df)

    # Download option
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Expense Report (CSV)",
        data=csv,
        file_name="ai_bill_analysis_report.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by Koushik Sarbabhoum | Powered by Streamlit + PyTesseract OCR")
