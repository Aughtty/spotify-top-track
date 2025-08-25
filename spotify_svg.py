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
    # 0. 蓝色风格, 为默认风格
    {
        "name": "blue",
        "bg": "#0d1117",  # 背景色：非常深的蓝黑色
        "card": "#161b22",  # 卡片背景色：比背景稍浅的深灰蓝色
        "title": "#c9d1d9",  # 标题文字色：浅灰白，清晰可读
        "subtitle": "#8b949e",  # 副标题文字色：中灰蓝色，用于次要信息
        "text": "#e6edf3",  # 正文文字色：接近白色，舒适易读
        "accent": "#58a6ff",  # 强调色：亮蓝色，用于按钮、链接或重点
        "bar_bg": "#30363d"  # 进度条背景色：暗灰蓝色，低调不抢眼
    },
    # 1. 经典绿色风格
    {
        "name": "green",
        "bg": "#0d1117",  # 背景色：非常深的蓝黑色
        "card": "#161b22",  # 卡片背景色：比背景稍浅的深灰蓝色
        "title": "#c9d1d9",  # 标题文字色：浅灰白，清晰可读
        "subtitle": "#8b949e",  # 副标题文字色：中灰蓝色，用于次要信息
        "text": "#e6edf3",  # 正文文字色：接近白色，舒适易读
        "accent": "#1D8348",  # 强调色：深绿色
        "bar_bg": "#A9DFBF"  # 进度条背景色：浅绿色
    },
    # 2. 暖色调风格
    {
        "name": "warm",
        "bg": "#1c1c1c",  # 背景色：深灰色
        "card": "#2e2e2e",  # 卡片背景色：稍浅的深灰色
        "title": "#f5f5f5",  # 标题文字色：接近白色
        "subtitle": "#b0b0b0",  # 副标题文字色：中灰色
        "text": "#e0e0e0",  # 正文文字色：浅灰色
        "accent": "#ff6f61",  # 强调色：珊瑚红
        "bar_bg": "#ffcccb"  # 进度条背景色：浅珊瑚红
    },
    # 3. 冷色调风格
     {
        "name": "cool",
        "bg": "#0f2027",  # 背景色：深蓝绿色
        "card": "#203a43",  # 卡片背景色：深青色
        "title": "#e0f7fa",  # 标题文字色：浅青色
        "subtitle": "#80deea",  # 副标题文字色：中浅青色
        "text": "#b2ebf2",  # 正文文字色：浅青色
        "accent": "#00acc1",  # 强调色：亮青色
        "bar_bg": "#4dd0e1"  # 进度条背景色：中浅青色

     },
    # 4. 紫色风格
    {
        "name": "purple",
        "bg": "#0d0d1a",    # 背景色：非常深的紫黑色
        "card": "#1b1b2f",  # 卡片背景色：比背景稍浅的深紫色
        "title": "#d0c0ff", # 标题文字色：浅紫色
        "subtitle": "#b0a0ff",  # 副标题文字色：中紫色
        "text": "#e0dfff",  # 正文文字色：接近白色
        "accent": "#a070ff",    # 强调色：亮紫色
        "bar_bg": "#3a3a50"     # 进度条背景色：暗紫色
    },
    # 5. 粉色风格
    {
        "name": "pink",
        "bg": "#1a0d1a",  # 背景色：非常深的粉紫色
        "card": "#2f1b2f",  # 卡片背景色：比背景稍浅的深粉色
        "title": "#ffd0e0",  # 标题文字色：浅粉色
        "subtitle": "#ffb0c0",  # 副标题文字色：中粉色
        "text": "#ffe0f0",  # 正文文字色：接近白色
        "accent": "#ff70a0",  # 强调色：亮粉色
        "bar_bg": "#503a50"  # 进度条背景色：暗粉色

    }

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

def build_svg(tracks, style):
    width = 720
    row_h = 36
    padding_top = 100
    padding_side = 24
    gap = 12
    height = padding_top + len(tracks)*(row_h+gap)+36

    # 计算条长度（按排名衰减）
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

def main():
    token = get_access_token()
    tracks = fetch_top_tracks(token)
    out_dir = pathlib.Path("assets")
    out_dir.mkdir(parents=True, exist_ok=True)

    for style in STYLES:
        svg = build_svg(tracks, style)
        out_path = out_dir / f"spotify-top-{style['name']}.svg"
        out_path.write_text(svg, encoding="utf-8")
        print(f"Generated {out_path}")

if __name__ == "__main__":
    main()
