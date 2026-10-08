import cv2
import numpy as np
from PIL import Image
from pathlib import Path


def edge_detection_canny(gray, threshold1=50, threshold2=150):
    """Use Canny edge detection for detailed edge finding."""
    return cv2.Canny(gray, threshold1, threshold2)


def edge_detection_sobel(gray, kernel_size=3):
    """Use Sobel operator for edge detection."""
    sobelx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=kernel_size)
    sobely = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=kernel_size)
    return np.sqrt(sobelx**2 + sobely**2).astype(np.uint8)


def edge_detection_laplacian(gray):
    """Use Laplacian operator for second-order derivative edges."""
    return cv2.Laplacian(gray, cv2.CV_32F)


def enhance_edges(gray, method='canny', **kwargs):
    """Enhance edges using various methods for better detail preservation."""
    if method == 'canny':
        return edge_detection_canny(gray, **kwargs)
    elif method == 'sobel':
        return edge_detection_sobel(gray, **kwargs)
    elif method == 'laplacian':
        laplacian = edge_detection_laplacian(gray)
        return cv2.convertScaleAbs(laplacian)
    else:
        return gray


def line_thinning(binary_image):
    """Apply morphological skeleton/thinning to preserve line structure."""
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    thinned = cv2.morphologyEx(binary_image, cv2.MORPH_ERODE, kernel, iterations=1)
    return thinned


def extract_fine_details(image_path, threshold=180, edge_method='canny',
                         enhance_factor=1.5, apply_thinning=False):
    """Extract fine details from bitmap using edge detection and enhancement."""
    original = Image.open(image_path).convert("RGB")
    gray = cv2.cvtColor(np.array(original), cv2.COLOR_RGB2GRAY)
    
    # Enhance local contrast with CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Apply edge detection
    edges = enhance_edges(enhanced, method=edge_method)
    
    # Enhance edge intensity
    edges = cv2.convertScaleAbs(edges * enhance_factor)
    edges = np.clip(edges, 0, 255).astype(np.uint8)
    
    # Combine with threshold-based binary
    _, binary = cv2.threshold(enhanced, threshold, 255, cv2.THRESH_BINARY)
    
    # Combine edges and binary for better detail preservation
    combined = cv2.bitwise_or(edges, binary)
    
    if apply_thinning:
        combined = line_thinning(combined)
    
    return combined, gray, edges, binary


def extract_fine_contours(edge_image, binary_image, min_area=5, simplification=0.001):
    """Extract contours from edge-enhanced image for maximum detail."""
    # Use edge image as primary source
    contours_edge, _ = cv2.findContours(edge_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Also get contours from binary
    contours_binary, _ = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    all_contours = contours_edge + contours_binary
    selected = []
    seen = set()

    for contour in all_contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue

        perimeter = cv2.arcLength(contour, True)
        epsilon = max(0.0, simplification * perimeter)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if len(approx) >= 3:
            # Avoid duplicates
            contour_tuple = tuple(map(tuple, approx.reshape(-1, 2)))
            if contour_tuple not in seen:
                seen.add(contour_tuple)
                selected.append(approx)

    selected.sort(key=lambda c: cv2.contourArea(c), reverse=True)
    return selected


if __name__ == "__main__":
    import argparse
    from vectorize_advanced import contours_to_svg_advanced

    parser = argparse.ArgumentParser(description="Extract fine details from bitmap.")
    parser.add_argument("input", help="Input bitmap")
    parser.add_argument("output", help="Output SVG")
    parser.add_argument("--threshold", type=int, default=180)
    parser.add_argument("--edge-method", default="canny", choices=["canny", "sobel", "laplacian"])
    parser.add_argument("--enhance", type=float, default=1.5, help="Edge enhancement factor")
    parser.add_argument("--thin", action="store_true", help="Apply line thinning")
    parser.add_argument("--min-area", type=int, default=5)
    parser.add_argument("--simplify", type=float, default=0.001)
    args = parser.parse_args()

    combined, gray, edges, binary = extract_fine_details(
        args.input,
        threshold=args.threshold,
        edge_method=args.edge_method,
        enhance_factor=args.enhance,
        apply_thinning=args.thin
    )
    
    contours = extract_fine_contours(combined, binary, min_area=args.min_area, simplification=args.simplify)
    
    original = Image.open(args.input)
    svg = contours_to_svg_advanced(contours, original.width, original.height, use_curves=True)
    
    Path(args.output).write_text(svg)
    print(f"Extracted {len(contours)} fine detail contours into {args.output}")
