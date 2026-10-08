import os
import tempfile
import streamlit as st
from PIL import Image
from vectorize_advanced import trace_bitmap_to_svg_advanced

st.set_page_config(
    page_title="Advanced Bitmap to Vector Converter",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎨 Advanced Bitmap to Vector Converter")
st.caption(
    "Chuyên nghiệp vector hóa bitmap cho hình ảnh chi tiết và phức tạp. "
    "Hỗ trợ CLAHE, Adaptive Threshold, Bezier smoothing, và corner preservation."
)

with st.sidebar:
    st.header("⚙️ Cài đặt xử lý ảnh")
    
    preset = st.selectbox(
        "Chọn preset",
        [
            "Tùy chỉnh",
            "Ảnh đơn giản (tối ưu cho logo)",
            "Ảnh chi tiết (tối ưu cho tranh vẽ)",
            "Ảnh phức tạp (tối ưu cho ảnh quét)",
            "Vẽ kỹ thuật (góc nhọn)",
        ]
    )
    
    # Load presets
    presets = {
        "Ảnh đơn giản (tối ưu cho logo)": {
            "threshold": 180,
            "blur": 1,
            "min_area": 20,
            "simplification": 0.005,
            "use_adaptive": False,
            "morpho_kernel": 3,
            "morph_iterations": 1,
            "use_bezier": False,
            "preserve_corners": False,
            "use_curves": False,
        },
        "Ảnh chi tiết (tối ưu cho tranh vẽ)": {
            "threshold": 160,
            "blur": 2,
            "min_area": 5,
            "simplification": 0.002,
            "use_adaptive": True,
            "morpho_kernel": 3,
            "morph_iterations": 1,
            "use_bezier": True,
            "preserve_corners": False,
            "use_curves": True,
        },
        "Ảnh phức tạp (tối ưu cho ảnh quét)": {
            "threshold": 150,
            "blur": 3,
            "min_area": 3,
            "simplification": 0.0015,
            "use_adaptive": True,
            "morpho_kernel": 5,
            "morph_iterations": 2,
            "use_bezier": True,
            "preserve_corners": False,
            "use_curves": True,
        },
        "Vẽ kỹ thuật (góc nhọn)": {
            "threshold": 170,
            "blur": 1,
            "min_area": 10,
            "simplification": 0.003,
            "use_adaptive": False,
            "morpho_kernel": 3,
            "morph_iterations": 1,
            "use_bezier": False,
            "preserve_corners": True,
            "use_curves": False,
        },
    }
    
    if preset in presets:
        params = presets[preset]
    else:
        params = {}
    
    st.subheader("Ngưỡng & Làm mềm")
    threshold = st.slider(
        "Ngưỡng nhị phân",
        0, 255, params.get("threshold", 180),
        help="Phân tách giữa nền và vật thể. Tăng để bỏ nền sáng hơn."
    )
    blur = st.slider(
        "Bán kính Gaussian Blur",
        0, 9, params.get("blur", 1), step=2,
        help="Làm mêm trước khi vector hóa. Giúp giảm nhiễu."
    )
    
    st.subheader("Phát hiện contour")
    min_area = st.slider(
        "Diện tích contour tối thiểu",
        1, 200, params.get("min_area", 10),
        help="Bỏ các chi tiết quá nhỏ (pixels). Giảm để giữ chi tiết nhỏ."
    )
    simplification = st.slider(
        "Mức độ đơn giản hóa",
        0.0001, 0.05, params.get("simplification", 0.003),
        format="%.4f",
        help="Giảm số điểm trên đường cong. Thấp = nhiều chi tiết, cao = mịn hơn."
    )
    
    st.subheader("Xử lý hình thái (Morphological)")
    use_adaptive = st.checkbox(
        "Dùng Adaptive Threshold",
        value=params.get("use_adaptive", False),
        help="Tốt hơn cho ảnh có độ sáng không đều."
    )
    morpho_kernel = st.slider(
        "Kích thước kernel hình thái",
        1, 7, params.get("morpho_kernel", 3), step=2,
        help="Lớn hơn = làm sạch nhiều nút thắt hơn."
    )
    morph_iterations = st.slider(
        "Số lần lặp morphological",
        1, 5, params.get("morph_iterations", 1),
        help="Tăng để làm sạch tốt hơn nhưng có thể mất chi tiết."
    )
    
    st.subheader("Làm mịn contour")
    use_bezier = st.checkbox(
        "Dùng Bezier Smoothing",
        value=params.get("use_bezier", False),
        help="Tạo đường cong mịn mà hơn bằng spline fitting."
    )
    preserve_corners = st.checkbox(
        "Giữ góc nhọn",
        value=params.get("preserve_corners", False),
        help="Giữ các góc sắc nét trong vẽ kỹ thuật."
    )
    
    st.subheader("SVG Output")
    use_curves = st.checkbox(
        "Dùng SVG Curves (Quadratic Bezier)",
        value=params.get("use_curves", False),
        help="Tạo SVG mịn hơn bằng quadratic Bezier curves."
    )
    
    invert = st.checkbox("Đảo ngược hình ảnh trước xử lý")

uploaded_file = st.file_uploader(
    "📤 Chọn ảnh bitmap",
    type=["png", "jpg", "jpeg", "bmp", "webp", "tiff"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    width, height = image.size

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📸 Ảnh gốc")
        st.image(image, use_column_width=True, caption=f"{width}×{height}px")
    
    with col2:
        st.subheader("✨ Vector Preview")
        
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            image.save(tmp.name)
            tmp_path = tmp.name
        
        try:
            with st.spinner("Đang vector hóa..."):
                # Build SVG
                result = trace_bitmap_to_svg_advanced(
                    tmp_path,
                    "/tmp/preview.svg",
                    threshold=threshold,
                    blur=blur,
                    min_area=min_area,
                    simplification=simplification,
                    invert=invert,
                    use_adaptive=use_adaptive,
                    morpho_kernel_size=morpho_kernel,
                    morph_iterations=morph_iterations,
                    use_bezier=use_bezier,
                    preserve_corners=preserve_corners,
                    use_curves=use_curves,
                )
            
            with open("/tmp/preview.svg", "r") as f:
                svg_content = f.read()
            
            svg_html = f"""
            <div style="border: 1px solid #e5e7eb; background: white; padding: 8px; 
                        overflow: auto; max-height: 700px; border-radius: 8px;">
                {svg_content}
            </div>
            """
            st.markdown(svg_html, unsafe_allow_html=True)
            
            st.download_button(
                label="⬇️ Tải SVG",
                data=svg_content,
                file_name="vectorized_output.svg",
                mime="image/svg+xml",
                use_container_width=True
            )
            
            st.success(
                f"✅ Hoàn tất! Contours: {result['contours']} | "
                f"Size: {result['width']}×{result['height']}px"
            )
        
        except Exception as e:
            st.error(f"❌ Lỗi: {str(e)}")
        
        finally:
            os.unlink(tmp_path)

else:
    st.info("👆 Tải lên ảnh bitmap để bắt đầu vector hóa!")
    st.markdown("""
    ### 💡 Mẹo sử dụng:
    
    1. **Ảnh đơn giản (logo, icon)**: Dùng preset "Ảnh đơn giản"
    2. **Tranh vẽ tay, chi tiết**: Dùng preset "Ảnh chi tiết" + Bezier + Curves
    3. **Ảnh quét có nhiều nốt**: Dùng preset "Ảnh phức tạp" + Adaptive Threshold
    4. **Vẽ kỹ thuật (CAD-style)**: Dùng preset "Vẽ kỹ thuật" + Preserve Corners
    
    ### 🎯 Các tham số quan trọng:
    
    - **Ngưỡng**: 150-180 cho ảnh bình thường, 100-150 cho ảnh nhạt
    - **Min Area**: 1-5 cho chi tiết nhỏ, 20+ để bỏ nhiễu
    - **Simplify**: 0.0005-0.002 cho chi tiết tối đa, 0.005+ để làm mịn
    - **Adaptive Threshold**: Tốt hơn cho ảnh có độ sáng không đều
    - **Bezier + Curves**: Kết hợp cho kết quả mịn nhất
    """)
