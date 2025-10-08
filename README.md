
---

## 2) HTML version (complete) — copy this whole block into a `.html` file

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>HTP by MrXeno — README</title>
<style>
  body{font-family:Inter,Arial,sans-serif;background:#f9fafb;color:#111;padding:28px;max-width:980px;margin:0 auto}
  h1{font-size:28px}
  pre{background:#111827;color:#f8fafc;padding:12px;border-radius:6px;overflow:auto}
  code{background:#eef2ff;padding:2px 6px;border-radius:4px}
  .badge{display:inline-block;padding:4px 8px;border-radius:6px;color:#fff;margin-right:6px}
  .b-blue{background:#3572A5}.b-green{background:#16a34a}.b-orange{background:#f97316}
  hr{border:none;height:1px;background:#e6e6e6;margin:18px 0}
  h2{margin-top:18px}
  ul{margin-left:18px}
  .note{color:#6b7280;font-style:italic}
</style>
</head>
<body>
<h1>HTP by MrXeno 🔍📱</h1>
<div>
  <span class="badge b-blue">Python 3.x</span>
  <span class="badge b-green">MIT License</span>
  <span class="badge b-orange">Termux | Windows | Linux</span>
</div>
<p>A Termux-friendly <strong>phone tracking & testing tool</strong> with <strong>full auto install</strong> and Cloudflare tunnel support.</p>
<blockquote><strong>IMPORTANT:</strong> Use this tool only on devices you own or have <strong>explicit permission</strong> to test. Misuse is illegal and unethical.</blockquote>
<hr>

<h2>Quick overview</h2>
<p class="note">This README contains: Termux, Ubuntu/WSL, Windows installation and re-open/start instructions.</p>

<hr>
<h2>1) TERMUX — Install (first time)</h2>
<pre><code>pkg update -y && pkg upgrade -y
pkg install git python curl wget proot-distro -y
proot-distro install ubuntu
proot-distro login ubuntu
</code></pre>
<p><strong>Inside Ubuntu proot:</strong></p>
<pre><code>apt update && apt upgrade -y
apt install -y python3 python3-venv python3-pip build-essential pkg-config libjpeg-turbo8-dev libpng-dev zlib1g-dev libfreetype6-dev git wget
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/techrumel/HTP.git
cd HTP
chmod +x HTP.py
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install flask requests "qrcode[pil]" pillow
</code></pre>

<hr>
<h2>1a) TERMUX — Re-open / Start</h2>
<pre><code>proot-distro login ubuntu
cd ~/projects/HTP
source .venv/bin/activate
mkdir -p logs
nohup python3 HTP.py &gt; logs/out.log 2&gt;&amp;1 &amp;
tail -f logs/out.log
</code></pre>

<hr>
<h2>2) UBUNTU / WSL — Install</h2>
<pre><code>sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git curl wget build-essential pkg-config libjpeg-turbo8-dev libpng-dev zlib1g-dev libfreetype6-dev
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/techrumel/HTP.git
cd HTP
chmod +x HTP.py
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install flask requests "qrcode[pil]" pillow
</code></pre>

<hr>
<h2>2a) UBUNTU / WSL — Re-open / Start</h2>
<pre><code>cd ~/projects/HTP
source .venv/bin/activate
mkdir -p logs
nohup python3 HTP.py &gt; logs/out.log 2&gt;&amp;1 &amp;
tail -f logs/out.log
</code></pre>

<hr>
<h2>3) WINDOWS (PowerShell) — Install</h2>
<pre><code># (PowerShell)
# install Python & Git using winget (optional)
winget install --id=Python.Python.3 -e --source winget
winget install --id=Git.Git -e --source winget

cd $env:USERPROFILE
mkdir projects
cd projects
git clone https://github.com/techrumel/HTP.git
cd HTP
python -m venv .venv
.\.venv\Scripts\Activate.ps1    # if blocked, run: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
pip install --upgrade pip setuptools wheel
pip install flask requests "qrcode[pil]" pillow
</code></pre>

<hr>
<h2>3a) WINDOWS — Re-open / Start</h2>
<pre><code># (PowerShell)
cd $env:USERPROFILE\projects\HTP
.\.venv\Scripts\Activate.ps1
# run foreground
python HTP.py
# or background with logs
New-Item -ItemType Directory -Path .\logs -Force | Out-Null
$p = Start-Process -FilePath python -ArgumentList "HTP.py" -RedirectStandardOutput ".\logs\out.log" -RedirectStandardError ".\logs\err.log" -PassThru
Get-Content .\logs\out.log -Wait -Tail 20
</code></pre>

<hr>
<h2>Common commands</h2>
<pre><code>mkdir -p logs
nohup python3 HTP.py &gt; logs/out.log 2&gt;&amp;1 &amp;
tail -f logs/out.log
pkill -f HTP.py
~/bin/cloudflared tunnel --url http://127.0.0.1:8080</code></pre>

<hr>
<h2>Troubleshooting & notes</h2>
<ul>
<li>If `pillow` fails, install system packages and retry <code>pip install --no-cache-dir pillow</code>.</li>
<li>If cloudflared shows illegal instruction, download binary for your architecture.</li>
<li>Use Ubuntu proot on Termux for best compatibility.</li>
</ul>

<hr>
<p><strong>With great power comes great responsibility. Use knowledge ethically.</strong></p>
</body>
</html>
