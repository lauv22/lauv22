"""
prep_photo.py
Prepares a source photo for ASCII conversion:
1. Removes the background (isolates the subject)
2. Boosts local contrast so facial features are readable
3. Composites onto pure white (so background -> blank ASCII glyph)

Usage:
    python scripts/prep_photo.py source-photo.jpg
"""

import sys
import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep_photo(input_path: str, output_path: str = "prepped-photo.png"):
    print(f"Loading {input_path}...")
    with open(input_path, "rb") as f:
        input_bytes = f.read()

    # Step 1: Remove background -> returns PNG bytes with alpha channel
    print("Removing background (this downloads a model on first run)...")
    output_bytes = remove(input_bytes)

    # Load the result as a PIL image with transparency
    from io import BytesIO
    subject = Image.open(BytesIO(output_bytes)).convert("RGBA")

    # Step 2: Composite onto pure white background
    print("Compositing onto white background...")
    white_bg = Image.new("RGBA", subject.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, subject).convert("RGB")

    # Convert to a format OpenCV can work with (numpy array, BGR order)
    cv_image = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2BGR)

    # Step 3: Boost local contrast with CLAHE
    # CLAHE = Contrast Limited Adaptive Histogram Equalization.
    # Unlike a simple brightness/contrast slider, it enhances contrast
    # in local regions, so shadows and highlights on a face become
    # visible even if the original lighting was flat.
    print("Boosting contrast with CLAHE...")
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Step 4: Save as grayscale PNG
    result = Image.fromarray(enhanced)
    result.save(output_path)
    print(f"Saved prepped photo to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <input-photo>")
        sys.exit(1)

    input_file = sys.argv[1]
    prep_photo(input_file, output_path="prepped-photo.png")