import streamlit as st
import easyocr
from PIL import Image
from pdf2image import convert_from_bytes

st.title("🧾 AI Bill Analyzer")

uploaded_file = st.file_uploader("Upload your bill or invoice", type=["jpg", "png", "jpeg", "pdf"])

if uploaded_file is not None:
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    if file_type == "pdf":
        st.info("Converting PDF to image...")
        images = convert_from_bytes(uploaded_file.read())
        image = images[0]  # Take the first page of the PDF
    else:
        image = Image.open(uploaded_file)

    st.image(image, caption="Uploaded Bill", use_column_width=True)

    reader = easyocr.Reader(['en'])
    result = reader.readtext(image)

    st.subheader("📋 Extracted Text:")
    for detection in result:
        st.write(detection[1])
