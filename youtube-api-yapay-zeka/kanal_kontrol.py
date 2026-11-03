#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Son kontrol: bağlanan kanal doğru mu, veriler okunabiliyor mu?

Kullanım:
    python3 kanal_kontrol.py client_secret.json token.json

Kanalın adını, son 5 videosunu (Data API) ve son 28 günün izlenme sayısını (Analytics API) yazar.
Hiçbir şey değiştirmez, yalnız okur. Gizli değerler ekrana basılmaz.
"""
import datetime
import json
import sys
import urllib.parse
import urllib.request


def erisim_anahtari(istemci, token):
    c = json.load(open(istemci))["installed"]
    t = json.load(open(token))
    d = urllib.parse.urlencode({"client_id": c["client_id"], "client_secret": c["client_secret"],
                                "refresh_token": t["refresh_token"], "grant_type": "refresh_token"}).encode()
    return json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", d, timeout=30))["access_token"]


def getir(url, anahtar):
    r = urllib.request.Request(url, headers={"Authorization": "Bearer " + anahtar})
    return json.load(urllib.request.urlopen(r, timeout=30))


def main():
    if len(sys.argv) != 3:
        print(__doc__); return 1
    a = erisim_anahtari(sys.argv[1], sys.argv[2])
    k = getir("https://www.googleapis.com/youtube/v3/channels?part=snippet,contentDetails&mine=true", a)["items"][0]
    print("Kanal:", k["snippet"]["title"])
    liste = k["contentDetails"]["relatedPlaylists"]["uploads"]
    v = getir("https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=5&playlistId=" + liste, a)
    print("\nSon videolar (Data API):")
    for x in v.get("items", []):
        print(" -", x["snippet"]["publishedAt"][:10], x["snippet"]["title"])
    bit = datetime.date.today()
    bas = bit - datetime.timedelta(days=28)
    s = getir("https://youtubeanalytics.googleapis.com/v2/reports?" + urllib.parse.urlencode(
        {"ids": "channel==MINE", "startDate": bas.isoformat(), "endDate": bit.isoformat(), "metrics": "views"}), a)
    goruntulenme = (s.get("rows") or [[0]])[0][0]
    print(f"\nSon 28 gün izlenme (Analytics API): {goruntulenme}")
    print("\nTamam: kanal doğru ve veriler okunabiliyor.")


if __name__ == "__main__":
    sys.exit(main())
