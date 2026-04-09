#!/usr/bin/env python3
"""
ASCII Art Renderer using shape-vector matching.

Instead of treating ASCII characters as pixels (mapping lightness → density),
this renderer quantifies the geometric *shape* of each character using 6D shape
vectors, then picks the character whose shape best matches each grid cell.

Based on: https://alexharri.com/blog/ascii-rendering

Usage:
    python3 ascii_render.py <image_path> [--cols 80] [--contrast 0.3] [--output out.txt]
    python3 ascii_render.py <video_path> [--cols 100] [--fps 10]
    python3 ascii_render.py --camera [--cols 120] [--fps 15]
"""

import argparse
import math
import os
import sys
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont


# ---------------------------------------------------------------------------
# Character shape-vector precomputation
# ---------------------------------------------------------------------------

# 95 printable ASCII characters (0x20–0x7E)
PRINTABLE_ASCII = [chr(i) for i in range(0x20, 0x7F)]

SIMPLE_CHARSET = list(" .:-=+*#%@")

BLOCK_CHARSET = list(" ░▒▓█▄▀▌▐")


def _find_monospace_font(size: int = 20) -> ImageFont.FreeTypeFont:
    """Try common monospace font paths, fall back to default."""
    candidates = [
        # macOS
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.dfont",
        "/Library/Fonts/Courier New.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
        # Windows
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/cour.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _render_char_bitmap(char: str, font: ImageFont.FreeTypeFont,
                        cell_w: int, cell_h: int) -> np.ndarray:
    """Render a single character into a grayscale bitmap of size (cell_h, cell_w)."""
    img = Image.new("L", (cell_w, cell_h), 0)
    draw = ImageDraw.Draw(img)
    bbox = font.getbbox(char)
    char_w = bbox[2] - bbox[0]
    char_h = bbox[3] - bbox[1]
    x = (cell_w - char_w) // 2 - bbox[0]
    y = (cell_h - char_h) // 2 - bbox[1]
    draw.text((x, y), char, fill=255, font=font)
    return np.array(img, dtype=np.float32) / 255.0


def _make_sampling_circles(cell_w: int, cell_h: int):
    """
    Create 6 sampling circles in a 3-row x 2-column staggered layout.

    Left column circles are shifted slightly down, right column slightly up,
    and circles are sized to cover most of the cell while minimizing gaps.

    Returns list of (cx, cy, radius) tuples.
    """
    col_centers = [cell_w * 0.3, cell_w * 0.7]
    row_centers = [cell_h * 0.25, cell_h * 0.5, cell_h * 0.75]

    # Subtle stagger: left goes slightly lower, right slightly higher
    stagger = cell_h * 0.03
    radius = cell_w * 0.35

    circles = []
    for row_idx in range(3):
        # Left circle (shifted slightly down)
        cx_l = col_centers[0]
        cy_l = row_centers[row_idx] + stagger
        circles.append((cx_l, cy_l, radius))
        # Right circle (shifted slightly up)
        cx_r = col_centers[1]
        cy_r = row_centers[row_idx] - stagger
        circles.append((cx_r, cy_r, radius))

    return circles


def _sample_circle_overlap(bitmap: np.ndarray, cx: float, cy: float,
                           radius: float) -> float:
    """Compute fraction of pixels within a circle that are 'lit' in the bitmap."""
    h, w = bitmap.shape
    total = 0
    lit = 0.0
    r2 = radius * radius
    y_min = max(0, int(cy - radius))
    y_max = min(h, int(cy + radius) + 1)
    x_min = max(0, int(cx - radius))
    x_max = min(w, int(cx + radius) + 1)
    for y in range(y_min, y_max):
        for x in range(x_min, x_max):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r2:
                total += 1
                lit += bitmap[y, x]
    return lit / total if total > 0 else 0.0


def precompute_shape_vectors(charset=None, font_size: int = 24,
                             font_aspect: float = 2.0):
    """
    Precompute normalized 6D shape vectors for each character.

    Returns:
        list of (character, shape_vector) tuples
    """
    if charset is None:
        charset = PRINTABLE_ASCII

    font = _find_monospace_font(font_size)

    # Determine cell dimensions from a reference character
    bbox = font.getbbox("M")
    cell_w = bbox[2] - bbox[0] + 4  # small padding
    cell_h = int(cell_w * font_aspect)

    circles = _make_sampling_circles(cell_w, cell_h)

    raw_vectors = []
    valid_chars = []
    for char in charset:
        try:
            bitmap = _render_char_bitmap(char, font, cell_w, cell_h)
            vec = [_sample_circle_overlap(bitmap, cx, cy, r) for cx, cy, r in circles]
            raw_vectors.append(vec)
            valid_chars.append(char)
        except Exception:
            continue

    if not raw_vectors:
        raise RuntimeError("Failed to compute shape vectors for any character")

    raw_vectors = np.array(raw_vectors)

    # Normalize: divide each dimension by its max
    max_per_dim = raw_vectors.max(axis=0)
    max_per_dim[max_per_dim == 0] = 1.0  # avoid division by zero
    normalized = raw_vectors / max_per_dim

    return list(zip(valid_chars, normalized.tolist()))


# ---------------------------------------------------------------------------
# Image sampling & rendering
# ---------------------------------------------------------------------------

def _rgb_to_lightness(r: float, g: float, b: float) -> float:
    """Convert RGB (0-255) to relative luminance (0-1)."""
    return 0.2126 * (r / 255.0) + 0.7152 * (g / 255.0) + 0.0722 * (b / 255.0)


def _sample_cell(image_array: np.ndarray, cell_x: float, cell_y: float,
                 cell_w: float, cell_h: float, circles_template,
                 font_aspect: float) -> list:
    """
    Sample a cell from the source image using 6 sampling circles.

    Returns a 6D sampling vector.
    """
    img_h, img_w = image_array.shape[:2]
    has_color = len(image_array.shape) == 3

    vector = []
    for cx_frac, cy_frac, r_frac in circles_template:
        # Map circle center and radius to image coordinates
        cx = cell_x + cx_frac * cell_w
        cy = cell_y + cy_frac * cell_h
        radius = r_frac * cell_w

        # Take samples within the circle
        n_samples = 12  # balance of quality vs speed
        total_light = 0.0
        count = 0
        for angle_idx in range(n_samples):
            angle = 2 * math.pi * angle_idx / n_samples
            for r_mult in [0.0, 0.5, 1.0]:
                sx = int(cx + math.cos(angle) * radius * r_mult)
                sy = int(cy + math.sin(angle) * radius * r_mult)
                if 0 <= sx < img_w and 0 <= sy < img_h:
                    if has_color:
                        px = image_array[sy, sx]
                        total_light += _rgb_to_lightness(px[0], px[1], px[2])
                    else:
                        total_light += image_array[sy, sx] / 255.0
                    count += 1
        vector.append(total_light / count if count > 0 else 0.0)

    return vector


def enhance_contrast(vector: list, strength: float = 0.3) -> list:
    """
    Push sampling vector components away from their mean to sharpen edges.
    """
    if strength <= 0:
        return vector
    mean = sum(vector) / len(vector)
    enhanced = []
    for v in vector:
        diff = v - mean
        new_v = mean + diff * (1.0 + strength)
        enhanced.append(max(0.0, min(1.0, new_v)))
    return enhanced


def find_best_character(sampling_vector: list,
                        characters: list) -> tuple:
    """
    Find the character whose shape vector is closest to the sampling vector.

    Returns (character, color_tuple_or_None).
    """
    best_char = " "
    best_dist = float("inf")
    for char, shape_vec in characters:
        dist = sum((a - b) ** 2 for a, b in zip(sampling_vector, shape_vec))
        if dist < best_dist:
            best_dist = dist
            best_char = char
    return best_char


def render_image_to_ascii(image: Image.Image, cols: int = 80,
                          font_aspect: float = 2.0, contrast: float = 0.3,
                          invert: bool = False, characters=None,
                          color: bool = False) -> str:
    """
    Convert a PIL Image to ASCII art string using shape-vector matching.
    """
    if characters is None:
        characters = precompute_shape_vectors()

    img_array = np.array(image)
    img_h, img_w = img_array.shape[:2]

    cell_w = img_w / cols
    cell_h = cell_w * font_aspect
    rows = int(img_h / cell_h)

    if rows == 0 or cols == 0:
        return ""

    # Sampling circle template (fractional positions within a cell)
    # 3 rows x 2 cols, staggered — must match _make_sampling_circles layout
    stagger = 0.03
    circles_template = [
        (0.3, 0.25 + stagger, 0.35),  # top-left
        (0.7, 0.25 - stagger, 0.35),  # top-right
        (0.3, 0.50 + stagger, 0.35),  # mid-left
        (0.7, 0.50 - stagger, 0.35),  # mid-right
        (0.3, 0.75 + stagger, 0.35),  # bot-left
        (0.7, 0.75 - stagger, 0.35),  # bot-right
    ]

    lines = []
    for row in range(rows):
        line_chars = []
        for col in range(cols):
            cx = col * cell_w
            cy = row * cell_h

            sv = _sample_cell(img_array, cx, cy, cell_w, cell_h,
                              circles_template, font_aspect)

            if invert:
                sv = [1.0 - v for v in sv]

            sv = enhance_contrast(sv, contrast)

            char = find_best_character(sv, characters)

            if color and len(img_array.shape) == 3:
                # Get average color of the cell for ANSI coloring
                y0 = int(cy)
                y1 = min(int(cy + cell_h), img_h)
                x0 = int(cx)
                x1 = min(int(cx + cell_w), img_w)
                region = img_array[y0:y1, x0:x1]
                if region.size > 0:
                    avg_color = region.mean(axis=(0, 1)).astype(int)
                    r, g, b = avg_color[0], avg_color[1], avg_color[2]
                    if invert:
                        r, g, b = 255 - r, 255 - g, 255 - b
                    line_chars.append(f"\033[38;2;{r};{g};{b}m{char}\033[0m")
                else:
                    line_chars.append(char)
            else:
                line_chars.append(char)

        lines.append("".join(line_chars))

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Video / camera rendering
# ---------------------------------------------------------------------------

def render_video_to_ascii(source, cols=80, font_aspect=2.0, contrast=0.3,
                          invert=False, characters=None, color=False,
                          fps=15, output_path=None):
    """Render video or camera feed as ASCII in the terminal."""
    try:
        import cv2
    except ImportError:
        print("Error: opencv-python is required for video/camera mode.", file=sys.stderr)
        print("Install with: pip install opencv-python", file=sys.stderr)
        sys.exit(1)

    if characters is None:
        characters = precompute_shape_vectors()

    if source == "__camera__":
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print(f"Error: Cannot open video source: {source}", file=sys.stderr)
        sys.exit(1)

    frame_delay = 1.0 / fps
    frame_count = 0

    try:
        while True:
            t_start = time.time()
            ret, frame = cap.read()
            if not ret:
                break

            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)

            ascii_frame = render_image_to_ascii(
                img, cols=cols, font_aspect=font_aspect, contrast=contrast,
                invert=invert, characters=characters, color=color
            )

            # Clear screen and print
            sys.stdout.write("\033[H\033[J")
            sys.stdout.write(ascii_frame)
            sys.stdout.flush()

            frame_count += 1

            # Frame rate control
            elapsed = time.time() - t_start
            if elapsed < frame_delay:
                time.sleep(frame_delay - elapsed)

    except KeyboardInterrupt:
        pass
    finally:
        cap.release()

    if output_path:
        # Save last frame
        with open(output_path, "w") as f:
            f.write(ascii_frame)
        print(f"\nLast frame saved to {output_path}", file=sys.stderr)

    print(f"\nRendered {frame_count} frames", file=sys.stderr)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="ASCII Art Renderer using shape-vector matching"
    )
    parser.add_argument("input", nargs="?", help="Image or video path")
    parser.add_argument("--camera", action="store_true", help="Use webcam")
    parser.add_argument("--cols", type=int, default=80, help="Output columns (default: 80)")
    parser.add_argument("--contrast", type=float, default=0.3,
                        help="Contrast enhancement strength 0.0-1.0 (default: 0.3)")
    parser.add_argument("--invert", action="store_true",
                        help="Invert lightness (for light-on-dark terminals)")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--color", action="store_true", help="Enable ANSI true-color output")
    parser.add_argument("--charset", choices=["full", "simple", "blocks"],
                        default="full", help="Character set (default: full)")
    parser.add_argument("--font-aspect", type=float, default=2.0,
                        help="Font aspect ratio height/width (default: 2.0)")
    parser.add_argument("--fps", type=int, default=15,
                        help="Target FPS for video/camera (default: 15)")

    args = parser.parse_args()

    if not args.input and not args.camera:
        parser.error("Provide an image/video path or use --camera")

    # Select charset
    if args.charset == "simple":
        charset = SIMPLE_CHARSET
    elif args.charset == "blocks":
        charset = BLOCK_CHARSET
    else:
        charset = PRINTABLE_ASCII

    print("Precomputing character shape vectors...", file=sys.stderr)
    characters = precompute_shape_vectors(charset=charset, font_aspect=args.font_aspect)
    print(f"Ready ({len(characters)} characters)", file=sys.stderr)

    # Determine if input is video or image
    is_video = False
    if args.camera:
        is_video = True
    elif args.input:
        ext = os.path.splitext(args.input)[1].lower()
        if ext in (".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv"):
            is_video = True

    if is_video:
        source = "__camera__" if args.camera else args.input
        render_video_to_ascii(
            source, cols=args.cols, font_aspect=args.font_aspect,
            contrast=args.contrast, invert=args.invert,
            characters=characters, color=args.color,
            fps=args.fps, output_path=args.output
        )
    else:
        # Image mode
        try:
            img = Image.open(args.input).convert("RGB")
        except Exception as e:
            print(f"Error opening image: {e}", file=sys.stderr)
            sys.exit(1)

        result = render_image_to_ascii(
            img, cols=args.cols, font_aspect=args.font_aspect,
            contrast=args.contrast, invert=args.invert,
            characters=characters, color=args.color
        )

        if args.output:
            with open(args.output, "w") as f:
                f.write(result)
            print(f"Written to {args.output}", file=sys.stderr)
        else:
            print(result)


if __name__ == "__main__":
    main()
