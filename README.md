<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>HTP — Install & Re-open Guide</title>
</head>
<body>
  <h1>HTP by MrXeno 🔍📱</h1>

  <p><strong>IMPORTANT:</strong> Use this tool only on devices you own or have explicit permission to test. Misuse is illegal and unethical.</p>

  <hr>

  <h2>Table of contents</h2>
  <ol>
    <li>Termux — Install & Re-open</li>
    <li>Termux (Ubuntu proot) — Install & Re-open</li>
    <li>Ubuntu / WSL — Install & Re-open</li>
    <li>Windows (PowerShell) — Install & Re-open (auto cloudflared)</li>
    <li>Common commands: run, logs, stop</li>
  </ol>

  <hr>

  <h2>1) TERMUX (native) — Install</h2>
  <p>If you want to run native Termux (we recommend Ubuntu proot for better compatibility):</p>
  <pre><code>pkg update -y && pkg upgrade -y
pkg install git python curl wget -y

# Clone repo
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/techrumel/HTP.git
cd HTP
chmod +x HTP.py

# Create venv and install
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install flask requests "qrcode[pil]" pillow</code></pre>

  <h3>Termux — Re-open / Start</h3>
  <pre><code>cd ~/projects/HTP
source .venv/bin/activate
# foreground (debug)
python3 HTP.py
# or background with logs
mkdir -p logs
nohup python3 HTP.py > logs/out.log 2>&1 &
tail -f logs/out.log</code></pre>

  <hr>

  <h2>2) TERMUX (Ubuntu proot) — Install</h2>
  <p>Using Ubuntu proot gives better binary compatibility — recommended:</p>
  <pre><code>pkg update -y && pkg upgrade -y
pkg install proot-distro git -y
proot-distro install ubuntu
proot-distro login ubuntu

# Now inside Ubuntu shell:
apt update && apt upgrade -y
apt install -y python3 python3-venv python3-pip build-essential pkg-config libjpeg-dev libpng-dev zlib1g-dev libfreetype6-dev git wget curl

# Clone & setup
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/techrumel/HTP.git
cd HTP
chmod +x HTP.py
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install flask requests "qrcode[pil]" pillow</code></pre>

  <h3>Termux (Proot) — Re-open / Start</h3>
  <pre><code>proot-distro login ubuntu
cd ~/projects/HTP
source .venv/bin/activate
mkdir -p logs
nohup python3 HTP.py > logs/out.log 2>&1 &
tail -f logs/out.log</code></pre>

  <hr>

  <h2>3) UBUNTU / WSL (Desktop) — Install</h2>
  <pre><code>sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git wget curl build-essential pkg-config libjpeg-dev libpng-dev zlib1g-dev libfreetype6-dev

mkdir -p ~/projects
cd ~/projects
git clone https://github.com/techrumel/HTP.git
cd HTP
chmod +x HTP.py
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install flask requests "qrcode[pil]" pillow</code></pre>

  <h3>Ubuntu / WSL — Re-open / Start</h3>
  <pre><code>cd ~/projects/HTP
source .venv/bin/activate
mkdir -p logs
nohup python3 HTP.py > logs/out.log 2>&1 &
tail -f logs/out.log</code></pre>

  <hr>

  <h2>4) WINDOWS (PowerShell) — Install (auto cloudflared)</h2>
  <p>Copy and paste the commands below into PowerShell. They will:</p>
  <ul>
    <li>Create and activate a virtual environment (temporary execution policy bypass if needed)</li>
    <li>Install Python packages</li>
    <li>Detect Windows architecture and download the correct Cloudflare Tunnel binary into <code>.\bin\cloudflared.exe</code></li>
  </ul>

  <pre><code># (PowerShell)
# Optional: install Python & Git via winget if needed
winget install --id=Python.Python.3 -e --source winget
winget install --id=Git.Git -e --source winget

cd $env:USERPROFILE
if (-not (Test-Path -Path ".\projects")) { New-Item -ItemType Directory -Path ".\projects" | Out-Null }
cd .\projects

