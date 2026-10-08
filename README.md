# Bitmap to Vector Converter

Một ứng dụng Python giúp chuyển bitmap (PNG/JPG/BMP) thành SVG vector bằng kỹ thuật phát hiện contour và approximation đường biên. Dự án này phù hợp cho việc giữ lại chi tiết nhỏ, góc cạnh và hình dạng phức tạp trong ảnh raster.

## Tính năng

- Tải ảnh bitmap lên từ máy tính
- Chuyển đổi sang vùng nhị phân bằng threshold và blur
- Khám phá contour và giữ lại chi tiết nhỏ bằng độ nhạy có thể điều chỉnh
- Xuất ra file SVG để chỉnh sửa tiếp trên Illustrator, Figma hoặc web
- Hỗ trợ giao diện Streamlit và CLI

## Cài đặt

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Chạy giao diện web

```bash
streamlit run app.py
```

Mở trình duyệt tới địa chỉ hiển thị trong terminal (thường là http://localhost:8501).

## Chạy CLI

```bash
python vectorize_cli.py input.png output.svg --threshold 180 --min-area 10 --simplify 0.003
```

## Tham số quan trọng

- `--threshold`: ngưỡng phân tách nền và vật thể
- `--min-area`: giới hạn diện tích contour tối thiểu để bỏ nhiễu
- `--simplify`: hệ số làm mịn/giảm điểm đường cong
- `--blur`: làm mịn ảnh trước khi vector hóa
- `--invert`: đảo ngược ảnh nếu cần đọc vùng đối tượng trên nền trắng/sẫm

## Gợi ý sử dụng

- Với ảnh có đường viền sắc nét: dùng threshold ở khoảng 150-200
- Với hình ảnh có nhiều chi tiết nhỏ: giảm `--min-area` và giảm `--simplify`
- Với ảnh nhiễu: tăng `--blur` và `--min-area`

## Lưu ý

Đây là phương pháp vector hóa theo đường viền (contour tracing), phù hợp với bitmap có hình dạng rõ ràng. Nếu muốn chuyển các ảnh ảnh chụp có bức ảnh phức tạp, độ chính xác có thể cần điều chỉnh thêm thuật toán nâng cấp như simplification/edge fitting hoặc giải pháp dựa trên OCR/AI tracing.
