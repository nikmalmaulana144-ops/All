#!/usr/bin/env python3
# language: Python 3.8+
# file: acx_client.py
# AlwaysCodex All-in-One Client — by malz codex
# android / termux — no root — stdlib only
# D E V E L O P E R
# Tiktok   : @ini_nikmal
# Youtube  : @Nikmal_hsb
# Github   : @ini_nikmal
# Telegram : @ini_nikmal

import os
import re
import sys
import json
import time
import random
import string
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from pathlib import Path

# ================================================================
# ANSI
# ================================================================
if os.name == "nt":
    os.system("")

R   = "\033[0m"; B = "\033[1m"; DIM = "\033[2m"
CY  = "\033[96m"; GR = "\033[92m"; YL = "\033[93m"
RD  = "\033[91m"; MG = "\033[95m"; WH = "\033[97m"; GRY = "\033[90m"

AUTHOR = "malz codex"
APP    = "ACX CLIENT"
VER    = "v2.0.0"

BASE_URL   = "https://api.alwayscodex.eu.cc"
RESULT_DIR = Path.cwd() / "result" / "acx"
CFG_FILE   = "acx_config.json"
HIST_FILE  = "acx_history.json"

try: RESULT_DIR.mkdir(parents=True, exist_ok=True)
except Exception: pass

# ================================================================
# CONFIG
# ================================================================
DEFAULT_CFG = {
    "proxies": [],
    "use_proxy": False,
    "timeout": 60,
}

def load_cfg():
    if os.path.isfile(CFG_FILE):
        try:
            with open(CFG_FILE) as f:
                cfg = json.load(f)
                for k, v in DEFAULT_CFG.items(): cfg.setdefault(k, v)
                return cfg
        except Exception: pass
    return dict(DEFAULT_CFG)

def save_cfg(cfg):
    try:
        with open(CFG_FILE, "w") as f: json.dump(cfg, f, indent=2)
        return True
    except Exception: return False

CFG = load_cfg()

# ================================================================
# UTIL
# ================================================================
def clear(): os.system("cls" if os.name == "nt" else "clear")

def width():
    try: return min(os.get_terminal_size().columns, 78)
    except OSError: return 78

def c(t, col=""): return f"{col}{t}{R}" if col else t
def line(ch="─", col=GRY): print(c(ch * width(), col))

def type_out(text, delay=0.004, col="", end="\n"):
    for ch in text:
        sys.stdout.write(c(ch, col)); sys.stdout.flush(); time.sleep(delay)
    sys.stdout.write(end)

def loading(text, seconds=1.0, col=CY):
    frames = ["|", "/", "-", "\\"]
    end = time.time() + seconds; i = 0
    while time.time() < end:
        sys.stdout.write("\r  " + c(frames[i % len(frames)], col) + "  " + text + "   ")
        sys.stdout.flush(); time.sleep(0.1); i += 1
    sys.stdout.write("\r  " + c("OK", GR) + "  " + text + "   \n")

def box(title, lines, col=CY, pad=2):
    w = width() - 2; inner = w - pad * 2
    print(c("+" + "=" * w + "+", col))
    if title:
        t = " " + title + " "
        left = max(0, (w - len(t)) // 2); right = max(0, w - len(t) - left)
        print(c("|", col) + " " * left + c(t, B + WH) + " " * right + c("|", col))
        print(c("+" + "=" * w + "+", col))
    for ln in lines:
        vis = re.sub(r"\033\[[0-9;]*m", "", ln)
        space = max(0, inner - len(vis))
        print(c("|", col) + " " * pad + ln + " " * space + " " * pad + c("|", col))
    print(c("+" + "=" * w + "+", col))

def prompt(text, col=YL):
    try: return input("  " + c(">", col) + " " + c(text, WH) + " ").strip()
    except (EOFError, KeyboardInterrupt): print(); return None

def banner():
    clear()
    print(c("  ▄▀█ █▀ █▀▄▀█ █▀▀ █▄░█", MG + B))
    print(c("  █▀█ ▄█ █░▀░█ ██▄ █░▀█", MG + B))
    print(c("  ▄▀█ █░░ █░░   █ █▄░█   █▀█ █▄░█ █▀▀", MG + B))
    print(c("  █▀█ █▄▄ █▄▄   █ █░▀█   █▄█ █░▀█ ██▄", MG + B))
    print()
    print("  " + c(APP + "  " + VER, WH + B) + c("   by ", GRY) + c(AUTHOR, MG + B))
    print("  " + c("all-in-one alwayscodex client", GRY))
    line("─", GRY)
    print()

def header(sub):
    banner()
    print("  " + c("*", MG) + " " + c(sub, WH + B))
    print()

def rand_str(n=8):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))

