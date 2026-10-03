<!--
  __  __          _____  ______       ______     __   __      __      _____ _____  _           __     ___________   ___  
 |  \/  |   /\   |  __ \|  ____|     |  _ \ \   / /   \ \    / /\    / ____|  __ \| |        /\\ \   / /___  / _ \ / _ \ 
 | \  / |  /  \  | |  | | |__        | |_) \ \_/ /     \ \  / /  \  | (___ | |__) | |       /  \\ \_/ /   / / (_) | | | |
 | |\/| | / /\ \ | |  | |  __|       |  _ < \   /       \ \/ / /\ \  \___ \|  ___/| |      / /\ \\   /   / / \__, | | | |
 | |  | |/ ____ \| |__| | |____      | |_) | | |         \  / ____ \ ____) | |    | |____ / ____ \| |   / /__  / /| |_| |
 |_|  |_/_/    \_\_____/|______|     |____/  |_|          \/_/    \_\_____/|_|    |______/_/    \_\_|  /_____|/_/  \___/ 
                                                                                                                         
                                                                                                                         
                  ArizNodesLabs  ×  Vasplayz90
-->

<h1 align="center">🖥️ VPS Deployer Bot</h1>

<p align="center">
  <b>Deploy real Linux VPS containers straight from Discord.</b><br>
  LXC-powered · Pinggy.io SSH tunnels · Modern button UI · Web dashboard
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-5865F2?style=for-the-badge">
  <img src="https://img.shields.io/badge/python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/LXC-powered-orange?style=for-the-badge">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge">
</p>

<p align="center">
  <b>Made with ❤️ by <a href="https://github.com/ariznodes-og">ArizNodesLabs</a> & Vasplayz90</b>
</p>

---

## ✨ What is this?

A Discord bot that turns your Linux server into a **one-click VPS provider**.
Users type `!deploy debian12`, get an LXC container with its own CPU/RAM/disk limits,
a public SSH endpoint via a Pinggy tunnel, and a modern management panel with buttons.

No Docker. No Kubernetes. Real containers, real SSH, real internet.

---

## 🚀 Features

- 🧩 **LXC container deployment** — real Linux containers, not fake shell accounts
- 🐧 **14 OS templates** — Debian 11/12/13, Ubuntu 20/22/24, AlmaLinux, Rocky, CentOS, Fedora, Arch, Kali, openSUSE
- 🌐 **Pinggy.io SSH tunnels** — public `tcp://` endpoints from a single SSH command
- 🎛 **Modern Discord UI** — buttons, modals, confirm dialogs, live panels
- 📸 **Snapshots** — create / list / restore / delete
- ⌨️ **Console modal** — run shell commands inside containers from Discord
- 📊 **Live stats** — CPU, RAM, IP, state, per-container info
- 🗄 **Web dashboard** — Flask panel with Start/Stop/Destroy buttons
- 📝 **Audit log** — every action tracked
- 🔒 **Per-user limits** — configurable max VPS per user
- ⚙️ **Systemd ready** — runs as a proper Linux service
- 🧾 **167 commands** — full VPS, network, system, admin, utility coverage

---

## 📦 Requirements

| Component | Version |
|---|---|
| OS | Debian 11+ / Ubuntu 22.04+ (host) |
| Python | 3.10 or newer |
| LXC | 4.0 or newer |
| Network | Outbound SSH (port 443) for Pinggy |
| Privileges | root (LXC requires it) |

---

## ⚡ Quick Install

```bash
# 1. Host prep
apt update && apt upgrade -y
apt install -y lxc lxc-templates lxc-utils bridge-utils dnsmasq openssh-client git curl
systemctl enable --now lxc-net

# 2. Clone
cd /root
git clone https://github.com/ariznodes-og/vps-deployerbot.git
cd vps-deployerbot

# 3. Python env
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
nano .env     # paste your Discord token + dashboard secret

# 5. Test run
sudo python3 bot.py
# press Ctrl+C once you see "[+] Logged in as ..."

# 6. Install as system service
sudo cp systemd/vps-deployerbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now vps-deployerbot

# 7. Check
sudo systemctl status vps-deployerbot
