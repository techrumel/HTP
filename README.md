# HTP by MrXeno 🔍📱

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Platform](https://img.shields.io/badge/Platform-Termux-orange?style=flat&logo=android)

A Termux-friendly **phone tracking & testing tool** with **full auto install** and Cloudflare tunnel support.  

> **IMPORTANT:** Use this tool only on devices you own or have **explicit permission** to test. Misuse is illegal and unethical.  

---

## ⚠️ Disclaimer

**HTP is for educational & testing purposes only.**  
Do **not** use this tool to track devices without consent. The developers are not responsible for misuse.

---

## 📋 Features

- 🔒 **Tool Lock** — requires consent before starting  
- 🌐 **Cloudflare Tunnel** — auto public URL generation  
- 📍 **Live Location Tracking** — real-time GPS coordinates in Termux  
- 📱 **QR Code Generator** — easy sharing of URL  
- ✅ **Single File Solution** — `HTP.py`, no complex setup needed  

---

## 🧰 Requirements

- Android device with Termux **or** Linux/WSL/Ubuntu  
- Python 3.8+  
- Internet connection  
- `cloudflared` (auto-download included)  
- Python packages: `flask`, `requests`, `qrcode[pil]`, `pillow`  

---

## 📥 Installation & Setup

> Works on Termux + Ubuntu Proot or Linux desktop.  

### Termux / Linux Setup

```bash
# Update Termux packages
pkg update -y && pkg upgrade -y

# Install essentials
pkg install git python curl wget proot-distro -y

# Install Ubuntu Proot (optional but recommended)
proot-distro install ubuntu
proot-distro login ubuntu
