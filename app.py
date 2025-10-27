import streamlit as st
import cv2
import pytesseract
import numpy as np
from PIL import Image
import pandas as pd
import io
import re
import matplotlib.pyplot as plt

# Streamlit Page Config
st.set_page_config(page_title="🧾 AI Bill Analyzer", layout="wide")
st.title("🧾 AI Bill Analyzer")
st.write("Upload your bill or receipt image to extract, analyze, and visualize key insights.")

# File uploader
uploaded_file = st.file_uploader("📸 Upload Bill Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Display uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Bill Image", use_container_width=True)

    # Convert to grayscale
    image_np = np.array(image)
    gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)

    # OCR with pytesseract
    text = pytesseract.image_to_string(gray)

    # Show extracted text
    st.subheader("📋 Extracted Text")
    st.text_area("Text from Bill", text, height=200)

    # Detect lines that might contain amounts
    lines = [line.strip() for line in text.split("\n") if line.strip() != ""]
    amount_lines = [line for line in lines if re.search(r"\d+\.\d{2}", line)]

    # Create DataFrame
    df = pd.DataFrame(amount_lines, columns=["Detected Lines"])

    # Try to extract possible items and prices
    items, prices = [], []
    for line in amount_lines:
        match = re.search(r"(.*?)(\d+\.\d{2})", line)
        if match:
            item = match.group(1).strip().title()
            price = float(match.group(2))
            items.append(item)
            prices.append(price)

    if items and prices:
        data = pd.DataFrame({"Item": items, "Price (₹)": prices})
        st.subheader("📊 Detected Bill Details")
        st.dataframe(data)

        # Calculate totals
        subtotal = sum(prices)
        tax = subtotal * 0.18  # Assuming 18% tax
        total = subtotal + tax

        st.metric("🧾 Subtotal", f"₹{subtotal:.2f}")
        st.metric("💰 Estimated Tax (18%)", f"₹{tax:.2f}")
        st.metric("✅ Total Amount", f"₹{total:.2f}")

        # Category detection (simple keywords)
        categories = {
            "Food": ["pizza", "burger", "restaurant", "meal", "snack", "cafe"],
            "Grocery": ["milk", "rice", "sugar", "oil", "bread", "vegetable"],
            "Electronics": ["charger", "mobile", "tv", "headphone", "laptop"],
            "Clothing": ["shirt", "jeans", "dress", "shoe", "t-shirt"],
        }

        def detect_category(item):
            for cat, keywords in categories.items():
                for k in keywords:
                    if k.lower() in item.lower():
                        return cat
            return "Other"

        data["Category"] = data["Item"].apply(detect_category)
        st.subheader("🗂️ Categorized Expenses")
        st.dataframe(data)

        # Visualization
        st.subheader("📈 Expense Distribution")
        category_sum = data.groupby("Category")["Price (₹)"].sum()
        fig, ax = plt.subplots()
        category_sum.plot.pie(autopct="%1.1f%%", ax=ax)
        plt.ylabel("")
        st.pyplot(fig)

        # Download as CSV
        csv = data.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Bill Data (CSV)", csv, "bill_analysis.csv", "text/csv")

    else:
        st.warning("No valid amount lines detected. Try uploading a clearer image or a printed bill.")

# Sidebar Info
st.sidebar.header("⚙️ Advanced Features")
st.sidebar.markdown("""
- 🧾 OCR-based text extraction (Tesseract)
- 💰 Auto total and tax calculation
- 📦 Smart item categorization
- 📈 Expense visualization
- ⬇️ Data export as CSV
""")

st.sidebar.info("💡 Upcoming: Multi-language OCR, Invoice History, Cloud Save")
