import os, requests, html, datetime, pathlib

# ===================== 配置 =====================
TOKEN_URL = "https://accounts.spotify.com/api/token"
TOP_URL = "https://api.spotify.com/v1/me/top/tracks"
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")
TIME_RANGE = os.getenv("SPOTIFY_TIME_RANGE", "short_term")
LIMIT = int(os.getenv("SPOTIFY_LIMIT", "5"))

# 定义多种风格
STYLES = [
    # ===================== 颜色风格 =====================
    {
        "name": "blue",
        "bg": "#0d1117",
        "card": "#161b22",
        "title": "#c9d1d9",
        "subtitle": "#8b949e",
        "text": "#e6edf3",
        "accent": "#58a6ff",
        "bar_bg": "#30363d"
    },
    {
        "name": "green",
        "bg": "#0d1117",
        "card": "#161b22",
        "title": "#c9d1d9",
        "subtitle": "#8b949e",
        "text": "#e6edf3",
        "accent": "#1D8348",
        "bar_bg": "#A9DFBF"
    },
    {
        "name": "warm",
        "bg": "#1c1c1c",
        "card": "#2e2e2e",
        "title": "#f5f5f5",
        "subtitle": "#b0b0b0",
        "text": "#e0e0e0",
        "accent": "#ff6f61",
        "bar_bg": "#ffcccb"
    },
    {
        "name": "purple",
        "bg": "#0d0d1a",
        "card": "#1b1b2f",
        "title": "#d0c0ff",
        "subtitle": "#b0a0ff",
        "text": "#e0dfff",
        "accent": "#a070ff",
        "bar_bg": "#3a3a50"
    },
]

# ===================== 功能函数 =====================
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
    return {"short_term": "Last 4 weeks",
            "medium_term": "Last 6 months",
            "long_term": "Last year"}.get(tr, tr)

def esc(s): return html.escape(s, quote=True)

# ===================== 修改1: 新增 size 参数 =====================
def build_svg(tracks, style, size="medium"):
    if size == "small":
        width = 360   # 小卡片宽度
    elif size == "large":
        width = 1080  # 占满整行
    else:
        width = 720   # 默认中等大小

    row_h = 36
    padding_top = 100
    padding_side = 24
    gap = 12
    height = padding_top + len(tracks)*(row_h+gap)+36

    max_bar = width - padding_side*2 - 160
    lengths = []
    for i in range(len(tracks)):
        w = 1 - i*0.12
        if w < 0.3: w = 0.3
        lengths.append(int(max_bar * w))

    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    tr_label = time_range_label(TIME_RANGE)

    svg_parts = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
        f'<style><![CDATA[text{{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Ubuntu,Helvetica Neue,Arial,Noto Sans,sans-serif}}]]></style>',
        f'<rect width="{width}" height="{height}" rx="16" fill="{style["bg"]}"/>',
        f'<rect x="8" y="8" width="{width-16}" height="{height-16}" rx="14" fill="{style["card"]}" stroke="{style["bar_bg"]}"/>',
        f'<text x="{padding_side}" y="40" font-size="20" fill="{style["title"]}" font-weight="600">Top Spotify Tracks</text>',
        f'<text x="{padding_side}" y="64" font-size="13" fill="{style["subtitle"]}">{esc(tr_label)} · Updated {esc(now)}</text>',
    ]

    y = padding_top
    for i, (track, L) in enumerate(zip(tracks, lengths), start=1):
        name = esc(track["name"])
        artists = ", ".join(esc(a["name"]) for a in track["artists"])
        url = track["external_urls"]["spotify"]

        svg_parts += [
            f'<circle cx="{padding_side+12}" cy="{y-10}" r="11" fill="{style["accent"]}"/>',
            f'<text x="{padding_side+12}" y="{y-6}" text-anchor="middle" font-size="12" fill="{style["bg"]}" font-weight="700">{i}</text>',
            f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">',
            f'<text x="{padding_side+32}" y="{y}" font-size="14" fill="{style["text"]}" font-weight="600">{name}</text>',
            f'</a>',
            f'<text x="{padding_side+32}" y="{y+18}" font-size="12" fill="{style["subtitle"]}">{artists}</text>',
            f'<rect x="{padding_side+32}" y="{y+24}" width="{max_bar}" height="8" rx="4" fill="{style["bar_bg"]}"/>',
            f'<rect x="{padding_side+32}" y="{y+24}" width="{L}" height="8" rx="4" fill="{style["accent"]}"/>',
        ]
        y += row_h + gap

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)

# ===================== 修改2: 在 main() 里生成三种大小 =====================
def main():
    token = get_access_token()
    tracks = fetch_top_tracks(token)
    out_dir = pathlib.Path("spotify-top-svgs")
    out_dir.mkdir(parents=True, exist_ok=True)

    for style in STYLES:
        for size in ["small", "medium", "large"]:  # 生成三种大小
            svg = build_svg(tracks, style, size=size)
            out_path = out_dir / f"{style['name']}_{size}.svg"
            out_path.write_text(svg, encoding="utf-8")
            print(f"Generated {out_path}")

if __name__ == "__main__":
    main()