def rand_ip():
    return f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"

def sanitize_filename(name):
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", name or "output")
    name = re.sub(r"\s+", "_", name.strip())
    return name[:50] or "output"

# ================================================================
# PROXY
# ================================================================
_PROXY_IDX = {"i": 0}

def get_proxy():
    if not CFG.get("use_proxy"): return None
    pr = CFG.get("proxies", [])
    if not pr: return None
    p = pr[_PROXY_IDX["i"] % len(pr)]
    _PROXY_IDX["i"] += 1
    return p

# ================================================================
# REQUEST
# ================================================================
def do_request(method, endpoint, params=None, timeout=None):
    if timeout is None:
        timeout = CFG.get("timeout", 60)

    url = BASE_URL + endpoint
    if params:
        qs = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        if qs: url += ("&" if "?" in url else "?") + qs

    headers = {
        "user-agent": "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "x-forwarded-for": rand_ip(),
    }

    proxy = get_proxy()
    if proxy:
        handler = urllib.request.ProxyHandler({"http": proxy, "https": proxy})
        opener = urllib.request.build_opener(handler)
    else:
        opener = urllib.request.build_opener()

    body = None
    if method == "POST":
        body = b""

    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with opener.open(req, timeout=timeout) as resp:
            data = resp.read()
            ct = resp.headers.get("content-type", "")
            return True, data, ct, resp.status, url
    except urllib.error.HTTPError as e:
        try: data = e.read()
        except Exception: data = b""
        ct = e.headers.get("content-type", "") if e.headers else ""
        return False, data, ct, e.code, url
    except Exception as e:
        return False, str(e).encode("utf-8", "replace"), "", 0, url

# ================================================================
# RESPONSE HANDLER
# ================================================================
def extract_url_from_json(body, ct):
    """cari URL di JSON response (image / download / result)"""
    if "json" not in ct.lower():
        try: j = json.loads(body.decode("utf-8", "replace"))
        except Exception: return None
    else:
        try: j = json.loads(body.decode("utf-8", "replace"))
        except Exception: return None

    if not j: return None
    candidates = []

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and v.startswith("http"):
                    low = v.lower()
                    if any(x in low for x in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".mp3", ".apk", "download", "/file/", "cdn"]):
                        candidates.append(v)
                walk(v)
        elif isinstance(o, list):
            for it in o: walk(it)

    walk(j)
    return candidates[0] if candidates else None

def save_result(body, ct, prefix, is_json=False):
    """simpan bytes ke result/, return path"""
    ct_l = ct.lower()

    if is_json:
        ext = ".json"
    elif "jpeg" in ct_l or "jpg" in ct_l: ext = ".jpg"
    elif "png" in ct_l: ext = ".png"
    elif "webp" in ct_l: ext = ".webp"
    elif "gif" in ct_l: ext = ".gif"
    elif "mp4" in ct_l or "video" in ct_l: ext = ".mp4"
    elif "mp3" in ct_l or "audio" in ct_l: ext = ".mp3"
    elif "apk" in ct_l or "android" in ct_l: ext = ".apk"
    elif "text" in ct_l: ext = ".txt"
    elif "json" in ct_l: ext = ".json"
    else: ext = ".bin"

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"{sanitize_filename(prefix)}_{ts}_{rand_str(4)}{ext}"
    path = RESULT_DIR / fname

    try:
        with open(path, "wb") as f: f.write(body)
        return str(path)
    except Exception:
        return None

