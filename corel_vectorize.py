from pathlib import Path
import cv2
import numpy as np
from PIL import Image


def ensure_odd(value):
    value = int(value)
    if value < 1:
        return 1
    if value % 2 == 0:
        return value + 1
    return value


def preprocess(image, threshold=160, blur=2, invert=False):
    rgb = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    if blur > 0:
        gray = cv2.GaussianBlur(gray, (ensure_odd(blur), ensure_odd(blur)), 0)
    if invert:
        gray = 255 - gray
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)
    return binary


def contour_to_path(points):
    pts = points.reshape(-1, 2)
    if len(pts) < 3:
        return ""
    parts = [f"M {pts[0][0]:.2f} {pts[0][1]:.2f}"]
    for x, y in pts[1:]:
        parts.append(f"L {x:.2f} {y:.2f}")
    parts.append("Z")
    return " ".join(parts)


def contours_to_svg(contours, width, height):
    paths = []
    for idx, contour in enumerate(contours):
        path_data = contour_to_path(contour)
        if path_data:
            paths.append(
                f'<path id="path-{idx}" d="{path_data}" fill="none" stroke="black" '
                'stroke-width="1" stroke-linejoin="round" stroke-linecap="round" />'
            )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="white" />
  {''.join(paths)}
</svg>
'''


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Vectorize a bitmap for CorelDRAW import.")
    parser.add_argument("input", help="Input bitmap png/jpeg path")
    parser.add_argument("output", help="Output SVG path")
    parser.add_argument("--threshold", type=int, default=160)
    parser.add_argument("--blur", type=int, default=2)
    parser.add_argument("--min-area", type=int, default=5)
    parser.add_argument("--simplify", type=float, default=0.002)
    parser.add_argument("--adaptive", action="store_true")
    parser.add_argument("--bezier", action="store_true")
    parser.add_argument("--curves", action="store_true")
    parser.add_argument("--invert", action="store_true")
    args = parser.parse_args()

    image = Image.open(args.input).convert("RGB")
    width, height = image.size

    binary = preprocess(image, threshold=args.threshold, blur=args.blur, invert=args.invert)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    selected = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < args.min_area:
            continue
        perimeter = cv2.arcLength(contour, True)
        epsilon = max(0.0, args.simplify * perimeter)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        if len(approx) >= 3:
            selected.append(approx)

    selected.sort(key=lambda c: cv2.contourArea(c), reverse=True)

    svg = contours_to_svg(selected, width, height)
    Path(args.output).write_text(svg, encoding="utf-8")
    print(f"Saved SVG: {args.output}")


if __name__ == "__main__":
    main()
