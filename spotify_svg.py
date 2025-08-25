# file: scripts/spotify_svg.py
# pip install requests
import os, requests, html, datetime, pathlib

TOKEN_URL = "https://accounts.spotify.com/api/token"
TOP_URL = "https://api.spotify.com/v1/me/top/tracks"

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")
TIME_RANGE = os.getenv("SPOTIFY_TIME_RANGE", "short_term")  # short_term / medium_term / long_term
LIMIT = int(os.getenv("SPOTIFY_LIMIT", "5"))

def get_access_token():
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    r = requests.post(TOKEN_URL, data=data, timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]

def fetch_top_tracks(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"limit": LIMIT, "time_range": TIME_RANGE}
    r = requests.get(TOP_URL, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.json()["items"]

def time_range_label(tr):
    return {
        "short_term": "Last 4 weeks",
        "medium_term": "Last 6 months",
        "long_term": "Last year",
    }.get(tr, tr)

def build_svg(tracks):
    # 基础尺寸
    width = 720
    row_h = 36
    padding_top = 100
    padding_side = 24
    gap = 12
    height = padding_top + len(tracks) * (row_h + gap) + 36

    # 主题色/样式（简洁风）
    bg = "#0d1117"
    card = "#161b22"
    title = "#c9d1d9"
    subtitle = "#8b949e"
    text = "#e6edf3"
    accent = "#58a6ff"
    bar_bg = "#30363d"

    # 计算条形长度（按排名衰减，非真实播放量）
    max_bar = width - padding_side * 2 - 160
    lengths = []
    for i in range(len(tracks)):
        # 简单权重：1.0, 0.88, 0.76, ...
        w = 1 - i * 0.12
        if w < 0.3: w = 0.3
        lengths.append(int(max_bar * w))

    def esc(s): return html.escape(s, quote=True)

    # Header
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    tr_label = time_range_label(TIME_RANGE)

    svg_parts = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Spotify Top Tracks">',
        f'<style><![CDATA['
        f'text{{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Ubuntu,Helvetica Neue,Arial,Noto Sans,sans-serif}}'
        f']]></style>',
        f'<rect width="{width}" height="{height}" rx="16" fill="{bg}"/>',
        f'<rect x="8" y="8" width="{width-16}" height="{height-16}" rx="14" fill="{card}" stroke="{bar_bg}"/>',
        f'<text x="{padding_side}" y="40" font-size="20" fill="{title}" font-weight="600">Top Spotify Tracks</text>',
        f'<text x="{padding_side}" y="64" font-size="13" fill="{subtitle}">{esc(tr_label)} · Updated {esc(now)}</text>',
    ]

    # Rows
    y = padding_top
    for i, (track, L) in enumerate(zip(tracks, lengths), start=1):
        name = esc(track["name"])
        artists = ", ".join(esc(a["name"]) for a in track["artists"])
        url = track["external_urls"]["spotify"]

        # Rank circle
        svg_parts += [
            f'<circle cx="{padding_side+12}" cy="{y-10}" r="11" fill="{accent}"/>',
            f'<text x="{padding_side+12}" y="{y-6}" text-anchor="middle" font-size="12" fill="#0d1117" font-weight="700">{i}</text>'
        ]

        # Title (name - artist)
        svg_parts += [
            f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">'
            f'<text x="{padding_side+32}" y="{y}" font-size="14" fill="{text}" font-weight="600">{name}</text>'
            f'</a>',
            f'<text x="{padding_side+32}" y="{y+18}" font-size="12" fill="{subtitle}">{artists}</text>',
        ]

        # Bar
        bar_x = padding_side + 32
        bar_y = y + 24
        svg_parts += [
            f'<rect x="{bar_x}" y="{bar_y}" width="{max_bar}" height="8" rx="4" fill="{bar_bg}"/>',
            f'<rect x="{bar_x}" y="{bar_y}" width="{L}" height="8" rx="4" fill="{accent}"/>',
        ]

        y += row_h + gap

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)

def main():
    token = get_access_token()
    tracks = fetch_top_tracks(token)
    svg = build_svg(tracks)

    out_dir = pathlib.Path("assets")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "spotify-top.svg"
    out_path.write_text(svg, encoding="utf-8")
    print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()
