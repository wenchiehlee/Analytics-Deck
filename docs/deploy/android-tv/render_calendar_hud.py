#!/usr/bin/env python3
"""
Dynamic HUD Generator for Home Assistant on Android TV (Solution B)
Generates an 18px rounded corner 32-bit RGBA frosted glass notification card
with the Sentinel Dog mascot and Zen Maru Gothic typography.

Multi-event mode: pass multiple event lines separated by '|' or '\n' in the
message argument. Each additional event line adds 28px to the card height.
Maximum 4 event lines; extra lines are truncated with '…'.

Usage:
    python3 render_calendar_hud.py "<title>" "<event1>|<event2>|..." "<out_path>"
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from PIL import Image, ImageDraw, ImageFont

# Layout constants
CARD_WIDTH = 480
BASE_HEIGHT = 104       # height for 1 event line
ROW_HEIGHT = 28         # extra pixels per additional event line
MAX_EVENTS = 4          # maximum displayable lines before truncation
MASCOT_X, MASCOT_Y = 16, 24
MASCOT_SIZE = 56
TEXT_X = 84
TITLE_Y = 18
FIRST_MSG_Y = 52        # y position of the first event line
BAR_LEFT = 84
BAR_RIGHT = CARD_WIDTH - 24
BAR_THICKNESS = 3
ACCENT_ICE_CYAN = (56, 189, 248)      # #38bdf8
BG_FILL = (15, 23, 42, 130)           # dark slate ~51% alpha
BORDER_FILL = (56, 189, 248, 140)
TEXT_TITLE_FILL = (56, 189, 248, 255)  # ice cyan
TEXT_MSG_FILL = (241, 245, 249, 255)   # near-white
FONT_TITLE_PT = 21
FONT_MSG_PT = 16
MAX_MSG_CHARS = 38   # per-line character limit before truncation


def _parse_event_lines(message: str) -> list[str]:
    """Split message on '|' or literal '\\n', strip each line, drop empty."""
    if "|" in message:
        lines = message.split("|")
    else:
        lines = message.replace("\\n", "\n").split("\n")
    return [l.strip() for l in lines if l.strip()]


def _truncate(text: str, max_chars: int = MAX_MSG_CHARS) -> str:
    return text if len(text) <= max_chars else text[:max_chars - 1] + "…"


def render_hud(
    title: str,
    message: str,
    out_path: str,
    font_path: str = None,
    icon_path: str = None,
    accent_color: tuple = ACCENT_ICE_CYAN,
    progress_pct: float = 0.45,
):
    """Render a multi-event frosted glass HUD PNG (Solution B).

    Args:
        title:        Header text (ice-cyan, 21pt).
        message:      One or more event lines, separated by '|' or '\\n'.
        out_path:     Destination PNG path.
        font_path:    Path to ZenMaruGothic-Bold.ttf (optional; falls back to default).
        icon_path:    Path to sentinel mascot PNG (optional).
        accent_color: RGB tuple for ice-cyan accent (default #38bdf8).
        progress_pct: Fill ratio [0..1] for the bottom progress bar.
    """
    event_lines = _parse_event_lines(message)
    n_lines = len(event_lines)

    # Truncate to MAX_EVENTS, append ellipsis marker if needed
    if n_lines > MAX_EVENTS:
        event_lines = event_lines[:MAX_EVENTS - 1] + ["…"]
        n_lines = MAX_EVENTS

    # Dynamic card height
    height = BASE_HEIGHT + max(0, n_lines - 1) * ROW_HEIGHT

    # Vertically center the mascot relative to the text content area
    # Text content spans from FIRST_MSG_Y to FIRST_MSG_Y + (n_lines-1)*ROW_HEIGHT + FONT_MSG_PT
    content_top = TITLE_Y
    content_bottom = FIRST_MSG_Y + max(0, n_lines - 1) * ROW_HEIGHT + FONT_MSG_PT
    mascot_y = max(MASCOT_Y, (content_top + content_bottom) // 2 - MASCOT_SIZE // 2)

    img = Image.new("RGBA", (CARD_WIDTH, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Background: 18px rounded corners, dark-slate translucent + ice-cyan border
    draw.rounded_rectangle(
        [(2, 2), (CARD_WIDTH - 3, height - 3)],
        radius=18,
        fill=BG_FILL,
        outline=(accent_color[0], accent_color[1], accent_color[2], 140),
        width=2,
    )

    # 2. Sentinel Dog mascot
    if icon_path and os.path.exists(icon_path):
        try:
            mascot = Image.open(icon_path).convert("RGBA").resize(
                (MASCOT_SIZE, MASCOT_SIZE), Image.Resampling.LANCZOS
            )
            img.paste(mascot, (MASCOT_X, mascot_y), mascot)
        except Exception as e:
            print(f"Warning: could not paste icon {icon_path}: {e}", file=sys.stderr)

    # 3. Typography
    font_title = None
    font_msg = None
    if font_path and os.path.exists(font_path):
        try:
            font_title = ImageFont.truetype(font_path, FONT_TITLE_PT)
            font_msg = ImageFont.truetype(font_path, FONT_MSG_PT)
        except Exception as e:
            print(f"Warning: could not load font {font_path}: {e}", file=sys.stderr)
    if not font_title:
        font_title = ImageFont.load_default()
        font_msg = ImageFont.load_default()

    # Title row
    draw.text(
        (TEXT_X, TITLE_Y),
        title.strip(),
        font=font_title,
        fill=(accent_color[0], accent_color[1], accent_color[2], 255),
    )

    # Event rows (stacked, 28px apart)
    for i, line in enumerate(event_lines):
        y = FIRST_MSG_Y + i * ROW_HEIGHT
        draw.text(
            (TEXT_X, y),
            _truncate(line),
            font=font_msg,
            fill=TEXT_MSG_FILL,
        )

    # 4. Bottom progress bar
    bar_y = height - 16
    draw.rounded_rectangle(
        [(BAR_LEFT, bar_y), (BAR_RIGHT, bar_y + BAR_THICKNESS)],
        radius=2,
        fill=(accent_color[0], accent_color[1], accent_color[2], 60),
    )
    active_w = int((BAR_RIGHT - BAR_LEFT) * max(0.05, min(1.0, progress_pct)))
    draw.rounded_rectangle(
        [(BAR_LEFT, bar_y), (BAR_LEFT + active_w, bar_y + BAR_THICKNESS)],
        radius=2,
        fill=(accent_color[0], accent_color[1], accent_color[2], 255),
    )

    # 5. Save
    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    img.save(out_path, "PNG")

    # Mirror as calendar.png (legacy alias)
    if out_path.endswith("calendar_event.png"):
        cal_path = out_path.replace("calendar_event.png", "calendar.png")
        try:
            img.save(cal_path, "PNG")
        except Exception:
            pass

    print(
        f"Rendered HUD [{CARD_WIDTH}x{height}] -> {out_path} "
        f"({n_lines} event line(s) | title='{title}')"
    )


def main():
    title    = sys.argv[1] if len(sys.argv) > 1 else "今日行程提醒 📅"
    message  = sys.argv[2] if len(sys.argv) > 2 else "今日行程 ⏰"
    out_path = sys.argv[3] if len(sys.argv) > 3 else "/config/www/ux-deck/huds/calendar_event.png"

    # Search for font and mascot in candidate directories
    candidate_dirs = [
        "/config/www/ux-deck",
        "/config/scripts",
        os.path.join(os.path.dirname(__file__), "..", "..", "www", "ux-deck"),
        os.path.join(os.path.dirname(__file__), "huds"),
        os.path.dirname(__file__),
        "deploy/android-tv",
        ".",
    ]

    font_path = None
    for d in candidate_dirs:
        candidate = os.path.join(d, "ZenMaruGothic-Bold.ttf")
        if os.path.exists(candidate):
            font_path = candidate
            break

    icon_path = None
    for d in candidate_dirs:
        for icon_name in ["sentinel_mascot_amber.png", "sentinel_mascot_clean.png", "sentinel_icon.png"]:
            candidate = os.path.join(d, icon_name)
            if os.path.exists(candidate):
                icon_path = candidate
                break
        if icon_path:
            break

    render_hud(
        title=title,
        message=message,
        out_path=out_path,
        font_path=font_path,
        icon_path=icon_path,
    )


if __name__ == "__main__":
    main()
