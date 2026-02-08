import http.server
import socket
import socketserver
import subprocess
import pyqrcode
from urllib.parse import urlparse

PORT = 8765


HTML = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>Mac Remote</title>

  <style>
    :root {{
      --bg: #f2f2f7;
      --card: #ffffff;
      --border: #d1d1d6;
      --text: #1c1c1e;
      --muted: #6e6e73;
      --btn: #f9f9fb;
      --btn-active: #e5e5ea;
    }}

    * {{
      box-sizing: border-box;
      -webkit-tap-highlight-color: transparent;
    }}

    body {{
      margin: 0;
      font-family:
        -apple-system,
        BlinkMacSystemFont,
        "SF Pro Text",
        "SF Pro Display",
        system-ui,
        sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}

    /* ---------- hint ---------- */
    .hint {{
      padding: 14px 16px;
      font-size: 14px;
      color: var(--muted);
      text-align: center;
    }}

    /* ---------- bottom controller ---------- */
    .controller {{
      margin-top: auto;
      padding: 16px;
      padding-bottom: calc(16px + env(safe-area-inset-bottom));
    }}

    .panel {{
      background: var(--card);
      border-radius: 24px;
      padding: 16px;
      box-shadow:
        0 8px 24px rgba(0, 0, 0, 0.06),
        0 1px 2px rgba(0, 0, 0, 0.04);
    }}

    .row {{
      display: flex;
      justify-content: center;
      gap: 14px;
      margin-bottom: 14px;
    }}

    .row:last-child {{
      margin-bottom: 0;
    }}

    button {{
      appearance: none;
      border: 1px solid var(--border);
      background: var(--btn);
      border-radius: 20px;
      font-size: 28px;
      width: 72px;
      height: 72px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition:
        transform 0.05s ease,
        background 0.1s ease;
    }}

    button:active {{
      transform: scale(0.97);
      background: var(--btn-active);
    }}

    .pause {{
      width: 100%;
      height: 78px;
      font-size: 32px;
      border-radius: 22px;
    }}
  </style>
</head>

<body>
  <div class="hint">
    Works if OS focus is on the video
  </div>

  <div class="controller">
    <div class="panel">
      <div class="row" content="Volume">
        <button onclick="hit('/down')">⬇︎︎</button>
        <button onclick="hit('/up')">⬆︎</button>
      </div>
      <div class="row">

        <button onclick="hit('/left')">⏪︎</button>
        <button onclick="hit('/right')">⏩︎</button>
      </div>
      <div class="row">
        <button class="pause" onclick="hit('/pause')">⏯</button>
      </div>

    </div>
  </div>

  <script>
    async function hit(path) {{
      try {{
        await fetch(path, {{ method: 'POST' }});
        navigator.vibrate?.(15);
      }} catch {{
        alert('No Mac connection');
      }}
    }}
  </script>
</body>
</html>
"""


def send_key(key_name: str):
    if key_name == "space":
        script = 'tell application "System Events" to key code 49'  # space
    elif key_name == "left":
        script = 'tell application "System Events" to key code 123'  # left arrow
    elif key_name == "right":
        script = 'tell application "System Events" to key code 124'  # right arrow
    elif key_name == "up":
        script = 'tell application "System Events" to key code 126'  # up arrow
    elif key_name == "down":
        script = 'tell application "System Events" to key code 125'  # down arrow
    else:
        raise ValueError(f"Unknown key: {key_name}")

    subprocess.run(["osascript", "-e", script], check=False)


class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, code=200, body=b"", content_type="text/plain; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/" or path == "/index.html":
            self._send(200, HTML.encode("utf-8"), "text/html; charset=utf-8")
        else:
            self._send(404, b"Not found")

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/pause":
            send_key("space")
            self._send(204)
        elif path == "/left":
            send_key("left")
            self._send(204)
        elif path == "/right":
            send_key("right")
            self._send(204)
        elif path == "/up":
            send_key("up")
            self._send(204)
        elif path == "/down":
            send_key("down")
            self._send(204)
        elif path == "/ping":
            self._send(200, b"pong")
        else:
            self._send(404, b"Not found")

    def log_message(self, format, *args):
        return

def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

def main():
    ip = get_local_ip()
    # ip = socket.gethostbyname(socket.gethostname())
    host = f"http://{ip}:{PORT}"
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Mac Remote listening on {host}/")
        print("Open it from your phone using your Mac's IP address.")
        pyqrcode.create(content=host)
        print(pyqrcode.create(content=host).terminal(module_color="white", background="black"))
        httpd.serve_forever()


if __name__ == "__main__":
    main()