# Clone repo if not present
if (-not (Test-Path -Path ".\HTP")) {
  git clone https://github.com/techrumel/HTP.git
}
cd HTP

# Create venv and activate (bypass execution policy for this session)
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\.venv\Scripts\Activate.ps1

# Upgrade pip & install Python packages
python -m pip install --upgrade pip setuptools wheel
pip install flask requests "qrcode[pil]" pillow

# Auto-detect Windows architecture and download correct cloudflared
$binDir = Join-Path $PWD "bin"
New-Item -ItemType Directory -Path $binDir -Force | Out-Null
$arch = (Get-CimInstance Win32_OperatingSystem).OSArchitecture
Write-Output "Detected OS Architecture: $arch"

if ($arch -match "64") {
  $cloudUrl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
} elseif ($arch -match "32") {
  $cloudUrl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-386.exe"
} else {
  $cloudUrl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
}

$cloudPath = Join-Path $binDir "cloudflared.exe"
Write-Output "Downloading cloudflared from: $cloudUrl"
Invoke-WebRequest -Uri $cloudUrl -OutFile $cloudPath -UseBasicParsing
Write-Output "Saved cloudflared to: $cloudPath"</code></pre>

  <h3>Windows — Re-open / Start</h3>
  <pre><code># (PowerShell)
cd $env:USERPROFILE\projects\HTP

# Activate venv (bypass execution policy if blocked)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\.venv\Scripts\Activate.ps1

# Run HTP in foreground
python HTP.py

# Or run in background with logs
New-Item -ItemType Directory -Path .\logs -Force | Out-Null
$p = Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "HTP.py" -RedirectStandardOutput ".\logs\out.log" -RedirectStandardError ".\logs\err.log" -PassThru

# Tail logs
Get-Content .\logs\out.log -Wait -Tail 50

# If cloudflared did not auto-start or no public URL shown, run manually:
cd $env:USERPROFILE\projects\HTP\bin
.\cloudflared.exe tunnel --url http://127.0.0.1:8080</code></pre>

  <hr>

  <h2>5) Common commands (same everywhere)</h2>

  <h3>Start (foreground)</h3>
  <pre><code>python HTP.py</code></pre>

  <h3>Start (background) — Linux / Termux</h3>
  <pre><code>mkdir -p logs
nohup python3 HTP.py > logs/out.log 2>&1 &</code></pre>

  <h3>Start (background) — Windows PowerShell</h3>
  <pre><code>New-Item -ItemType Directory -Path .\logs -Force | Out-Null
Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "HTP.py" -RedirectStandardOutput ".\logs\out.log" -RedirectStandardError ".\logs\err.log" -PassThru</code></pre>

  <h3>View logs</h3>
  <pre><code># Linux / Termux
tail -f logs/out.log

# Windows PowerShell
Get-Content .\logs\out.log -Wait -Tail 50</code></pre>

  <h3>Stop HTP</h3>
  <pre><code># Linux / Termux
pkill -f HTP.py

# Windows (PowerShell)
Get-Process python | Where-Object { $_.Path -like "*HTP*" } | Stop-Process -Force</code></pre>

  <hr>

  <h2>Troubleshooting — common issues</h2>
  <ul>
    <li><strong>cloudflared architecture / WinError 193:</strong> you have the wrong binary. Use the Windows auto-detect step above or replace <code>.\bin\cloudflared.exe</code> with the matching file for your OS (amd64 / 386 / arm).</li>
    <li><strong>ModuleNotFoundError:</strong> activate <code>.venv</code> then run <code>pip install &lt;module&gt;</code>.</li>
    <li><strong>Pillow build errors:</strong> install system dev packages (libjpeg, zlib, libpng, freetype) before installing pillow.</li>
    <li><strong>Cloudflare tunnel not shown:</strong> run cloudflared manually from <code>.\bin\cloudflared.exe tunnel --url http://127.0.0.1:8080</code> and check its output for the <code>trycloudflare</code> URL.</li>
  </ul>

  <hr>

  <h2>Legal & Ethical</h2>
  <p>Always get explicit permission before tracking devices. This tool is for education/testing. Misuse is your responsibility.</p>

</body>
</html>
