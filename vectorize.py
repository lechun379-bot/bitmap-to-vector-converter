from PIL import Image
import cv2
import numpy as np
from pathlib import Path


def normalize_image(image):
    """Convert input to 8-bit RGB numpy array."""
    if isinstance(image, (str, Path)):
        img = Image.open(image).convert("RGB")
    else:
        img = image.convert("RGB")
    return np.array(img)


def ensure_odd(value):
    value = int(value)
    if value < 1:
        return 1
    if value % 2 == 0:
        return value + 1
    return value


def preprocess_bitmap(image, threshold=180, blur=1, invert=False):
    """Convert bitmap to a binary mask suitable for contour extraction."""
    rgb = normalize_image(image)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    if blur > 0:
        gray = cv2.GaussianBlur(gray, (ensure_odd(blur), ensure_odd(blur)), 0)

    if invert:
        gray = 255 - gray

    if threshold < 0:
        threshold = 0
    if threshold > 255:
        threshold = 255

    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    return binary


def extract_contours(binary, min_area=10, simplification=0.003):
    """Find contours on the binary image and simplify them for vector output."""
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    selected = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue

        perimeter = cv2.arcLength(contour, True)
        epsilon = max(0.0, simplification * perimeter)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if len(approx) >= 3:
            selected.append(approx)

    # Keep most significant contours first
    selected.sort(key=lambda c: cv2.contourArea(c), reverse=True)
    return selected


def contour_to_path(points):
    """Convert a contour to an SVG path string."""
    if len(points) < 3:
        return ""

    coords = points.reshape(-1, 2)
    segments = [f"M {coords[0][0]:.1f} {coords[0][1]:.1f}"]
    for x, y in coords[1:]:
        segments.append(f"L {x:.1f} {y:.1f}")
    segments.append("Z")
    return " ".join(segments)


def contours_to_svg(contours, width, height, stroke_width=1.0):
    """Render vector paths representing contours into a standalone SVG."""
    paths = []
    for contour in contours:
        path_data = contour_to_path(contour)
        if path_data:
            paths.append(
                f'<path d="{path_data}" fill="none" stroke="black" stroke-width="{stroke_width}" '
                'stroke-linejoin="round" stroke-linecap="round" />'
            )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="white" />
  {''.join(paths)}
</svg>
'''
    return svg


def trace_bitmap_to_svg(input_path, output_path, threshold=180, min_area=10, simplification=0.003, blur=1, invert=False):
    """Trace a bitmap image and save the vectorized output as an SVG file."""
    original = Image.open(input_path).convert("RGB")
    width, height = original.size

    binary = preprocess_bitmap(original, threshold=threshold, blur=blur, invert=invert)
    contours = extract_contours(binary, min_area=min_area, simplification=simplification)
    svg = contours_to_svg(contours, width=width, height=height)

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(svg, encoding="utf-8")

    return {
        "width": width,
        "height": height,
        "contours": len(contours),
        "path": str(out_path),
    }


def trace_bitmap_to_svg_bytes(input_path, threshold=180, min_area=10, simplification=0.003, blur=1, invert=False):
    """Return SVG content as a string for in-memory processing."""
    original = Image.open(input_path).convert("RGB")
    width, height = original.size
    binary = preprocess_bitmap(original, threshold=threshold, blur=blur, invert=invert)
    contours = extract_contours(binary, min_area=min_area, simplification=simplification)
    return contours_to_svg(contours, width=width, height=height)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Trace raster bitmap into vector paths.")
    parser.add_argument("input", help="Input bitmap image")
    parser.add_argument("output", help="Output SVG file")
    parser.add_argument("--threshold", type=int, default=180, help="Binary threshold, 0-255")
    parser.add_argument("--min-area", type=int, default=10, help="Minimum contour area")
    parser.add_argument("--simplify", type=float, default=0.003, help="Approximation factor")
    parser.add_argument("--blur", type=int, default=1, help="Gaussian blur radius")
    parser.add_argument("--invert", action="store_true", help="Invert the grayscale image before tracing")
    args = parser.parse_args()

    result = trace_bitmap_to_svg(
        args.input,
        args.output,
        threshold=args.threshold,
        min_area=args.min_area,
        simplification=args.simplify,
        blur=args.blur,
        invert=args.invert,
    )
    print(f"Vectorized {result['contours']} contours into {result['path']}")
