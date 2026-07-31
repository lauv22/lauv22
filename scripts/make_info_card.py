"""
make_info_card.py
Hand-authored neofetch-style info panel that fades in line by line.
Edit the CONTENT dict below with your own details.

Usage:
    python scripts/make_info_card.py
    STATIC=1 python scripts/make_info_card.py   # frozen frame, no animation
"""

import os

# ---- EDIT THIS SECTION WITH YOUR OWN INFO ----
CONTENT = {
    "user": "roshan@github",
    "now": "BCA Student · ML/AI Intern @ Codesparks Technology",
    "prev": "",
    "location": "Birtamode, Nepal",
    "stack": "Python · Java · C · .NET · PyTorch · scikit-learn · XGBoost · OpenCV · pandas · numpy · Flask",
    "highlights": [
        "Face Recognition Attendance System — Flask + DeepFace, real-time webcam-based attendance, Dockerized",
        "Cardiovascular Risk Predictor — XGBoost model trained on 300K+ patient records, Flask web app",
        "Plainly (Text Simplifier) — converts AI-generated text into human-written style using a local LLM",
        "OCR Document Classifier — extracts and classifies Passport/Citizenship/PAN/National ID fields via Tesseract OCR",
    ],
}
# ------------------------------------------------

WIDTH = 490
HEIGHT = 420
BG_COLOR = "#0d1117"       # GitHub dark terminal background
BORDER_COLOR = "#30363d"
TITLE_BAR_COLOR = "#161b22"
LABEL_COLOR = "#58a6ff"    # blue, like neofetch field labels
VALUE_COLOR = "#c9d1d9"    # light gray body text
ACCENT_COLOR = "#39d353"   # green accent (matches heatmap top color)

LINE_HEIGHT = 24
FADE_DURATION = 0.4
LINE_STAGGER = 0.15

STATIC = os.environ.get("STATIC") == "1"


def escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def fade_in_attrs(index: int) -> str:
    """Returns the animate/opacity setup for a line, or static full-opacity if STATIC=1."""
    if STATIC:
        return ""
    delay = 0.3 + index * LINE_STAGGER
    return (
        f'<animate attributeName="opacity" from="0" to="1" '
        f'begin="{delay}s" dur="{FADE_DURATION}s" fill="freeze" />'
        f'<animate attributeName="transform" '
        f'values="translate(-8,0);translate(0,0)" '
        f'begin="{delay}s" dur="{FADE_DURATION}s" fill="freeze" calcMode="linear" />'
    )


def build_lines() -> list[str]:
    """Builds the list of (label, value) content lines from CONTENT."""
    lines = [("now", CONTENT["now"])]
    if CONTENT.get("prev"):
        lines.append(("prev", CONTENT["prev"]))
    if CONTENT.get("location"):
        lines.append(("location", CONTENT["location"]))
    if CONTENT.get("focus"):
        lines.append(("focus", CONTENT["focus"]))
    lines.append(("stack", CONTENT["stack"]))
    for i, h in enumerate(CONTENT["highlights"]):
        label = "highlights" if i == 0 else ""
        lines.append((label, h))
    return lines


def build_svg() -> str:
    lines = build_lines()
    start_opacity = "1" if STATIC else "0"

    text_elements = []
    y = 70
    for i, (label, value) in enumerate(lines):
        group_transform = "translate(0,0)" if STATIC else "translate(-8,0)"
        anim = fade_in_attrs(i)
        label_span = (
            f'<tspan fill="{LABEL_COLOR}" font-weight="bold">{escape_xml(label)}:</tspan> '
            if label else ""
        )
        text_elements.append(f'''
    <g opacity="{start_opacity}" transform="{group_transform}">
      {anim}
      <text x="24" y="{y}" font-family="monospace" font-size="14" fill="{VALUE_COLOR}" xml:space="preserve">{label_span}{escape_xml(value)}</text>
    </g>''')
        y += LINE_HEIGHT

    svg = f'''<svg viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}"
     xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" rx="8" fill="{BG_COLOR}" stroke="{BORDER_COLOR}" stroke-width="1" />

  <rect x="0" y="0" width="{WIDTH}" height="36" rx="8" fill="{TITLE_BAR_COLOR}" />
  <rect x="0" y="28" width="{WIDTH}" height="8" fill="{TITLE_BAR_COLOR}" />
  <circle cx="20" cy="18" r="6" fill="#ff5f56" />
  <circle cx="40" cy="18" r="6" fill="#ffbd2e" />
  <circle cx="60" cy="18" r="6" fill="#27c93f" />
  <text x="{WIDTH/2}" y="23" font-family="monospace" font-size="13" fill="{VALUE_COLOR}" text-anchor="middle">neofetch</text>

  <text x="24" y="56" font-family="monospace" font-size="15" font-weight="bold" fill="{ACCENT_COLOR}">{escape_xml(CONTENT["user"])}</text>
  <line x1="24" y1="62" x2="{WIDTH-24}" y2="62" stroke="{BORDER_COLOR}" stroke-width="1" />

{"".join(text_elements)}
</svg>'''
    return svg


if __name__ == "__main__":
    svg_content = build_svg()
    output_path = "info-card.svg"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    mode = "static" if STATIC else "animated"
    print(f"Saved {output_path} ({mode})")