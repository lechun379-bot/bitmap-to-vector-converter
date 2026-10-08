import os
import tempfile

import streamlit as st
from PIL import Image

from vectorize import trace_bitmap_to_svg_bytes

st.set_page_config(page_title="Bitmap to Vector Converter", layout="wide")
st.title("Bitmap to Vector Converter")
st.caption("Upload a bitmap and export a clean SVG vector trace with fine contour detail preservation.")

with st.sidebar:
    st.header("Trace settings")
    threshold = st.slider("Threshold", 0, 255, 180)
    blur = st.slider("Blur radius", 0, 9, 1, step=2)
    min_area = st.slider("Min contour area", 1, 200, 10)
    simplification = st.slider("Simplification", 0.0005, 0.02, 0.003, format="%.4f")
    invert = st.checkbox("Invert image before tracing")

uploaded_file = st.file_uploader("Choose a bitmap image", type=["png", "jpg", "jpeg", "bmp", "webp"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    width, height = image.size

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original")
        st.image(image, use_column_width=True)

    with col2:
        st.subheader("Vector preview")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            image.save(tmp.name)
            tmp_path = tmp.name

        svg_content = trace_bitmap_to_svg_bytes(
            tmp_path,
            threshold=threshold,
            min_area=min_area,
            simplification=simplification,
            blur=blur,
            invert=invert,
        )

        os.unlink(tmp_path)

        svg_html = f"""
        <div style="border: 1px solid #e5e7eb; background: white; padding: 8px; overflow: auto; max-height: 700px;">
            {svg_content}
        </div>
        """
        st.markdown(svg_html, unsafe_allow_html=True)

        st.download_button(
            label="Download SVG",
            data=svg_content,
            file_name="vectorized_output.svg",
            mime="image/svg+xml",
        )

        st.info(
            f"Image size: {width} × {height}px | Generated SVG contour count: {svg_content.count('<path ')}"
        )
else:
    st.info("Upload a bitmap to convert it to precise vector contours.")
