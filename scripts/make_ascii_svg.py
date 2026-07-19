"""
make_ascii_svg.py
Converts prepped-photo.png into a monochrome ASCII art SVG that
"types" itself in row by row when viewed (via SMIL animation).

Usage:
    python scripts/make_ascii_svg.py
"""

from PIL import Image

# Bright (sparse) -> dark (dense). Leading space clears background to nothing.
RAMP = " .`:-=+*cs#%@"

# Grid size: wide enough for detail, narrow enough to stay a readable "portrait"
GRID_WIDTH = 100
GRID_HEIGHT = 53

# Monospace character cell size in the SVG (in px)
CHAR_WIDTH = 7
CHAR_HEIGHT = 12

FILL_COLOR = "#c9d1d9"   # light gray, GitHub dark-mode-friendly monochrome
ROW_STAGGER = 0.05        # seconds between each row starting to type
TYPE_DURATION = 0.6       # seconds each row takes to fully type in


def image_to_ascii_grid(image_path: str) -> list[str]:
    img = Image.open(image_path).convert("L")  # grayscale
    img = img.resize((GRID_WIDTH, GRID_HEIGHT))

    rows = []
    for y in range(GRID_HEIGHT):
        row_chars = []
        for x in range(GRID_WIDTH):
            brightness = img.getpixel((x, y))  # 0 = black, 255 = white
            # Invert: bright pixel (white/background) -> low ramp index (space)
            #         dark pixel (face/subject) -> high ramp index (dense char)
            inverted = 255 - brightness
            ramp_index = int((inverted / 255) * (len(RAMP) - 1))
            row_chars.append(RAMP[ramp_index])
        rows.append("".join(row_chars))
    return rows


def escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_svg(rows: list[str]) -> str:
    svg_width = GRID_WIDTH * CHAR_WIDTH
    svg_height = GRID_HEIGHT * CHAR_HEIGHT

    row_elements = []
    for i, row_text in enumerate(rows):
        y_pos = (i + 1) * CHAR_HEIGHT
        start_time = i * ROW_STAGGER

        # Each row is clipped by a rectangle that animates its width
        # from 0 to full, creating the left-to-right "typing" wipe.
        clip_id = f"clip-row-{i}"
        row_elements.append(f'''
    <clipPath id="{clip_id}">
      <rect x="0" y="{y_pos - CHAR_HEIGHT}" width="0" height="{CHAR_HEIGHT}">
        <animate attributeName="width" from="0" to="{svg_width}"
                 begin="{start_time}s" dur="{TYPE_DURATION}s"
                 fill="freeze" calcMode="linear" />
      </rect>
    </clipPath>''')

    text_elements = []
    for i, row_text in enumerate(rows):
        y_pos = (i + 1) * CHAR_HEIGHT
        clip_id = f"clip-row-{i}"
        safe_text = escape_xml(row_text)
        text_elements.append(
            f'    <text x="0" y="{y_pos - 2}" clip-path="url(#{clip_id})" '
            f'font-family="monospace" font-size="{CHAR_HEIGHT}" '
            f'fill="{FILL_COLOR}" xml:space="preserve">{safe_text}</text>'
        )

    svg = f'''<svg viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}"
     xmlns="http://www.w3.org/2000/svg">
  <defs>{"".join(row_elements)}
  </defs>
  <rect width="{svg_width}" height="{svg_height}" fill="transparent" />
{chr(10).join(text_elements)}
</svg>'''
    return svg


if __name__ == "__main__":
    print("Reading prepped-photo.png...")
    rows = image_to_ascii_grid("prepped-photo.png")

    print("Building SVG...")
    svg_content = build_svg(rows)

    output_path = "avi-ascii.svg"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"Saved {output_path} ({GRID_WIDTH}x{GRID_HEIGHT} grid)")