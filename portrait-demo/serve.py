"""零依赖教学入口：python serve.py。只监听本机。"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

if __name__ == '__main__':
    root = Path(__file__).parent / 'web'
    server = ThreadingHTTPServer(('127.0.0.1', 8765), partial(SimpleHTTPRequestHandler, directory=str(root)))
    print('打开 http://127.0.0.1:8765 ，按 Ctrl+C 退出。', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
