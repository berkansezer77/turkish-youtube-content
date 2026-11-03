#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""YouTube kanalını yapay zekâ ajanına bağlar (OAuth, masaüstü istemcisi).

Kullanım:
    python3 kanal_bagla.py client_secret.json token.json

1) Tarayıcıda açmanız gereken Google giriş adresini yazar.
2) Girişi ve izni SİZ verirsiniz; Google sizi bu bilgisayardaki 127.0.0.1 adresine geri yollar.
3) Gelen kodu kalıcı anahtara (refresh token) çevirir, token.json dosyasına yalnız sizin okuyabileceğiniz izinle yazar.
4) Bağlanan kanalın adını ekrana ve tarayıcıya yazar.

Yalnız Python'un kendi kütüphanelerini kullanır, ek paket gerekmez. Gizli değerler ekrana basılmaz.
client_secret.json ve token.json dosyalarını kimseyle paylaşmayın, GitHub'a koymayın.
"""
import argparse
import base64
import hashlib
import html
import http.server
import json
import os
import secrets
import sys
import urllib.parse
import urllib.request

# YouTube (yükleme, başlık, açıklama, altyazı, yorum) + Analytics/Reporting (yalnız okuma)
KAPSAM = "https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/youtube.force-ssl"


def main():
    p = argparse.ArgumentParser(description="YouTube kanalını OAuth ile bağlar")
    p.add_argument("istemci", help="Google Cloud'dan indirilen client_secret JSON dosyası")
    p.add_argument("token", help="yazılacak token dosyası, örn. token.json")
    p.add_argument("--port", type=int, default=8765)
    a = p.parse_args()
    c = json.load(open(a.istemci))["installed"]          # "Desktop app" istemcisi olmalı
    yon = f"http://127.0.0.1:{a.port}"
    dogrulayici = secrets.token_urlsafe(64)
    durum = secrets.token_urlsafe(16)
    meydan = base64.urlsafe_b64encode(hashlib.sha256(dogrulayici.encode()).digest()).rstrip(b"=").decode()
    adres = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": c["client_id"], "redirect_uri": yon, "response_type": "code", "scope": KAPSAM,
        "access_type": "offline", "prompt": "consent", "state": durum,
        "code_challenge": meydan, "code_challenge_method": "S256"})
    print("\nBu adresi tarayıcıda açın, kanalın Google hesabıyla giriş yapıp izin verin:\n\n" + adres + "\n", flush=True)
    sonuc = {}

    class Isleyici(http.server.BaseHTTPRequestHandler):
        def log_message(self, *x):
            pass

        def do_GET(self):
            q = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
            if "code" not in q and "error" not in q:
                self.send_response(404); self.end_headers(); return
            baslik, alt = "Bağlanamadı", q.get("error", "")
            if q.get("state") == durum and "code" in q:
                d = urllib.parse.urlencode({"code": q["code"], "client_id": c["client_id"], "client_secret": c["client_secret"],
                                            "redirect_uri": yon, "grant_type": "authorization_code",
                                            "code_verifier": dogrulayici}).encode()
                t = json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", d, timeout=30))
                eski = os.umask(0o077)
                with open(a.token, "w") as f:
                    json.dump({"refresh_token": t.get("refresh_token"), "scope": t.get("scope"), "token_type": t.get("token_type")}, f)
                os.umask(eski)
                r = urllib.request.Request("https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&mine=true",
                                           headers={"Authorization": "Bearer " + t["access_token"]})
                k = json.load(urllib.request.urlopen(r, timeout=30)).get("items", [{}])[0]
                sn = k.get("snippet", {})
                baslik = "Bağlandı"
                alt = f'{sn.get("title", "")} · {int(k.get("statistics", {}).get("subscriberCount", 0)):,} abone'
                sonuc.update(kanal=sn.get("title"), refresh_token_var=bool(t.get("refresh_token")), kapsam=t.get("scope"))
            sayfa = f"""<!doctype html><meta charset="utf-8"><title>Kanal bağlama</title>
<body style="margin:0;height:100vh;display:grid;place-items:center;background:#16181d;color:#f2f2f2;font:20px -apple-system,Helvetica,sans-serif">
<div style="text-align:center"><div style="font-size:40px;font-weight:700;margin:8px 0">{html.escape(baslik)}</div>
<div style="opacity:.75">{html.escape(alt)}</div><div style="opacity:.45;margin-top:28px;font-size:16px">Bu sekmeyi kapatabilirsiniz.</div></div>"""
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
            self.wfile.write(sayfa.encode())
            sonuc["bitti"] = True

    s = http.server.HTTPServer(("127.0.0.1", a.port), Isleyici)
    s.timeout = 30
    for _ in range(60):  # en çok ~30 dakika bekler
        s.handle_request()
        if sonuc.get("bitti"):
            break
    print(json.dumps(sonuc, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
