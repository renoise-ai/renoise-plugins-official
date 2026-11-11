#!/usr/bin/env python3
"""Wikimedia Commons: `search` file names (with license + date) / `get` a 1600 px copy and log author + license in assets/photo/credits.json
Usage: commons.py search "query" [N] [--full] | commons.py get "File:xxx.jpg" name   (the API rate-limits: pause a few seconds between calls)"""
import json, sys, urllib.parse, urllib.request, os
API = "https://commons.wikimedia.org/w/api.php?"
UA = {"User-Agent": "vox-collage/1.0 (documentary research tool)"}
if not os.environ.get("SSL_CERT_FILE"):          # python.org builds on macOS have no CA store without this
    try: import certifi; os.environ["SSL_CERT_FILE"] = certifi.where()
    except ImportError: pass
def http(u, timeout):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=timeout).read()
def q(params):
    return json.loads(http(API + urllib.parse.urlencode({**params, "format": "json"}), 40))
if sys.argv[1] == "search":
    r = q({"action": "query", "generator": "search", "gsrsearch": sys.argv[2], "gsrnamespace": 6, "gsrlimit": sys.argv[3] if len(sys.argv) > 3 else 8, "prop": "imageinfo", "iiprop": "size|extmetadata", "iiextmetadatafilter": "LicenseShortName|DateTimeOriginal"})
    for p in (r.get("query", {}).get("pages", {}) or {}).values():
        ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
        print(f'{p["title"] if "--full" in sys.argv else p["title"][:80]:80} {ii["width"]}x{ii["height"]} | {m.get("LicenseShortName",{}).get("value","?")[:22]} | {str(m.get("DateTimeOriginal",{}).get("value",""))[:30]}')
else:
    title, name = sys.argv[2], sys.argv[3]
    r = q({"action": "query", "titles": title, "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 1600})
    p = list(r["query"]["pages"].values())[0]; ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
    url = ii.get("thumburl") or ii["url"]; ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower() or ".jpg"   # thumb URLs can carry a ?utm query
    os.makedirs("assets/photo", exist_ok=True); out = f"assets/photo/{name}{ext}"
    open(out, "wb").write(http(url, 90))
    cf = "assets/photo/credits.json"; c = json.load(open(cf, encoding="utf-8")) if os.path.exists(cf) else {}
    strip = lambda s: __import__("re").sub("<[^>]+>", "", s or "")
    c[name] = {"file": out, "title": title, "page": ii.get("descriptionurl"), "license": m.get("LicenseShortName", {}).get("value"), "artist": strip(m.get("Artist", {}).get("value"))[:120]}
    json.dump(c, open(cf, "w", encoding="utf-8"), ensure_ascii=False, indent=1); print(out, c[name]["license"], c[name]["artist"][:50])
