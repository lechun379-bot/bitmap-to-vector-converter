import cv2
import numpy as np
from scipy.interpolate import splprep, BSpline
from PIL import Image
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


def adaptive_threshold(gray, block_size=11, method='gaussian'):
    """Apply adaptive thresholding for better edge detection in complex images."""
    block_size = ensure_odd(block_size)
    if method == 'gaussian':
        return cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, block_size, 2
        )
    else:
        return cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY, block_size, 2
        )


def preprocess_bitmap_advanced(image, threshold=180, blur=1, invert=False,
                                use_adaptive=False, adaptive_block=11,
                                morpho_kernel_size=3, morph_iterations=1):
    """Advanced preprocessing with morphological operations for complex images."""
    rgb = normalize_image(image)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) for better detail
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    if blur > 0:
        gray = cv2.GaussianBlur(gray, (ensure_odd(blur), ensure_odd(blur)), 0)

    if invert:
        gray = 255 - gray

    # Apply adaptive or fixed threshold
    if use_adaptive:
        binary = adaptive_threshold(gray, block_size=adaptive_block)
    else:
        threshold = max(0, min(255, threshold))
        _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

    # Morphological operations to clean up small artifacts
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morpho_kernel_size, morpho_kernel_size))
    
    # Close to fill small holes
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=morph_iterations)
    
    # Open to remove small noise
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=morph_iterations)

    return binary


def smooth_contour_with_bezier(points, num_control_points=None):
    """Fit Bezier curve through contour points for smoother output."""
    if len(points) < 4:
        return points

    points = points.reshape(-1, 2).astype(np.float32)
    
    try:
        # Use spline interpolation for smoother curves
        tck, u = splprep([points[:, 0], points[:, 1]], s=10, k=min(3, len(points) - 1))
        u_smooth = np.linspace(0, 1, max(len(points), 50))
        smooth_x, smooth_y = BSpline(*tck)(u_smooth)
        return np.column_stack([smooth_x, smooth_y])
    except:
        # Fallback: simple averaging if spline fails
        return points


def preserve_edges(contour, edge_threshold=0.1):
    """Preserve sharp edges and corners in contours."""
    if len(contour) < 3:
        return contour

    points = contour.reshape(-1, 2).astype(np.float32)
    
    # Calculate angles at each point
    preserved = [points[0]]
    
    for i in range(1, len(points) - 1):
        p1 = points[i - 1]
        p2 = points[i]
        p3 = points[i + 1]
        
        v1 = p1 - p2
        v2 = p3 - p2
        
        len_v1 = np.linalg.norm(v1)
        len_v2 = np.linalg.norm(v2)
        
        if len_v1 > 0 and len_v2 > 0:
            cos_angle = np.dot(v1, v2) / (len_v1 * len_v2)
            cos_angle = np.clip(cos_angle, -1, 1)
            angle = np.arccos(cos_angle)
            
            # Keep points that form sharp angles (corners)
            if angle < (np.pi - edge_threshold) or angle > edge_threshold:
                preserved.append(p2)
    
    preserved.append(points[-1])
    return np.array(preserved)


def extract_contours_advanced(binary, min_area=10, simplification=0.003,
                               max_contours=None, use_bezier=False,
                               preserve_corners=False, approx_method='poly'):
    """Extract and refine contours with multiple smoothing strategies."""
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    selected = []

    for idx, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area < min_area:
            continue

        perimeter = cv2.arcLength(contour, True)
        
        # Use different approximation methods
        if approx_method == 'poly':
            epsilon = max(0.0, simplification * perimeter)
            approx = cv2.approxPolyDP(contour, epsilon, True)
        elif approx_method == 'chain':
            approx = cv2.approxPolyDP(contour, simplification * perimeter, True)
        else:
            approx = contour

        if len(approx) >= 3:
            # Optional: preserve corners for technical drawings
            if preserve_corners:
                approx = preserve_edges(approx)
            
            # Optional: smooth with Bezier curves
            if use_bezier and len(approx) > 4:
                approx = smooth_contour_with_bezier(approx)
            
            selected.append(approx)

    # Sort by area, keep most significant ones
    selected.sort(key=lambda c: cv2.contourArea(c), reverse=True)
    
    if max_contours:
        selected = selected[:max_contours]

    return selected


def contour_to_path_advanced(points, use_curve=False):
    """Convert contour to SVG path with optional curve fitting."""
    if len(points) < 3:
        return ""

    coords = points.reshape(-1, 2)
    segments = [f"M {coords[0][0]:.2f} {coords[0][1]:.2f}"]
    
    if use_curve and len(coords) > 2:
        # Use quadratic Bezier curves for smoother paths
        for i in range(1, len(coords) - 1):
            cp_x, cp_y = coords[i]
            next_x, next_y = coords[i + 1]
            segments.append(f"Q {cp_x:.2f} {cp_y:.2f} {next_x:.2f} {next_y:.2f}")
        segments.append(f"L {coords[-1][0]:.2f} {coords[-1][1]:.2f}")
    else:
        # Use straight lines
        for x, y in coords[1:]:
            segments.append(f"L {x:.2f} {y:.2f}")
    
    segments.append("Z")
    return " ".join(segments)


