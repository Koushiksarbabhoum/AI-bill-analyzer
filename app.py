import streamlit as st
import pytesseract
from PIL import Image
import numpy as np
import io
import re
import matplotlib.pyplot as plt
from datetime import datetime

# -----------------------------
# App Title & Description
# -----------------------------
st.set_page_config(page_title="🧾 AI Bill Analyzer", page_icon="🤖", layout="wide")

st.title("🧾 AI Bill Analyzer")
st.write("Upload any **invoice or bill image**, and I’ll automatically extract, summarize, and analyze key details for you!")

# -----------------------------
# Visitor Analytics Counter
# -----------------------------
if "visitor_count" not in st.session_state:
    st.session_state.visitor_count = 0
st.session_state.visitor_count += 1
st.sidebar.metric("👥 Visitors this session", st.session_state.visitor_count)

# -----------------------------
# File Upload Section
# -----------------------------
uploaded_file = st.file_uploader("📤 Upload your bill/invoice image (JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="🧾 Uploaded Invoice", use_column_width=True)

    # Convert image to text
    with st.spinner("🔍 Extracting text using OCR..."):
        text = pytesseract.image_to_string(image)

    # -----------------------------
    # Display Extracted Text
    # -----------------------------
    st.subheader("📄 Extracted Text")
    st.text_area("Raw Text", text, height=200)

    # -----------------------------
    # Extract Key Invoice Info
    # -----------------------------
    def extract_invoice_details(text):
        details = {}

        # Invoice number
        match = re.search(r"(?:Invoice|Bill|Receipt)\s*No[:\-]?\s*([A-Za-z0-9\-]+)", text, re.IGNORECASE)
        details["Invoice Number"] = match.group(1) if match else "Not found"

        # Date
        date_match = re.search(r"(\d{1,2}[-/\s]\d{1,2}[-/\s]\d{2,4})", text)
        details["Date"] = date_match.group(1) if date_match else "Not found"

        # Total amount
        total_match = re.search(r"Total\s*[:\-]?\s*₹?\s*([\d,.]+)", text, re.IGNORECASE)
        details["Total Amount"] = total_match.group(1) if total_match else "Not found"

        # Company / Vendor name
        company_match = re.search(r"(?:From|Vendor|Company)\s*[:\-]?\s*(.*)", text)
        details["Vendor"] = company_match.group(1).strip() if company_match else "Not found"

        return details

    details = extract_invoice_details(text)

    # -----------------------------
    # Display Extracted Details
    # -----------------------------
    st.subheader("🧠 Extracted Invoice Details")
    for key, val in details.items():
        st.write(f"**{key}:** {val}")

    # -----------------------------
    # Expense Category Detection
    # -----------------------------
    def categorize_expense(text):
        categories = {
            "Food": ["restaurant", "food", "meal", "dine", "pizza", "burger"],
            "Travel": ["uber", "ola", "travel", "flight", "bus", "train", "cab"],
            "Shopping": ["amazon", "flipkart", "purchase", "order", "item"],
            "Utilities": ["electricity", "water", "internet", "recharge", "bill"],
            "Medical": ["pharmacy", "hospital", "medicine", "health"]
        }
        for cat, keywords in categories.items():
            if any(k.lower() in text.lower() for k in keywords):
                return cat
        return "General"

    category = categorize_expense(text)
    st.success(f"💰 **Detected Expense Category:** {category}")

    # -----------------------------
    # Insights Visualization
    # -----------------------------
    st.subheader("📊 Quick Insights")

    labels = ["Subtotal", "Tax", "Discount", "Total"]
    values = [70, 10, 5, 85]

    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_title("Sample Bill Breakdown (%)")
    ax.set_ylabel("Amount")
    st.pyplot(fig)

    # -----------------------------
    # Download Extracted Info
    # -----------------------------
    result_text = "\n".join([f"{k}: {v}" for k, v in details.items()])
    result_text += f"\nDetected Category: {category}\nExtracted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    st.download_button(
        label="📥 Download Extracted Details",
        data=result_text,
        file_name="invoice_details.txt",
        mime="text/plain"
    )

else:
    st.info("👆 Upload an invoice to begin analysis!")

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("Built with ❤️ using Streamlit, Tesseract OCR, and Python. | © 2025 AI Bill Analyzer")
