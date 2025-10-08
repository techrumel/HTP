
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
# Install Python & Git using winget (optional)
winget install --id=Python.Python.3 -e --source winget
winget install --id=Git.Git -e --source winget

cd $env:USERPROFILE
# Create projects folder if it doesn't exist
if (-not (Test-Path -Path .\projects)) { mkdir projects }
cd projects

# Clone HTP repo (skip if already exists)
if (-not (Test-Path -Path .\HTP)) {
    git clone https://github.com/techrumel/HTP.git
}
cd HTP

# Create Python virtual environment
python -m venv .venv

# Activate venv (bypass execution policy if blocked)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\.venv\Scripts\Activate.ps1

# Upgrade pip & install required Python packages
pip install --upgrade pip setuptools wheel
pip install flask requests "qrcode[pil]" pillow

# Optional: download cloudflared if not present
if (-not (Test-Path -Path .\bin\cloudflared.exe)) {
    mkdir .\bin -Force
    Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile ".\bin\cloudflared.exe" -UseBasicParsing
}
</code></pre>

<hr>
<h2>3a) WINDOWS — Re-open / Start</h2>
<pre><code># (PowerShell)
cd $env:USERPROFILE\projects\HTP

# Activate venv (bypass execution policy if blocked)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\.venv\Scripts\Activate.ps1

# Run in foreground (interactive)
python HTP.py

# OR run in background with logs
New-Item -ItemType Directory -Path .\logs -Force | Out-Null
$p = Start-Process -FilePath python -ArgumentList "HTP.py" -RedirectStandardOutput ".\logs\out.log" -RedirectStandardError ".\logs\err.log" -PassThru

# Monitor logs live
Get-Content .\logs\out.log -Wait -Tail 50

# Optional: Start Cloudflared manually if public URL needed
.\bin\cloudflared.exe tunnel --url http://
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
