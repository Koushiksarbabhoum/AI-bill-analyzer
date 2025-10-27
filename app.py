# app.py
import streamlit as st
from PIL import Image
import io

# lightweight pdf text extractor
try:
    import pdfplumber
except Exception:
    pdfplumber = None

st.set_page_config(page_title="AI Bill Analyzer - MVP", layout="centered")
st.title("🧾 AI Bill Analyzer — MVP")

uploaded_file = st.file_uploader("Upload an invoice (image or PDF with selectable text)", type=["png","jpg","jpeg","pdf"])

if uploaded_file is None:
    st.info("Upload a JPG/PNG image or a PDF that contains selectable text (not a scanned image).")
else:
    file_bytes = uploaded_file.read()
    file_type = uploaded_file.name.split('.')[-1].lower()

    if file_type == "pdf":
        if pdfplumber is None:
            st.error("pdfplumber not installed. Please check requirements.")
        else:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                # show first page as image if it has an image object, otherwise show nothing
                first_page = pdf.pages[0]
                text = first_page.extract_text()
                st.subheader("Extracted Text (from PDF text layer):")
                if text and text.strip():
                    st.code(text)
                else:
                    st.warning("This PDF looks like a scanned image (no selectable text). For scanned PDFs, use the mobile app or consider the paid OCR option later.")
                # optionally render page as image if available
                try:
                    pil_image = first_page.to_image(resolution=150).original
                    st.image(pil_image, caption="PDF first page (rendered)", use_column_width=True)
                except Exception:
                    pass
    else:
        # image file
        image = Image.open(io.BytesIO(file_bytes))
        st.image(image, caption="Uploaded image", use_column_width=True)
        st.subheader("Note")
        st.write("This MVP displays the image. OCR for scanned images is a next-step upgrade.")