def download_file(url, prefix):
    try:
        req = urllib.request.Request(url, headers={"user-agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
            ct = resp.headers.get("content-type", "")
            ext = ".bin"
            ct_l = ct.lower()
            if "jpeg" in ct_l: ext = ".jpg"
            elif "png" in ct_l: ext = ".png"
            elif "webp" in ct_l: ext = ".webp"
            elif "gif" in ct_l: ext = ".gif"
            elif "mp4" in ct_l or "video" in ct_l: ext = ".mp4"
            elif "mp3" in ct_l or "audio" in ct_l: ext = ".mp3"
            elif "apk" in ct_l: ext = ".apk"
            else:
                # cek dari URL
                low = url.lower()
                for x in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".mp3", ".apk"]:
                    if x in low:
                        ext = x.replace(".jpeg", ".jpg")
                        break

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = f"{sanitize_filename(prefix)}_{ts}_{rand_str(4)}{ext}"
            path = RESULT_DIR / fname
            with open(path, "wb") as f: f.write(data)
            return str(path), len(data)
    except Exception:
        return None, 0

def append_history(entry):
    try:
        h = []
        if os.path.isfile(HIST_FILE):
            try:
                with open(HIST_FILE) as f: h = json.load(f)
            except Exception: h = []
        h.insert(0, entry)
        with open(HIST_FILE, "w") as f: json.dump(h[:300], f, indent=2)
    except Exception: pass

# ================================================================
# UNIVERSAL RUNNER
# ================================================================
def run_endpoint(name, method, path, param_defs):
    """
    param_defs: list of (key, label, required, default)
    """
    header(name)

    print("  " + c("Endpoint:", GRY) + " " + c(method + " " + path, CY))
    print()

    params = {}
    for (key, label, required, default) in param_defs:
        suffix = c(" (optional)", GRY) if not required else ""
        d_hint = f" [{default}]" if default else ""
        val = prompt(f"{label}{d_hint}{suffix} :")
        if val is None: return
        if not val and default: val = default
        if required and not val:
            print("  " + c(f"✘ {label} wajib diisi.", RD))
            time.sleep(1.4); return
        if val: params[key] = val

    print()
    print("  " + c("Parameter:", WH + B))
    for k, v in params.items():
        print("  " + c("  " + k.ljust(15), GRY) + ": " + c(v[:60] if len(v) <= 60 else v[:57] + "...", WH))
    print()

    if prompt("Kirim request? (y/n) :").lower() != "y":
        return

    print()
    loading("Mengirim request", 1.2, CY)

    ok, body, ct, code, url = do_request(method, path, params)

    print()
    if not ok or code not in (200, 201, 202):
        snippet = body[:300].decode("utf-8", "replace") if isinstance(body, bytes) else str(body)[:300]
        print("  " + c(f"✘ Gagal ({code})", RD))
        print("  " + c(snippet, YL))
        print()
        try: input("  " + c("> ENTER untuk kembali ", DIM + WH))
        except Exception: pass
        return

    # deteksi jenis response
    saved_path = None
    kind = "unknown"

    ct_l = ct.lower()
    is_image = any(x in ct_l for x in ["image/", "jpeg", "png", "webp", "gif"])
    is_video = "video" in ct_l or "mp4" in ct_l
    is_audio = "audio" in ct_l or "mp3" in ct_l
    is_json  = "json" in ct_l

    if is_image or is_video or is_audio:
        # binary file
        kind = "binary"
        saved_path = save_result(body, ct, name)
    else:
        # cek apakah JSON dengan URL
        img_url = extract_url_from_json(body, ct)
        if img_url:
            kind = "json-url"
            print("  " + c("URL detected:", GRY) + " " + c(img_url[:70], CY))
            print()
            loading("Download file", 1.0, CY)
            saved_path, size = download_file(img_url, name)
            if not saved_path:
                print("  " + c("Gagal download, simpan URL aja", YL))
                # simpan URL sebagai txt
                saved_path = save_result(img_url.encode(), "text/plain", name + "_url")
        elif is_json or (body[:1] == b"{"):
            kind = "json"
            saved_path = save_result(body, "application/json", name, is_json=True)
        else:
            kind = "text"
            saved_path = save_result(body, "text/plain", name)

    # tampilkan hasil
    rows = [
        c("SUKSES", GR + B), "",
        c("Endpoint", GRY) + "  : " + c(path, CY),
        c("Status", GRY) + "    : " + c(str(code), GR + B),
        c("Type", GRY) + "      : " + c(kind, WH),
        c("Content", GRY) + "   : " + c(ct[:40] or "-", WH),
        c("Size", GRY) + "      : " + c(f"{len(body)/1024:.1f} KB", WH),
    ]

    if saved_path:
        rows.append("")
        rows.append(c("File", GRY) + "      : " + c(saved_path, CY + B))

    box("  HASIL  ", rows, GR)

    # preview kalau JSON
    if kind == "json" or kind == "json-url":
        try:
            j = json.loads(body.decode("utf-8", "replace"))
            preview = json.dumps(j, indent=2, ensure_ascii=False)[:600]
            print()
            print("  " + c("PREVIEW:", WH + B))
            for l in preview.splitlines()[:15]:
                print("  " + c(l, GRY))
        except Exception:
            pass

    append_history({
        "time": datetime.now().isoformat(),
        "endpoint": path,
        "params": params,
        "saved": saved_path,
        "status": code,
    })

    print()
    if saved_path:
        print("  " + c("Saved:", GRY) + " " + c(saved_path, CY))
    print()
    try: input("  " + c("> ENTER untuk kembali ", DIM + WH))
    except Exception: pass

# ================================================================
# ENDPOINT DATABASE
# ================================================================
ENDPOINTS = {
    "MAKER": [
        ("Two Buttons", "GET", "/api/maker/twobuttons", [
            ("teks1", "Teks 1", True, ""),
            ("teks2", "Teks 2", True, ""),
            ("teks3", "Teks 3", False, ""),
        ]),
        ("TikTok Quote Card", "GET", "/api/maker/ttqc", [
            ("username", "Username", True, ""),
            ("text", "Text", True, ""),
            ("avatar", "Avatar URL", False, ""),
        ]),
        ("Fake IG Profile", "GET", "/api/maker/fakeigprofile", [
            ("username", "Username", True, ""),
            ("postingan", "Postingan", False, "12"),
            ("pengikut", "Pengikut", False, "1.123"),
            ("mengikuti", "Mengikuti", False, "12"),
            ("bio", "Bio", False, ""),
            ("ppurl", "Photo Profile URL", False, ""),
        ]),
        ("Fake IG Profile v2", "GET", "/api/maker/fakeigprofilev2", [
            ("username", "Username", True, ""),
            ("ppurl", "Photo Profile URL", False, ""),
            ("bio", "Bio", False, ""),
            ("postingan", "Postingan", False, "12"),
            ("pengikut", "Pengikut", False, "1.123"),
            ("mengikuti", "Mengikuti", False, "86"),
        ]),
        ("Fake Call Android", "GET", "/api/maker/fakecall-andro", [
            ("name", "Nama penelepon", True, ""),
            ("duration", "Durasi (00:00)", False, "00:00"),
            ("avatar", "Avatar URL", False, ""),
        ]),
        ("Fake Facebook", "GET", "/api/maker/fakebook", [
            ("teks", "Teks", True, ""),
        ]),
        ("Fake Telegram Profile", "GET", "/api/maker/fake-tele", [
            ("nama", "Nama", True, ""),
            ("ponsel", "Nomor HP", False, ""),
            ("bio", "Bio", False, ""),
            ("username", "Username", False, ""),
            ("ppurl", "Photo Profile URL", False, ""),
        ]),
        ("Fake FF Profile", "GET", "/api/maker/fake-profile-ff", [
            ("nickname", "Nickname", True, ""),
            ("uid", "UID", True, ""),
        ]),
        ("Fake Nokia", "GET", "/api/maker/fake-nokia", [
            ("text", "Teks", True, ""),
        ]),
        ("Fake Mobile Legends", "GET", "/api/maker/fake-ml", [
            ("username", "Username", True, ""),
            ("rank", "Rank", False, "imo"),
            ("border", "Border (1-10)", False, "7"),
            ("avatar", "Avatar URL", False, ""),
        ]),
        ("Fake FF Lobby", "GET", "/api/maker/fake-ff", [
            ("username", "Username", True, ""),
            ("lobby", "Lobby (1-10)", False, "5"),
        ]),
    ],
    "CANVAS": [
        ("Apple Music", "GET", "/api/canvas/applemusic", [
            ("title", "Judul", True, ""),
            ("artist", "Artist", True, ""),
            ("cover", "Cover URL", True, ""),
            ("current", "Current (2:40)", False, "2:40"),
            ("total", "Total (04:11)", False, "04:11"),
            ("progress", "Progress %", False, "53"),
            ("color1", "Warna 1 (#hex)", False, "#7b2cbf"),
            ("color2", "Warna 2", False, "#ff2a5f"),
            ("color3", "Warna 3", False, "#ff7e40"),
        ]),
        ("Brat Anime", "GET", "/api/canvas/brat-anime", [
            ("text", "Text", True, ""),
        ]),
        ("Brat Gojo", "GET", "/api/canvas/brat-gojo", [
            ("text", "Text", True, ""),
        ]),
        ("Brat Vermeil", "GET", "/api/canvas/brat-vermeil", [
            ("text", "Text", True, ""),
        ]),
        ("Brat", "GET", "/api/canvas/brat", [
            ("text", "Text", True, ""),
            ("theme", "Theme (white/black)", False, "white"),
            ("blur", "Blur (0-10)", False, "0"),
            ("mode", "Mode (left/center)", False, "left"),
        ]),
        ("BratVid Gojo", "GET", "/api/canvas/bratvid-gojo", [
            ("text", "Text", True, ""),
            ("duration", "Duration (detik)", False, "10"),
        ]),
        ("BratVid Vermeil", "GET", "/api/canvas/bratvid-vermeil", [
            ("text", "Text", True, ""),
            ("duration", "Duration", False, "10"),
        ]),
        ("Carbon", "GET", "/api/canvas/carbon", [
            ("code", "Code", True, ""),
            ("theme", "Theme", False, "dracula-pro"),
            ("font", "Font", False, "Fira Code"),
            ("fontSize", "Font Size", False, "14px"),
            ("lineNumbers", "Line Numbers (true/false)", False, "true"),
        ]),
        ("Roblox Profile", "GET", "/api/canvas/roblox", [
            ("username", "Username", True, ""),
        ]),
        ("Struk Generator", "GET", "/api/canvas/struk-generator", [
            ("nama", "Nama Toko", True, ""),
            ("alamat", "Alamat Toko", False, ""),
            ("kontak", "Kontak", False, ""),
            ("kasir", "Kasir", False, ""),
            ("pelanggan", "Pelanggan", False, ""),
            ("alamatPelanggan", "Alamat Pelanggan", False, ""),
            ("items", "Items (nama,qty,satuan,harga|...)", True, ""),
            ("bayar", "Bayar", False, ""),
            ("metodeBayar", "Metode Bayar", False, "Cash"),
        ]),
        ("WMP (WhatsApp)", "GET", "/api/canvas/wmp", [
            ("text", "Text (line1|line2|line3)", True, ""),
        ]),
    ],
    "IMAGE HD": [
        ("AI Enhance v4", "GET", "/api/imagehd/ai-enhancev4", [
            ("url", "Image URL", True, ""),
            ("scale", "Scale (2/4)", False, "4"),
        ]),
        ("AI Enhance", "GET", "/api/imagehd/ai-enhance", [
            ("url", "Image URL", True, ""),
        ]),
        ("AI Enhance v2", "GET", "/api/imagehd/ai-enhancev2", [
            ("url", "Image URL", True, ""),
            ("size", "Size", False, "4"),
        ]),
        ("Nex Upscale", "GET", "/api/imagehd/nexupscale", [
            ("url", "Image URL", True, ""),
            ("mode", "Mode (2x/4x)", False, "4x"),
        ]),
        ("Photo Enhancer", "GET", "/api/imagehd/photoihancer", [
            ("url", "Image URL", True, ""),
            ("method", "Method", False, "1"),
        ]),
        ("Remini", "GET", "/api/imagehd/remini", [
            ("url", "Image URL", True, ""),
        ]),
    ],
    "IMAGE AI": [
        ("FreeForAI", "GET", "/api/imageai/freeforai", [
            ("prompt", "Prompt", True, ""),
            ("model", "Model", False, "flux-dev"),
            ("size", "Size", False, "1024*1024"),
        ]),
    ],
    "SOLVE": [
        ("BypassLink v3", "GET", "/api/solve/bypasslinkv3", [
            ("url", "Link URL", True, ""),
        ]),
        ("ShrinkMe", "GET", "/api/solve/shrinkme", [
            ("url", "Link URL", True, ""),
        ]),
        ("BypassLink", "GET", "/api/solve/bypasslink", [
            ("url", "Link URL", True, ""),
            ("androidId", "Android ID", False, ""),
        ]),
    ],
    "STALKER": [
        ("Free Fire", "GET", "/api/stalker/freefire", [
            ("uid", "UID", True, ""),
        ]),
        ("TikTok", "GET", "/api/stalker/tiktok", [
            ("username", "Username", True, ""),
        ]),
        ("YouTube", "GET", "/api/stalker/youtube", [
            ("username", "Username", True, ""),
        ]),
    ],
    "TEMPMAIL": [
        ("Tempmail Plus", "GET", "/api/tempmail/tempmailplus", [
            ("action", "Action (create/get)", False, "create"),
            ("email", "Email (kosong=auto)", False, ""),
            ("name", "Name", False, ""),
            ("domain", "Domain", False, "mailto.plus"),
            ("timeout", "Timeout (detik)", False, "60"),
        ]),
        ("Temporary Mail", "GET", "/api/tempmail/temporarymail", [
            ("action", "Action (create/get)", False, "create"),
            ("sessionId", "Session ID", False, ""),
            ("emailId", "Email ID", False, ""),
        ]),
        ("1TimeTech", "GET", "/api/tempmail/1timetech", [
            ("action", "Action", False, "create"),
            ("email", "Email", False, ""),
        ]),
    ],
    "TOOLS": [
        ("Cuaca BMKG", "GET", "/api/tools/cuaca-bmkg", [
            ("action", "Action", False, "search"),
            ("query", "Query (jakarta)", False, "jakarta"),
            ("kode", "Kode wilayah", False, ""),
        ]),
        ("FF Guest", "GET", "/api/tools/ff-guest", []),
        ("HTML to Image", "GET", "/api/tools/html2img", [
            ("htmlCode", "HTML Code", True, ""),
        ]),
        ("IP Tracker", "GET", "/api/tools/iptraker", [
            ("ip", "IP address", True, "8.8.8.8"),
        ]),
        ("NGL Spam", "GET", "/api/tools/ngl-spam", [
            ("url", "NGL Link", True, ""),
            ("question", "Question", True, ""),
            ("count", "Count", False, "100"),
        ]),
        ("NIK Parse", "GET", "/api/tools/nikparse", [
            ("nik", "NIK (16 digit)", True, ""),
        ]),
        ("Proxy2", "GET", "/api/tools/proxy2", [
            ("url", "URL", True, ""),
        ]),
        ("Spam OTP", "GET", "/api/tools/spam-otp", [
            ("number", "Nomor target", True, ""),
        ]),
        ("Subdomain Finder", "GET", "/api/tools/subdomain-finder", [
            ("domain", "Domain", True, ""),
        ]),
        ("Web to APK", "GET", "/api/tools/web2apk", [
            ("url", "URL", True, ""),
            ("appName", "App Name", True, ""),
            ("icon", "Icon URL", False, ""),
            ("packageName", "Package Name", True, ""),
        ]),
    ],
    "DOWNLOADER": [
        ("9xBuddy", "GET", "/api/downloader/9xbuddy", [
            ("url", "URL", True, ""),
        ]),
        ("GTW Search", "GET", "/api/downloader/gtw", [
            ("action", "Action (search)", False, "search"),
            ("query", "Query", False, ""),
            ("source", "Source", False, "an1"),
            ("page", "Page", False, "1"),
        ]),
        ("Pinterest Video", "GET", "/api/downloader/pinvid", [
            ("url", "Pin URL", True, ""),
        ]),
        ("Spotify", "GET", "/api/downloader/spotify", [
            ("url", "Spotify URL", True, ""),
        ]),
        ("TikTok v2", "GET", "/api/downloader/tiktokv2", [
            ("url", "TikTok URL", True, ""),
        ]),
        ("TikTok", "GET", "/api/downloader/tiktok", [
            ("url", "TikTok URL", True, ""),
        ]),
        ("YouTube v4", "GET", "/api/downloader/youtubev4", [
            ("url", "YouTube URL", True, ""),
        ]),
    ],
    "HD VIDEO": [
        ("AI Upscale Video", "GET", "/api/hdvidio/ai-upscale-vidio", [
            ("url", "Video URL", True, ""),
            ("resolution", "Resolution", False, "1080p"),
        ]),
        ("To HD", "GET", "/api/hdvidio/tohd", [
            ("url", "Video URL", True, ""),
            ("fps", "FPS", False, "30"),
            ("resolution", "Resolution", False, "1080p"),
            ("quality", "Quality", False, "90"),
            ("enhance", "Enhance (yes/no)", False, "yes"),
            ("denoise", "Denoise (yes/no)", False, "no"),
            ("stabilize", "Stabilize (yes/no)", False, "no"),
            ("format", "Format", False, "mp4"),
        ]),
        ("Wink HD Video", "GET", "/api/hdvidio/wink-hd-video", [
            ("url", "Video URL", True, ""),
        ]),
    ],
    "RANDOM": [
        ("Quotes Anime", "GET", "/api/random/quotesanime", []),
        ("Waifu", "GET", "/api/random/waifu", []),
    ],
}

# ================================================================
# CATEGORY MENU
# ================================================================
def category_menu(cat_name):
    while True:
        items = ENDPOINTS[cat_name]
        header(cat_name + " — " + str(len(items)) + " endpoint")
        for i, (name, method, path, params) in enumerate(items, 1):
            print("  " + c(f"[{i:02}]", MG) + " " + c(name.ljust(25), WH) + " " + c(path, GRY))
        print()
        print("  " + c("[0]", MG) + " kembali")
        print()
        line("─", GRY)

        ch = prompt("Pilih :")
        if ch is None or ch == "0": return
        try:
            idx = int(ch) - 1
            if 0 <= idx < len(items):
                name, method, path, params = items[idx]
                run_endpoint(name, method, path, params)
        except Exception:
            pass

# ================================================================
# MAIN MENU
# ================================================================
def count_results():
    try:
        return sum(1 for f in RESULT_DIR.iterdir() if f.is_file())
    except Exception:
        return 0

def main_menu():
    while True:
        banner()
        n_files = count_results()
        pr = len(CFG.get("proxies", []))
        print("  " + c("Results", GRY) + " : " + c(str(n_files), WH) + " file  " + c("(" + str(RESULT_DIR) + ")", GRY))
        print("  " + c("Proxies", GRY) + " : " + c(str(pr), WH if pr else GRY) + c("  (use: " + ("ON" if CFG["use_proxy"] else "OFF") + ")", GRY))
        print()
        print("  " + c("KATEGORI:", WH + B))
        cats = list(ENDPOINTS.keys())
        for i, cat in enumerate(cats, 1):
            n = len(ENDPOINTS[cat])
            print("  " + c(f"[{i:02}]", MG) + " " + c(cat.ljust(15), WH) + " " + c(f"({n} endpoint)", GRY))
        print()
        print("  " + c("TOOLS:", WH + B))
        base = len(cats)
        print("  " + c(f"[{base+1:02}]", CY) + " " + c("Manage Proxy", WH))
        print("  " + c(f"[{base+2:02}]", CY) + " " + c("Settings", WH))
        print("  " + c(f"[{base+3:02}]", CY) + " " + c("History", WH))
        print("  " + c(f"[{base+4:02}]", CY) + " " + c("Buka Folder Result", WH))
        print("  " + c(f"[{base+5:02}]", CY) + " " + c("Info Dev", WH))
        print("  " + c("[0]", RD) + " " + c("Exit", WH))
        print()
        line("─", GRY)

        ch = prompt("Pilih :")
        if ch is None or ch == "0":
            clear(); banner()
            type_out("  thanks — " + AUTHOR + ".", 0.02, MG)
            print()
            return
        try:
            n = int(ch)
        except Exception:
            continue
        if 1 <= n <= len(cats):
            category_menu(cats[n - 1])
        elif n == base + 1: proxy_menu()
        elif n == base + 2: settings_menu()
        elif n == base + 3: history_menu()
        elif n == base + 4: open_result_folder()
        elif n == base + 5: info_dev()

# ================================================================
# PROXY MENU
# ================================================================
def proxy_menu():
    global CFG
    while True:
        header("MANAGE PROXY")
        print("  " + c("Total", GRY) + " : " + c(str(len(CFG["proxies"])), WH))
        print("  " + c("Use", GRY) + "   : " + c("ON" if CFG["use_proxy"] else "OFF", GR if CFG["use_proxy"] else GRY))
        print()
        print("  " + c("[1]", MG) + " scrape proxy gratis")
        print("  " + c("[2]", MG) + " tambah manual")
        print("  " + c("[3]", MG) + " lihat list (30 pertama)")
        print("  " + c("[4]", MG) + " hapus semua")
        print("  " + c("[5]", MG) + " toggle use proxy")
        print("  " + c("[0]", MG) + " kembali")
        print()
        ch = prompt("Pilih :")
        if ch is None or ch == "0": return
        if ch == "1":
            loading("Scrape proxy", 3.0, CY)
            try:
                req = urllib.request.Request(
                    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
                    headers={"user-agent": "Mozilla/5.0"},
                )
                with urllib.request.urlopen(req, timeout=20) as resp:
                    body = resp.read().decode()
                added = 0
                for l in body.splitlines():
                    l = l.strip()
                    if ":" in l:
                        p = "http://" + l
                        if p not in CFG["proxies"]:
                            CFG["proxies"].append(p); added += 1
                save_cfg(CFG)
                print("  " + c(f"Ditambah: {added}", GR))
            except Exception as e:
                print("  " + c("Gagal: " + str(e)[:50], RD))
            time.sleep(1.5)
        elif ch == "2":
            p = prompt("Proxy (http://ip:port) :")
            if p and p not in CFG["proxies"]:
                CFG["proxies"].append(p); save_cfg(CFG)
                print("  " + c("Ditambah.", GR)); time.sleep(1.0)
        elif ch == "3":
            for i, p in enumerate(CFG["proxies"][:30], 1):
                print("  " + c(f"[{i:02}]", CY) + " " + c(p, WH))
            print()
            try: input("  " + c("> ENTER ", DIM + WH))
            except Exception: pass
        elif ch == "4":
            if prompt("Hapus semua? (y/n) :").lower() == "y":
                CFG["proxies"] = []; save_cfg(CFG)
                print("  " + c("Cleared.", GR)); time.sleep(1.0)
        elif ch == "5":
            CFG["use_proxy"] = not CFG["use_proxy"]; save_cfg(CFG)
            print("  " + c("Use proxy: " + ("ON" if CFG["use_proxy"] else "OFF"), GR))
            time.sleep(1.0)

def settings_menu():
    global CFG
    while True:
        header("SETTINGS")
        print("  " + c("Timeout", GRY) + " : " + c(str(CFG["timeout"]) + "s", WH))
        print()
        print("  " + c("[1]", CY) + " ubah timeout")
        print("  " + c("[0]", CY) + " kembali")
        print()
        ch = prompt("Pilih :")
        if ch is None or ch == "0": return
        if ch == "1":
            try:
                CFG["timeout"] = max(10, min(300, int(prompt("Timeout (detik) :"))))
                save_cfg(CFG)
            except Exception: pass

def history_menu():
    header("HISTORY")
    if not os.path.isfile(HIST_FILE):
        print("  " + c("Belum ada history.", GRY))
        print()
        try: input("  " + c("> ENTER untuk kembali ", DIM + WH))
        except Exception: pass
        return
    try:
        with open(HIST_FILE) as f: h = json.load(f)
    except Exception: h = []
    if not h:
        print("  " + c("Kosong.", GRY))
    else:
        for i, e in enumerate(h[:20], 1):
            ts = e.get("time", "")[:19].replace("T", " ")
            ep = e.get("endpoint", "-")[:40]
            saved = e.get("saved") or "-"
            print("  " + c(f"[{i:02}]", CY) + " " + c(ep.ljust(40), WH) + " " + c(ts, GRY))
            print("       " + c(str(saved)[:70], GRY))
    print()
    try: input("  " + c("> ENTER untuk kembali ", DIM + WH))
    except Exception: pass

def open_result_folder():
    header("RESULT FOLDER")
    n = count_results()
    print("  " + c("Path", GRY) + "  : " + c(str(RESULT_DIR), CY))
    print("  " + c("Files", GRY) + " : " + c(str(n), WH))
    print()
    try:
        files = sorted(RESULT_DIR.iterdir(), key=lambda f: f.stat().st_mtime, reverse=True)[:20]
        for i, f in enumerate(files, 1):
            if f.is_file():
                size = f.stat().st_size
                print("  " + c(f"[{i:02}]", CY) + " " + c(f.name[:50].ljust(50), WH) + " " + c(f"{size/1024:.1f} KB", GRY))
    except Exception:
        pass
    print()
    if prompt("Buka folder di file manager? (y/n) :").lower() == "y":
        try:
            os.system(f"termux-open '{RESULT_DIR}' 2>/dev/null &")
        except Exception:
            pass
    print()
    try: input("  " + c("> ENTER untuk kembali ", DIM + WH))
    except Exception: pass

def info_dev():
    header("INFO DEVELOPER")
    total = sum(len(v) for v in ENDPOINTS.values())
    rows = [
        c("Author", GRY) + "    : " + c(AUTHOR, MG + B),
        c("Aplikasi", GRY) + "  : " + c(APP, WH),
        c("Versi", GRY) + "     : " + c(VER, WH),
        c("Base URL", GRY) + "  : " + c(BASE_URL, CY),
        c("Result", GRY) + "    : " + c(str(RESULT_DIR), GRY),
        c("Total", GRY) + "     : " + c(str(total) + " endpoint", GR + B),
        "",
        c("Kategori:", GRY),
    ]
    for cat, items in ENDPOINTS.items():
        rows.append("  " + c(cat.ljust(15), WH) + " " + c(str(len(items)) + " endpoint", GRY))
    rows += [
        "",
        c("Cara pakai:", GRY),
        c("  - pilih kategori → pilih endpoint → isi param", WH),
        c("  - hasil auto-save ke result/acx/", WH),
        "",
        c("Dibuat oleh " + AUTHOR, WH + B),
    ]
    box("  DEVELOPER  ", rows, MG)
    print()
    try: input("  " + c("> ENTER untuk kembali ", DIM + WH))
    except Exception: pass

# ================================================================
# MAIN
# ================================================================
def main():
    try:
        clear()
        loading("Memuat sistem", 0.6, MG)
        main_menu()
    except KeyboardInterrupt:
        print()
        clear(); banner()
        print("  " + c("bye — " + AUTHOR + ".", MG))
        print()

if __name__ == "__main__":
    main()