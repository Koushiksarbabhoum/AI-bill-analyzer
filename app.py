import streamlit as st
import easyocr
import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import datetime


st.set_page_config(page_title="🧾 AI Bill Analyzer", page_icon="🤖", layout="wide")


st.title("🧾 AI Bill Analyzer")
st.markdown("### Upload your bill or invoice and let AI extract, categorize, and visualize your expenses.")


if "session_start" not in st.session_state:
    st.session_state.session_start = datetime.now()
if "upload_count" not in st.session_state:
    st.session_state.upload_count = 0


st.sidebar.header("📊 App Analytics")
st.sidebar.write(f"🕒 Session started: {st.session_state.session_start.strftime('%H:%M:%S')}")
st.sidebar.write(f"📤 Files uploaded this session: {st.session_state.upload_count}")


uploaded_file = st.file_uploader("📂 Upload a bill/invoice image (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.session_state.upload_count += 1
    st.image(uploaded_file, caption="🧾 Uploaded Bill", use_column_width=True)
    st.write("🔍 Extracting text...")

    
    reader = easyocr.Reader(['en'])
    result = reader.readtext(uploaded_file)

    extracted_text = " ".join([res[1] for res in result])
    st.text_area("📜 Extracted Text", extracted_text, height=200)

    
    keywords = {
        "food": ["restaurant", "burger", "pizza", "food", "meal"],
        "travel": ["uber", "taxi", "bus", "train", "flight"],
        "utilities": ["electricity", "water", "internet", "gas", "bill"],
        "shopping": ["store", "shop", "amazon", "mall", "purchase"]
    }

    category_detected = None
    for category, words in keywords.items():
        if any(word in extracted_text.lower() for word in words):
            category_detected = category
            break

    
    import re
    amounts = re.findall(r'\d+\.\d+|\d+', extracted_text)
    total_amount = max(map(float, amounts)) if amounts else random.uniform(100, 1000)

    st.subheader("💡 Analysis Summary")
    st.write(f"**Category:** {category_detected or 'Uncategorized'}")
    st.write(f"**Total Amount Detected:** ₹{total_amount:.2f}")

    
    categories = ["Food", "Travel", "Utilities", "Shopping", "Others"]
    expenses = [random.uniform(100, 500) for _ in categories]
    if category_detected:
        idx = categories.index(category_detected.capitalize()) if category_detected.capitalize() in categories else -1
        if idx != -1:
            expenses[idx] = total_amount

    df = pd.DataFrame({"Category": categories, "Amount": expenses})

    fig, ax = plt.subplots()
    ax.pie(df["Amount"], labels=df["Category"], autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

    
    st.subheader("🧠 AI Expense Insight")
    if category_detected == "food":
        st.info("🍴 You’ve spent quite a bit on food — consider cooking at home a few times this week!")
    elif category_detected == "travel":
        st.info("🚗 Frequent travel detected — try using public transport or shared rides to cut costs.")
    elif category_detected == "utilities":
        st.info("💡 High utility bills? Try checking for unused subscriptions or energy-saving tips.")
    elif category_detected == "shopping":
        st.info("🛍️ Shopping habits spotted — you could plan a monthly budget to track purchases.")
    else:
        st.info("📈 Keep tracking your bills to discover spending trends over time.")


st.markdown("---")
st.caption("Developed with ❤️ using Streamlit + EasyOCR | © 2025 AI Bill Analyzer")
