# 整体流程

1. 申请 Spotify 开发者应用（拿到 Client ID/Secret，设置 Redirect URI）
2. 在本地跑一次授权脚本，拿到 Refresh Token
3. 把 Client ID/Secret/Refresh Token 放进 GitHub Secrets

--------

下面步骤不进行详细论述

4. 把生成 SVG 的 Python 脚本放进仓库
5. 将yml文件放进 `.github/workflows/` 目录（Actions 定时跑）
6. 将生成在 spotify-top.svg 的文件引用到 README.md 里


## 1. Spotify 开发者配置

* 进 [Spotify Developer Dashboard] → Create app
* 记下 Client ID 和 Client Secret
* 在应用设置里添加 Redirect URI：http://localhost:8888/callback（本地换其他端口也行）

## 2. 本地跑授权脚本拿 Refresh Token 
Refresh Token是必须的，但并不一定要用该种方式获取，也可选用其他方法

```python
# file: get_spotify_refresh_token.py
# pip install spotipy
import os
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID") or input("CLIENT_ID: ").strip()
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET") or input("CLIENT_SECRET: ").strip()
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI") or "http://localhost:8888/callback"

scope = "user-top-read"

oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=scope,
    open_browser=True,  # 会打开浏览器登录
)

auth_url = oauth.get_authorize_url()
print("Open this URL in your browser and authorize:\n", auth_url)

response_url = input("\nAfter granting access, paste the full redirect URL here:\n").strip()
code = oauth.parse_response_code(response_url)
token_info = oauth.get_access_token(code)

refresh_token = token_info.get("refresh_token")
print("\nYour REFRESH TOKEN:\n", refresh_token)
```

## 3. 设置 参数

在 GitHub 仓库的 Settings → Secrets and variables → Actions 里添加以下 Secrets 和 Variables：

| 参数名称              | 是否必要        | 作用                                                         |
| --------------------- | --------------- | ------------------------------------------------------------ |
| SPOTIFY_CLIENT_ID     | 是（Secrets）   | 用于标识 Spotify 应用的唯一 ID                               |
| SPOTIFY_CLIENT_SECRET | 是（Secrets）   | 用于与 Spotify 进行安全通信的密钥，配合 Client ID 获取访问令牌 |
| SPOTIFY_REFRESH_TOKEN | 是（Secrets）   | 用于刷新访问令牌（Access Token），保证接口长期可用           |
|                       |                 |                                                              |
| SPOTIFY_TIME_RANGE    | 否（Variables） | 指定获取数据的时间范围（如 short_term、medium_term、long_term） |
| SPOTIFY_LIMIT         | 否（Variables） | 指定返回结果的数量上限（如前 10 首歌）                       |



