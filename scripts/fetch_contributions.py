"""
fetch_contributions.py
Scrapes your public GitHub contribution calendar (no token needed) from
https://github.com/users/<username>/contributions and saves the parsed
data + derived stats to data/contributions.json.

Usage:
    python scripts/fetch_contributions.py
"""

import json
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

GITHUB_USERNAME = "lauv22"
OUTPUT_PATH = "data/contributions.json"


def fetch_contribution_html(username: str) -> str:
    url = f"https://github.com/users/{username}/contributions"
    headers = {"User-Agent": "Mozilla/5.0 (profile-readme-script)"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.text


def parse_contributions(html: str) -> list[dict]:
    """Parses the day cells from the contribution calendar HTML fragment."""
    soup = BeautifulSoup(html, "html.parser")
    days = []

    # GitHub renders each day as a <td> with a data-date and data-level attribute
    cells = soup.select("td.ContributionCalendar-day")
    for cell in cells:
        date_str = cell.get("data-date")
        level_str = cell.get("data-level")
        if not date_str or level_str is None:
            continue
        days.append({
            "date": date_str,
            "level": int(level_str),
        })

    return days


def compute_stats(days: list[dict]) -> dict:
    """Derives current streak, longest streak, best day, and monthly totals."""
    # Note: this scrape doesn't give exact counts, only levels (0-4).
    # We treat level > 0 as "contributed that day" for streak purposes.
    days_sorted = sorted(days, key=lambda d: d["date"])

    current_streak = 0
    longest_streak = 0
    running = 0
    best_day = None
    best_level = -1
    monthly_totals: dict[str, int] = {}

    for day in days_sorted:
        level = day["level"]
        month_key = day["date"][:7]  # YYYY-MM
        monthly_totals[month_key] = monthly_totals.get(month_key, 0) + level

        if level > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

        if level > best_level:
            best_level = level
            best_day = day["date"]

    # Current streak = trailing run of contributed days up to the most recent day
    for day in reversed(days_sorted):
        if day["level"] > 0:
            current_streak += 1
        else:
            break

    total_contributions = sum(d["level"] for d in days_sorted)

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": monthly_totals,
        "total_level_sum": total_contributions,
    }


if __name__ == "__main__":
    print(f"Fetching contribution calendar for {GITHUB_USERNAME}...")
    html = fetch_contribution_html(GITHUB_USERNAME)

    print("Parsing days...")
    days = parse_contributions(html)
    print(f"Parsed {len(days)} days")

    print("Computing stats...")
    stats = compute_stats(days)

    output = {
        "username": GITHUB_USERNAME,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
        "stats": stats,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Saved {OUTPUT_PATH}")
    print(f"Current streak: {stats['current_streak']} days")
    print(f"Longest streak: {stats['longest_streak']} days")