def contours_to_svg_advanced(contours, width, height, stroke_width=1.0,
                             fill_style='none', stroke_color='black',
                             use_curves=False, add_filters=False):
    """Render contours to SVG with advanced styling and optional filters."""
    paths = []
    
    for idx, contour in enumerate(contours):
        path_data = contour_to_path_advanced(contour, use_curve=use_curves)
        if path_data:
            fill = "none" if fill_style == 'none' else f"rgba(0,0,0,0.1)"
            paths.append(
                f'<path id="path-{idx}" d="{path_data}" fill="{fill}" '
                f'stroke="{stroke_color}" stroke-width="{stroke_width}" '
                f'stroke-linejoin="round" stroke-linecap="round" '
                f'vector-effect="non-scaling-stroke" />'
            )

    filters = ""
    if add_filters:
        filters = '''
  <defs>
    <filter id="smoothing">
      <feGaussianBlur in="SourceGraphic" stdDeviation="0.5" />
    </filter>
  </defs>
        '''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="white" />
{filters}
  {''.join(paths)}
</svg>
'''
    return svg


def trace_bitmap_to_svg_advanced(input_path, output_path,
                                  threshold=180,
                                  blur=1,
                                  min_area=10,
                                  simplification=0.003,
                                  invert=False,
                                  use_adaptive=False,
                                  adaptive_block=11,
                                  morpho_kernel_size=3,
                                  morph_iterations=1,
                                  max_contours=None,
                                  use_bezier=False,
                                  preserve_corners=False,
                                  use_curves=False,
                                  add_filters=False):
    """Advanced bitmap to SVG tracing with all options."""
    original = Image.open(input_path).convert("RGB")
    width, height = original.size

    binary = preprocess_bitmap_advanced(
        original,
        threshold=threshold,
        blur=blur,
        invert=invert,
        use_adaptive=use_adaptive,
        adaptive_block=adaptive_block,
        morpho_kernel_size=morpho_kernel_size,
        morph_iterations=morph_iterations
    )

    contours = extract_contours_advanced(
        binary,
        min_area=min_area,
        simplification=simplification,
        max_contours=max_contours,
        use_bezier=use_bezier,
        preserve_corners=preserve_corners
    )

    svg = contours_to_svg_advanced(
        contours,
        width=width,
        height=height,
        use_curves=use_curves,
        add_filters=add_filters
    )

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(svg, encoding="utf-8")

    return {
        "width": width,
        "height": height,
        "contours": len(contours),
        "path": str(out_path),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Advanced bitmap to vector tracing.")
    parser.add_argument("input", help="Input bitmap image")
    parser.add_argument("output", help="Output SVG file")
    parser.add_argument("--threshold", type=int, default=180, help="Binary threshold")
    parser.add_argument("--blur", type=int, default=1, help="Blur radius")
    parser.add_argument("--min-area", type=int, default=10, help="Min contour area")
    parser.add_argument("--simplify", type=float, default=0.003, help="Simplification factor")
    parser.add_argument("--invert", action="store_true", help="Invert image")
    parser.add_argument("--adaptive", action="store_true", help="Use adaptive threshold")
    parser.add_argument("--adaptive-block", type=int, default=11, help="Adaptive block size")
    parser.add_argument("--morpho-kernel", type=int, default=3, help="Morphological kernel size")
    parser.add_argument("--morph-iter", type=int, default=1, help="Morphological iterations")
    parser.add_argument("--max-contours", type=int, default=None, help="Max contours to keep")
    parser.add_argument("--bezier", action="store_true", help="Use Bezier smoothing")
    parser.add_argument("--preserve-corners", action="store_true", help="Preserve sharp corners")
    parser.add_argument("--curves", action="store_true", help="Use SVG curves")
    parser.add_argument("--filters", action="store_true", help="Add SVG filters")
    args = parser.parse_args()

    result = trace_bitmap_to_svg_advanced(
        args.input,
        args.output,
        threshold=args.threshold,
        blur=args.blur,
        min_area=args.min_area,
        simplification=args.simplify,
        invert=args.invert,
        use_adaptive=args.adaptive,
        adaptive_block=args.adaptive_block,
        morpho_kernel_size=args.morpho_kernel,
        morph_iterations=args.morph_iter,
        max_contours=args.max_contours,
        use_bezier=args.bezier,
        preserve_corners=args.preserve_corners,
        use_curves=args.curves,
        add_filters=args.filters
    )
    print(f"Vectorized {result['contours']} contours into {result['path']}")
