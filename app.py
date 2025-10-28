import streamlit as st
import sqlite3
import os
import pytesseract
from PIL import Image
import datetime
import pandas as pd
import requests
import matplotlib.pyplot as plt

# ------------------- CONFIG -------------------
DB_PATH = "invoices.db"
UPLOAD_DIR = "data/uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

st.set_page_config(page_title="AI Bill Analyzer", page_icon="🧾", layout="wide")

# ------------------- DATABASE SETUP -------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS invoices (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_name TEXT,
                        saved_path TEXT,
                        upload_ts TEXT,
                        vendor TEXT,
                        invoice_no TEXT,
                        date TEXT,
                        total_amount REAL,
                        currency TEXT,
                        category TEXT,
                        extracted_text TEXT,
                        ai_summary TEXT
                    )''')
    conn.commit()
    conn.close()

init_db()

# ------------------- OCR FUNCTION -------------------
def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        image = image.convert("RGB")
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        return f"[OCR error: {e}]"

# ------------------- AI SUMMARY FUNCTION -------------------
def generate_smart_summary(text):
    try:
        api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        headers = {"Authorization": "Bearer hf_xxx_your_token_here"}  # Replace with your token
        payload = {"inputs": text[:2000]}
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code == 200:
            summary = response.json()[0]['summary_text']
            return summary
        else:
            return f"[AI summary error: API returned {response.status_code}]"
    except Exception as e:
        return f"[AI summary error: {e}]"

# ------------------- SAVE TO DATABASE -------------------
def save_to_db(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO invoices 
                    (file_name, saved_path, upload_ts, vendor, invoice_no, date, total_amount, currency, category, extracted_text, ai_summary)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (data["file_name"], data["saved_path"], data["upload_ts"], data["vendor"], data["invoice_no"],
                    data["date"], data["total_amount"], data["currency"], data["category"], data["extracted_text"], data["ai_summary"]))
    conn.commit()
    conn.close()

# ------------------- LOAD DATABASE -------------------
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM invoices ORDER BY id DESC", conn)
    conn.close()
    return df

# ------------------- SIDEBAR NAVIGATION -------------------
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to", ["📤 Upload Invoice", "📊 Dashboard", "⚖️ Compare Invoices"])

# ------------------- UPLOAD PAGE -------------------
if page == "📤 Upload Invoice":
    st.title("📤 Upload and Analyze Invoice")

    uploaded_file = st.file_uploader("Upload a bill/invoice image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            saved_path = os.path.join(UPLOAD_DIR, f"{timestamp}_{uploaded_file.name}")
            with open(saved_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.info(f"Processing OCR for {uploaded_file.name}...")
            extracted_text = extract_text_from_image(saved_path)

            st.text_area("Extracted Text (Preview)", extracted_text[:1000], height=150)

            with st.spinner("Generating Smart AI Summary..."):
                ai_summary = generate_smart_summary(extracted_text)
            st.text_area("AI Smart Summary", ai_summary, height=150)

            vendor = st.text_input("Vendor Name", "UNKNOWN")
            invoice_no = st.text_input("Invoice No")
            total_amount = st.number_input("Total Amount", min_value=0.0, step=0.01)
            currency = st.selectbox("Currency", ["INR", "USD", "EUR", "Other"])
            category = st.selectbox("Category", ["Utilities", "Supplies", "Travel", "Other"])
            invoice_date = st.date_input("Invoice Date", datetime.date.today())

            if st.button("💾 Save to Database"):
                data = {
                    "file_name": uploaded_file.name,
                    "saved_path": saved_path,
                    "upload_ts": datetime.datetime.now().isoformat(),
                    "vendor": vendor,
                    "invoice_no": invoice_no,
                    "date": invoice_date.isoformat(),
                    "total_amount": total_amount,
                    "currency": currency,
                    "category": category,
                    "extracted_text": extracted_text,
                    "ai_summary": ai_summary
                }
                save_to_db(data)
                st.success(f"✅ {uploaded_file.name} saved successfully!")
                st.rerun()

        except Exception as e:
            st.error(f"❌ Error: {e}")

# ------------------- DASHBOARD PAGE -------------------
# ------------------- DASHBOARD PAGE -------------------
elif page == "📊 Dashboard":
    st.title("📊 Invoice Dashboard")
    try:
        df = load_data()
        if df.empty:
            st.info("No invoices found yet. Upload some to view analytics.")
        else:
            st.dataframe(df, use_container_width=True)

            st.subheader("🧾 Invoice Previews (Medium Size)")
            cols = st.columns(3)  # Show 3 images per row
            for i, row in df.iterrows():
                with cols[i % 3]:
                    try:
                        st.image(row["saved_path"], caption=row["file_name"], width=250)
                    except:
                        st.warning(f"Image not found for {row['file_name']}")

            st.markdown("---")

            # Two charts side by side
            st.subheader("📊 Spending Insights")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**📈 Category Distribution**")
                category_counts = df["category"].value_counts()
                fig1, ax1 = plt.subplots(figsize=(3.5, 3.5))
                ax1.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%', startangle=90)
                st.pyplot(fig1, use_container_width=True)

            with col2:
                st.markdown("**💰 Total Amount by Vendor**")
                vendor_sum = df.groupby("vendor")["total_amount"].sum().sort_values(ascending=False)
                fig2, ax2 = plt.subplots(figsize=(4, 3))
                vendor_sum.plot(kind='bar', ax=ax2, color='skyblue')
                plt.xticks(rotation=45)
                st.pyplot(fig2, use_container_width=True)

            st.markdown("---")
            st.subheader("🕒 Recent Uploads")
            st.write(df[["file_name", "vendor", "total_amount", "upload_ts", "category"]].head(10))

    except Exception as e:
        st.error(f"❌ Dashboard error: {e}")


# ------------------- COMPARE INVOICES PAGE -------------------
elif page == "⚖️ Compare Invoices":
    st.title("⚖️ Compare Multiple Invoices")

    df = load_data()
    if df.empty:
        st.info("No invoices available for comparison.")
    else:
        options = df["file_name"].tolist()
        selected_files = st.multiselect("Select invoices to compare", options)

        if len(selected_files) >= 2:
            selected_df = df[df["file_name"].isin(selected_files)]

            st.subheader("📄 Selected Invoice Details")
            st.dataframe(selected_df[["file_name", "vendor", "invoice_no", "date", "total_amount", "category"]], use_container_width=True)

            st.subheader("💰 Comparison of Total Amounts")
            fig3, ax3 = plt.subplots()
            ax3.bar(selected_df["file_name"], selected_df["total_amount"], color="skyblue")
            plt.xticks(rotation=45)
            plt.ylabel("Amount")
            plt.title("Invoice Amount Comparison")
            st.pyplot(fig3)

            st.subheader("🧠 AI Summary Comparison")
            for _, row in selected_df.iterrows():
                st.markdown(f"**{row['file_name']} — {row['vendor']}**")
                st.info(row['ai_summary'])

        else:
            st.warning("Select at least two invoices to compare.")
