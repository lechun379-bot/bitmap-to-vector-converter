import argparse
from pathlib import Path

from vectorize import trace_bitmap_to_svg


def main():
    parser = argparse.ArgumentParser(description="Convert a bitmap to SVG vector output.")
    parser.add_argument("input", type=str, help="Source bitmap file")
    parser.add_argument("output", type=str, help="Destination SVG file")
    parser.add_argument("--threshold", type=int, default=180, help="Grayscale threshold (0-255)")
    parser.add_argument("--blur", type=int, default=1, help="Gaussian blur radius")
    parser.add_argument("--min-area", type=int, default=10, help="Minimum contour area")
    parser.add_argument("--simplify", type=float, default=0.003, help="Contour approximation factor")
    parser.add_argument("--invert", action="store_true", help="Invert bitmap before tracing")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {args.input}")

    result = trace_bitmap_to_svg(
        str(input_path),
        str(output_path),
        threshold=args.threshold,
        min_area=args.min_area,
        simplification=args.simplify,
        blur=args.blur,
        invert=args.invert,
    )

    print(f"Created vector SVG at {result['path']}")
    print(f"Dimensions: {result['width']} × {result['height']}")
    print(f"Detected contours: {result['contours']}")


if __name__ == "__main__":
    main()
