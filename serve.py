#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
no-cache 정적 서버 + 강제 갱신 엔드포인트.
- 모든 응답에 Cache-Control: no-store (모바일 캐시 방지)
- GET /refresh  → fetch_news.py 를 즉시 1회 실행하고 결과(JSON) 반환 (페이지의 갱신 버튼용)

사용:  python3 serve.py            # 0.0.0.0:8001
       python3 serve.py 8002
"""
import sys
import os
import json
import time
import threading
import subprocess
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
HERE = os.path.dirname(os.path.abspath(__file__))
MARKET_JS = os.path.join(HERE, "market-data.js")
MARKET_MIN_AGE = 900          # 15분 — 이보다 신선하면 수집 안 함(차단 방지 겸)
_market_lock = threading.Lock()


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/refresh":
            self.handle_refresh()
            return
        if path == "/refresh-markets":
            self.handle_refresh_markets()
            return
        super().do_GET()

    def handle_refresh_markets(self):
        """시장 데이터가 15분 이상 묵었을 때만 fetch_markets.py 실행.
           클라이언트가 열 때 호출 → 신선하면 즉시 응답(수집 안 함)."""
        result = {"ok": True, "fresh": False}
        try:
            age = (time.time() - os.path.getmtime(MARKET_JS)
                   if os.path.exists(MARKET_JS) else 1e9)
            if age < MARKET_MIN_AGE:
                result["age_sec"] = int(age)          # 아직 신선 → 그대로 사용
            elif not _market_lock.acquire(blocking=False):
                result["busy"] = True                  # 다른 요청이 수집 중
            else:
                try:
                    r = subprocess.run(
                        [sys.executable, os.path.join(HERE, "fetch_markets.py")],
                        cwd=HERE, capture_output=True, text=True, timeout=300)
                    result["fresh"] = result["ok"] = (r.returncode == 0)
                finally:
                    _market_lock.release()
        except Exception as e:
            result = {"ok": False, "error": str(e)}
        body = json.dumps(result).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def handle_refresh(self):
        """auto_update.sh 즉시 실행 (fetch 수집 + Grok 번역). 수 분 소요."""
        result = {"ok": False}
        try:
            r = subprocess.run(
                ["/bin/bash", os.path.join(HERE, "auto_update.sh")],
                cwd=HERE, capture_output=True, text=True, timeout=900,
            )
            result["ok"] = (r.returncode == 0)
            tail = (r.stdout or "").strip().splitlines()
            result["log"] = tail[-3:] if tail else []
        except subprocess.TimeoutExpired:
            result["error"] = "시간 초과(15분)"
        except Exception as e:
            result["error"] = str(e)
        body = json.dumps(result, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass  # 로그 소음 줄이기


if __name__ == "__main__":
    ThreadingHTTPServer.allow_reuse_address = True
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"no-cache 서버 + /refresh 실행: http://0.0.0.0:{PORT}  (Ctrl+C 종료)")
    srv.serve_forever()
