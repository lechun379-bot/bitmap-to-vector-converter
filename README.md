# Bitmap to Vector Converter - Advanced Edition

Ứng dụng chuyên nghiệp chuyển đổi bitmap sang SVG vector với hỗ trợ các hình ảnh chi tiết và phức tạp.

## 🎯 Tính năng chính

### Xử lý ảnh nâng cao
- **CLAHE** (Contrast Limited Adaptive Histogram Equalization) để tăng cường chi tiết cục bộ
- **Adaptive Threshold** cho ảnh có độ sáng không đều
- **Xử lý hình thái** (morphological operations) để làm sạch nhiễu
- **Canny/Sobel/Laplacian** edge detection cho chi tiết nhỏ

### Vector hóa chính xác
- **Bezier Smoothing** - Làm mượt đường cong thông qua spline fitting
- **Corner Preservation** - Giữ lại các góc nhọn cho vẽ kỹ thuật
- **Quadratic Bezier Curves** trong SVG để làm mịn hơn
- **Fine Detail Extraction** - Phát hiện và giữ lại chi tiết tới mức pixel

### Preset tối ưu
1. **Ảnh đơn giản** - Logo, icon, hình dạng cơ bản
2. **Ảnh chi tiết** - Tranh vẽ tay, phác thảo, vẽ tự do
3. **Ảnh phức tạp** - Ảnh quét, ảnh có nhiều tín hiệu, nền phức tạp
4. **Vẽ kỹ thuật** - CAD-style, góc nhọn, độ chính xác cao

## 📦 Cài đặt

```bash
python -m venv .venv
source .venv/bin/activate  # Trên Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 🚀 Sử dụng

### Giao diện Web (Streamlit)

```bash
streamlit run app_advanced.py
```

Mở trình duyệt tại `http://localhost:8501` để sử dụng giao diện đầy đủ.

### CLI - Xử lý nâng cao

```bash
python vectorize_advanced.py input.png output.svg \
  --adaptive \
  --bezier \
  --preserve-corners \
  --curves \
  --min-area 5 \
  --simplify 0.002
```

### CLI - Trích xuất chi tiết

```bash
python vectorize_details.py input.png output.svg \
  --edge-method canny \
  --enhance 1.5 \
  --min-area 3 \
  --simplify 0.001
```

## 📋 Tham số chi tiết

### Threshold (Ngưỡng nhị phân)
- **150-170**: Cho ảnh nhạt, có nền sáng
- **180-200**: Cho ảnh bình thường
- **Adaptive**: Tốt hơn cho ảnh có độ sáng không đều

### Min Area (Diện tích tối thiểu)
- **1-5**: Giữ tất cả chi tiết, kể cả rất nhỏ
- **10-20**: Bỏ nhiễu nhỏ, giữ chi tiết chính
- **50+**: Chỉ giữ hình dạng chính

### Simplification (Mức độ đơn giản hóa)
- **0.0005-0.001**: Chi tiết cực đại, đường cong phức tạp
- **0.002-0.003**: Cân bằng chi tiết và độ mịn
- **0.005+**: Làm mịn mạnh, ít điểm hơn

### Morphological Kernel & Iterations
- **Kernel 3x3, 1 lần**: Làm sạch nhẹ, giữ chi tiết
- **Kernel 5x5, 2-3 lần**: Làm sạch mạnh, mất chi tiết nhỏ

### Edge Detection Methods (vectorize_details.py)
- **Canny**: Cân bằng tốt, phát hiện biên rõ ràng
- **Sobel**: Nhạy với gradient, tốt cho họa tiết
- **Laplacian**: Phát hiện biên sắc nét, nhạy với nhiễu

## 💡 Công thức tối ưu cho các loại ảnh

### Logo/Icon (tối ưu chất lượng)
```
Threshold: 180
Blur: 1
Min Area: 20
Simplify: 0.005
Adaptive: NO
Bezier: NO
Corners: NO
```

### Tranh vẽ/Phác thảo (chi tiết tối đa)
```
Threshold: 160
Blur: 2
Min Area: 5
Simplify: 0.0015
Adaptive: YES
Bezier: YES
Curves: YES
Corners: NO
```

### Ảnh quét/Phức tạp (làm sạch + chi tiết)
```
Threshold: 140-160
Blur: 3-4
Min Area: 3-5
Simplify: 0.001-0.002
Adaptive: YES
Morpho Kernel: 5
Morpho Iterations: 2
Bezier: YES
Curves: YES
```

### Vẽ kỹ thuật CAD (góc nhọn)
```
Threshold: 170
Blur: 1
Min Area: 10
Simplify: 0.003
Adaptive: NO
Preserve Corners: YES
Curves: NO
```

### Chi tiết cực nhỏ (Edge Detection)
```
python vectorize_details.py input.png output.svg
  --edge-method canny
  --enhance 2.0
  --min-area 2
  --simplify 0.0008
```

## 📊 So sánh các mode

| Mode | Ngưỡng | Chi tiết | Tốc độ | Tốt cho |
|------|--------|----------|--------|----------|
| Đơn giản | Cố định | Trung bình | Nhanh | Logo |
| Nâng cao | Cố định | Cao | Trung bình | Tranh vẽ |
| Chi tiết | Edge-based | Cực cao | Chậm | Texture |
| Kỹ thuật | Cố định | Cao | Nhanh | CAD |

## 🎨 Tips cho kết quả tốt nhất

1. **Chuẩn bị ảnh đầu vào**
   - Cắt bỏ nền thừa
   - Tăng cộng độ tương phản nếu cần
   - Lưu dưới dạng PNG (không nén mất dữ liệu)

2. **Điều chỉnh từng bước**
   - Bắt đầu với preset phù hợp
   - Điều chỉnh `min_area` trước tiên
   - Sau đó tùy chỉnh `simplification`
   - Cuối cùng thêm Bezier/Curves nếu cần

3. **Phối hợp tham số**
   - Blur + Min Area = làm sạch nhiễu
   - Simplification + Bezier = bàn mịn
   - Adaptive + Morpho = xử lý ảnh phức tạp
   - Preserve Corners + No Curves = kỹ thuật

4. **Kiểm tra kết quả**
   - Xem preview SVG trước khi download
   - Kiểm tra chi tiết nhỏ có bị mất không
   - Kiểm tra góc/biên có bị làm tròn không

## 📁 Cấu trúc project

```
.
├── vectorize.py                # Basic contour tracing
├── vectorize_advanced.py       # Advanced processing + Bezier
├── vectorize_details.py        # Edge detection + fine details
├── app.py                      # Basic Streamlit UI
├── app_advanced.py             # Advanced Streamlit UI
├── vectorize_cli.py            # CLI wrapper (tương thích)
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## 🔧 Troubleshooting

### Quá nhiều đường nét nhỏ?
→ Tăng `min_area`, giảm `blur`

### Mất chi tiết?
→ Giảm `min_area`, giảm `simplification`, thêm `--bezier`

### Đường cong không mịn?
→ Thêm `--bezier` và `--curves`, giảm `simplification`

### Góc bị làm tròn?
→ Thêm `--preserve-corners`, bỏ `--curves`

### Ảnh quét có nhiều nốt?
→ Dùng preset "Ảnh phức tạp", tăng `--morph-iter`

## 📚 Tài liệu thêm

- [OpenCV Documentation](https://docs.opencv.org/)
- [SVG Specification](https://www.w3.org/TR/SVG2/)
- [Bezier Curves](https://en.wikipedia.org/wiki/B%C3%A9zier_curve)

## 📝 License

MIT License - Tự do sử dụng cho mục đích cá nhân và thương mại.
