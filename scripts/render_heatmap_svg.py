"""
render_heatmap_svg.py
Renders data/contributions.json as a 53-week x 7-day GitHub-style
contribution heatmap, with boxes sliding in diagonally on load.

Usage:
    python scripts/render_heatmap_svg.py
"""

import json
from datetime import datetime

INPUT_PATH = "data/contributions.json"
OUTPUT_PATH = "contrib-heatmap.svg"

# none -> brightest (level 5 is a neon top end, purely decorative flourish)
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

BOX_SIZE = 11
BOX_GAP = 3
CELL = BOX_SIZE + BOX_GAP

LEFT_PADDING = 30   # room for day-of-week labels
TOP_PADDING = 20     # room for month labels
BOTTOM_PADDING = 40  # room for legend + stats footer

WEEKS = 53
DAYS = 7

ANIM_DURATION = 0.4
ANIM_STAGGER = 0.012  # per diagonal step


def load_data() -> dict:
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_week_grid(days: list[dict]) -> list[list[dict | None]]:
    """
    Arranges days into a 53-column x 7-row grid, GitHub style:
    columns = weeks, rows = day-of-week (0=Sunday .. 6=Saturday).
    """
    parsed = []
    for d in days:
        date_obj = datetime.strptime(d["date"], "%Y-%m-%d")
        parsed.append((date_obj, d["level"]))
    parsed.sort(key=lambda x: x[0])

    if not parsed:
        return []

    # Find the Sunday on/before the first date to align the grid
    first_date = parsed[0][0]
    start_offset = (first_date.weekday() + 1) % 7  # convert Mon=0 -> Sun=0 system
    grid: list[list[dict | None]] = [[None] * DAYS for _ in range(WEEKS)]

    col = 0
    row = start_offset
    for date_obj, level in parsed:
        if row == DAYS:
            row = 0
            col += 1
        if col >= WEEKS:
            break
        grid[col][row] = {"date": date_obj, "level": level}
        row += 1

    return grid


def month_labels(grid: list[list[dict | None]]) -> list[tuple[int, str]]:
    """Returns (week_column_index, month_name) for columns where a new month starts."""
    labels = []
    last_month = None
    for col_index, week in enumerate(grid):
        for cell in week:
            if cell is None:
                continue
            month = cell["date"].strftime("%b")
            if month != last_month:
                labels.append((col_index, month))
                last_month = month
            break
    return labels


def build_svg(data: dict) -> str:
    grid = build_week_grid(data["days"])
    stats = data["stats"]

    svg_width = LEFT_PADDING + WEEKS * CELL + 20
    svg_height = TOP_PADDING + DAYS * CELL + BOTTOM_PADDING

    box_elements = []
    diag_index_max = 0
    for col in range(len(grid)):
        for row in range(DAYS):
            cell = grid[col][row]
            level = cell["level"] if cell else 0
            level = min(level, len(PALETTE) - 1)
            color = PALETTE[level]

            x = LEFT_PADDING + col * CELL
            y = TOP_PADDING + row * CELL
            diag_index = col + row  # diagonal stagger key
            diag_index_max = max(diag_index_max, diag_index)
            delay = diag_index * ANIM_STAGGER

            title = f"{cell['date'].strftime('%b %d, %Y')}" if cell else ""

            box_elements.append(f'''
    <rect x="{x}" y="{y - 8}" width="{BOX_SIZE}" height="{BOX_SIZE}" rx="2"
          fill="{color}" opacity="0">
      <title>{title}</title>
      <animate attributeName="opacity" from="0" to="1"
               begin="{delay}s" dur="{ANIM_DURATION}s" fill="freeze" />
      <animate attributeName="y" from="{y - 8}" to="{y}"
               begin="{delay}s" dur="{ANIM_DURATION}s" fill="freeze" calcMode="linear" />
    </rect>''')

    month_elements = []
    for col_index, month in month_labels(grid):
        x = LEFT_PADDING + col_index * CELL
        month_elements.append(
            f'<text x="{x}" y="{TOP_PADDING - 6}" font-family="monospace" '
            f'font-size="10" fill="#8b949e">{month}</text>'
        )

    legend_y = TOP_PADDING + DAYS * CELL + 18
    legend_elements = [
        f'<text x="{LEFT_PADDING}" y="{legend_y}" font-family="monospace" '
        f'font-size="10" fill="#8b949e">Less</text>'
    ]
    lx = LEFT_PADDING + 35
    for color in PALETTE:
        legend_elements.append(
            f'<rect x="{lx}" y="{legend_y - 10}" width="{BOX_SIZE}" height="{BOX_SIZE}" '
            f'rx="2" fill="{color}" />'
        )
        lx += CELL
    legend_elements.append(
        f'<text x="{lx + 4}" y="{legend_y}" font-family="monospace" '
        f'font-size="10" fill="#8b949e">More</text>'
    )

    stats_y = legend_y + 20
    stats_text = (
        f"Current streak: {stats['current_streak']}d  |  "
        f"Longest streak: {stats['longest_streak']}d"
    )
    stats_element = (
        f'<text x="{LEFT_PADDING}" y="{stats_y}" font-family="monospace" '
        f'font-size="11" fill="#c9d1d9">{stats_text}</text>'
    )

    svg = f'''<svg viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}"
     xmlns="http://www.w3.org/2000/svg">
  <rect width="{svg_width}" height="{svg_height}" fill="transparent" />
{"".join(month_elements)}
{"".join(box_elements)}
  {"".join(legend_elements)}
  {stats_element}
</svg>'''
    return svg


if __name__ == "__main__":
    print("Loading contributions data...")
    data = load_data()

    print("Building heatmap SVG...")
    svg_content = build_svg(data)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"Saved {OUTPUT_PATH}")