# -*- coding: utf-8 -*-
"""本地预览服务器：python serve.py [端口]

绑定所有网卡，同一 Wi-Fi 下手机也能打开（http://<电脑IP>:8710）。
"""
from __future__ import annotations

import http.server
import os
import socket
import socketserver
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"


def lan_ips() -> list[str]:
    ips = []
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if ip not in ips and not ip.startswith("127."):
                ips.append(ip)
    except OSError:
        pass
    if not ips:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ips.append(s.getsockname()[0])
            s.close()
        except OSError:
            pass
    return ips


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SITE), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):  # noqa: A003
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8710
    os.chdir(SITE)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("0.0.0.0", port), Handler) as httpd:
        print(f"本机：  http://127.0.0.1:{port}/")
        for ip in lan_ips():
            print(f"手机：  http://{ip}:{port}/   （同一 Wi-Fi 下打开）")
        print("按 Ctrl+C 停止。")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止。")


if __name__ == "__main__":
    main()
