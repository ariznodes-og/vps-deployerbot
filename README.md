<div align="center">

 █████╗ ██████╗ ██╗███████╗███╗   ██╗ ██████╗ ██████╗ ███████╗███████╗
██╔══██╗██╔══██╗██║╚══███╔╝████╗  ██║██╔═══██╗██╔══██╗██╔════╝██╔════╝
███████║██████╔╝██║  ███╔╝ ██╔██╗ ██║██║   ██║██║  ██║█████╗  ███████╗
██╔══██║██╔══██╗██║ ███╔╝  ██║╚██╗██║██║   ██║██║  ██║██╔══╝  ╚════██║
██║  ██║██║  ██║██║███████╗██║ ╚████║╚██████╔╝██████╔╝███████╗███████║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝╚══════╝

**Deploy real Linux VPS containers straight from Discord.**

LXC-powered · Pinggy-exposed · Browser-accessible · Self-hosted · MIT

[![Version](https://img.shields.io/badge/version-2.0.0-5865F2?style=for-the-badge)](https://github.com/ariznodes-og/vps-deployerbot)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
[![LXC](https://img.shields.io/badge/powered%20by-LXC-orange?style=for-the-badge)](https://linuxcontainers.org)

**Made by [ArizNodesLabs](https://github.com/ariznodes-og) × Vasplayz90**

</div>

---

## 🚀 What is this?

A Discord bot that turns a plain Linux box into a **one-command VPS provider**.

Users type `!deploy debian12` in chat. They get:
- A real **LXC container** with its own CPU, RAM, and disk limits
- A **public SSH endpoint** through a Pinggy reverse tunnel
- A **management panel** with buttons — start, stop, restart, console, snapshots
- A **browser root shell** via sshx (no SSH client needed)

No Docker. No Kubernetes. No cloud provider. Just LXC, Python, and shell.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧩 **Real LXC containers** | Full Linux containers with own init, cgroup v2 limits, bridge networking |
| 🐧 **14 OS templates** | Debian 11/12/13, Ubuntu 20/22/24, AlmaLinux 8/9, Rocky 9, CentOS 9 Stream, Fedora 40, Arch, Kali, openSUSE |
| 🌐 **Pinggy tunnels** | Public SSH endpoints from one command. No port forwarding, no public IP needed |
| 🎛️ **Modern Discord UI** | Buttons, modals, live panels. Manage everything from chat |
| 🔗 **sshx browser shell** | One-click root shell in the browser. No SSH client, no password |
| 📊 **Web dashboard** | Flask panel with live host stats, container control, broadcast, and audit log |
| 📸 **Snapshots** | Snapshot any container before you break it. Restore with one command |
| 🔒 **Limits & safety** | Per-user VPS caps, per-guild caps, global rate limits, role-gated deploys |
| 🗄️ **Audit log** | Every action tracked with user and timestamp |
| ⚙️ **Systemd ready** | Runs as a proper Linux service, auto-restarts on failure |

---

## 📋 Requirements

| Component | Requirement |
|---|---|
| Host OS | Debian 12 or Ubuntu 22.04+ (bare metal or KVM VPS) |
| Privileges | **root** (LXC needs it) |
| Python | 3.10 or newer |
| Outbound ports | 22, 443, 80 |
| RAM | 1 GB minimum, 4 GB recommended |
| Disk | 20 GB minimum, ~1 GB per container |

> ⚠️ **Won't work on:** GitHub Codespaces, Docker containers, Fly.io, Render, Railway, Koyeb, Heroku. Those don't allow nested LXC with root.

---

## ⚡ Quick Install

```bash
# 1. System packages
apt update && apt install -y \
    lxc lxc-templates lxc-utils bridge-utils dnsmasq \
    git python3-venv python3-full python3-pip curl
systemctl enable --now lxc-net
ip addr show lxcbr0        # must print a real interface

# 2. Clone
cd /root
git clone https://github.com/ariznodes-og/vps-deployerbot.git
cd vps-deployerbot

# 3. Python environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip wheel
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
nano .env                  # paste your Discord bot token

# 5. Test run
sudo python bot.py         # verify login, then Ctrl+C

# 6. Install as service
sudo cp systemd/vps-deployerbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now vps-deployerbot
sudo systemctl status vps-deployerbot
```

**Done.** Invite the bot, type `!deploy debian12`, get a VPS.

---

## ⚙️ Configuration

Edit `.env` after copying from `.env.example`:

```env
DISCORD_TOKEN=your_bot_token_here
PREFIX=!
ADMIN_ROLE=VPS Admin
LXC_BRIDGE=lxcbr0
LXC_ROOT=/var/lib/lxc
PINGGY_HOST=free.pinggy.io
DASHBOARD_PORT=5000
DASHBOARD_SECRET=change_me_to_something_random
DASHBOARD_OPEN=false
MAX_VPS_PER_USER=3
DEFAULT_CPU=1
DEFAULT_RAM=512
DEFAULT_DISK=5
```

| Variable | Description |
|---|---|
| `DISCORD_TOKEN` | Bot token from https://discord.com/developers/applications |
| `PREFIX` | Command prefix (default `!`) |
| `ADMIN_ROLE` | Role name that can use admin commands |
| `LXC_BRIDGE` | Linux bridge for containers (`lxcbr0` is the default) |
| `LXC_ROOT` | LXC storage path (`/var/lib/lxc`) |
| `PINGGY_HOST` | Pinggy endpoint (`free.pinggy.io` for free tier) |
| `DASHBOARD_PORT` | Web dashboard port |
| `DASHBOARD_SECRET` | Key needed to open the dashboard (unless `DASHBOARD_OPEN=true`) |
| `DASHBOARD_OPEN` | `true` = no key needed, `false` = key required |
| `MAX_VPS_PER_USER` | Cap per Discord user |
| `DEFAULT_CPU/RAM/DISK` | Defaults if user doesn't specify |

> ⚠️ **Enable Message Content Intent** in the Discord Developer Portal → your app → Bot → Privileged Gateway Intents. Without it, the bot can't read messages.

---

## 🎮 Commands

**150+ commands total.** Full list with `!help`.

### Deploy

```
!deploy <os> [cpu] [ram] [disk]   Deploy a new VPS with confirmation
!deploy ubuntu24 2 2048 20        Ubuntu 24.04, 2 CPU, 2 GB RAM, 20 GB disk
!quickdeploy <os>                 Skip confirmation, use defaults
!templates                        List all 14 available OS images
```

### VPS Management

```
!vps list                             Show your VPS
!vps info <name>                      Open the management panel
!vps start <name>                     Boot the container
!vps stop <name>                      Shut it down
!vps restart <name>                   Stop then start
!vps destroy <name>                   Delete permanently (asks to confirm)
!vps ssh <name>                       Print the SSH command
!vps tunnel <name>                    Open a fresh Pinggy tunnel
!vps console <name> <cmd>             Run a shell command inside
!vps stats <name>                     Live CPU/RAM/state
!vps ip <name>                        Show the container's IP
!vps freeze | unfreeze <name>         Pause / resume
!vps logs <name>                      Tail the container log
!vps note <name> <text>               Attach a note
!vps rename <name> <new>              Rename the container
!vps clone <name> <new>               Duplicate a container
!vps export <name>                    Export to tar.gz
```

### sshx (Browser Shell)

```
!vps sshx <name>            Install + start + return a browser URL
!vps sshx-read <name>       Show the current URL
!vps sshx-status <name>     Installed / running / URL
!vps sshx-stop <name>       Kill the sshx process
!vps sshx-restart <name>    New URL
```

### Snapshots

```
!snap create <name>          Snapshot the container
!snap list <name>            List snapshots
!snap restore <name> <snap>  Rollback
!snap del <name> <snap>      Delete a snapshot
```

### System

```
!ping            Latency
!uptime          Bot + host uptime
!sysinfo         Host hardware
!stats           Bot statistics
!df !free !ps    Disk / memory / processes
!netstat         Listening ports
!invite          Bot invite link
!dashboard       Dashboard URL
!help            Full command list
```

### Admin (requires Administrator or the ADMIN_ROLE)

```
!admin list                 All VPS across the server
!admin destroy <name>       Force destroy, no prompt
!admin audit [n]            Last N audit entries
!admin cleanup              Remove orphan DB records
!admin backup               Download vps.db
!broadcast <msg>            Announce to every guild
!reload                     Resync slash commands
!shutdown                   Stop the bot
```

---

## 🎛️ The VPS Panel

After deploying, the bot posts a panel with these buttons:

| Button | Action |
|---|---|
| ▶️ **Start** | Boot the container |
| ⏹️ **Stop** | Shut it down |
| 🔄 **Restart** | Stop → start |
| 🌐 **Tunnel** | Open a fresh Pinggy tunnel |
| ℹ️ **Info** | `lxc-info` output |
| 📊 **Stats** | Live CPU / RAM / state |
| 📸 **Snapshots** | List container snapshots |
| ⌨️ **Console** | Modal to run a shell command inside |
| 🔗 **sshx** | Start sshx, get a browser URL |
| 🗑️ **Destroy** | Permanent delete with a confirm dialog |

Every button updates the panel live.

---

## 🌐 Pinggy Tunnels

Pinggy exposes your container's SSH port to the public internet through a reverse tunnel.

**How it works:**

```bash
ssh -p 443 -R0:<container_ip>:22 -T tcp@free.pinggy.io
```

Pinggy returns a `tcp://host:port` URL. Anyone can SSH to it and land inside the container.

> ⚠️ **Critical:** the tunnel must point at the **container's IP**, not `localhost`. Otherwise the tunnel goes to the host, not the container.

**Connect from your laptop:**

```bash
ssh -p 41857 root@abc.pinggy-free.link
```

**Free tier limits:**

| Limit | Value |
|---|---|
| Session lifetime | **60 minutes** |
| Concurrent tunnels per IP | ~2 |
| Rate limit | A few per hour |
| Subdomain | Random, changes each restart |

**Auto-restart loop (defeats the 60-min limit):**

```bash
cat > /root/pinggy-loop.sh <<'EOF'
#!/bin/bash
IP=$(lxc-info -n YOUR_VPS_NAME -iH | head -1)
while true; do
  pkill -f "pinggy.*tcp@" 2>/dev/null; sleep 2
  ssh -p 443 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
      -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes \
      -R0:$IP:22 -T tcp@a.pinggy.io 2>&1 | tee /tmp/pinggy.log &
  for i in $(seq 1 30); do
    URL=$(grep -oE 'tcp://[^ ]+' /tmp/pinggy.log 2>/dev/null | head -1)
    [ -n "$URL" ] && echo "$URL" > /tmp/pinggy-url.txt && break
    sleep 1
  done
  sleep 3300
done
EOF
chmod +x /root/pinggy-loop.sh
nohup /root/pinggy-loop.sh > /tmp/pinggy-loop.log 2>&1 &
```

Read the current URL: `cat /tmp/pinggy-url.txt`

---

## 🔗 sshx — Browser Shell

The fastest way to get root inside any container. No SSH client, no password, no tunnel.

**From Discord (recommended):**

```
!vps sshx <name>
```

You get an ephemeral reply with a URL:

```
https://sshx.io/s/AbCdEf#XyZ123
```

Open it in any browser — full root shell inside the container.

**From the host:**

```bash
lxc-attach -n <name> -- bash -c \
  "setsid nohup sshx > /tmp/sshx.log 2>&1 < /dev/null & disown"
sleep 4
lxc-attach -n <name> -- cat /tmp/sshx.log
```

> ⚠️ The URL is unrestricted root access. Never share it in public channels or screenshots.

**Rotate the URL:**

```bash
bash -c "pkill sshx; sleep 1; setsid nohup sshx > /tmp/sshx.log 2>&1 < /dev/null & disown"
cat /tmp/sshx.log
```

---

## 📊 Web Dashboard

A Flask admin panel runs on port 5000 of the host.

**Access:**

```
http://<host-ip>:5000/                 # if DASHBOARD_OPEN=true
http://<host-ip>:5000/?key=YOUR_SECRET # if using a key
```

**Endpoints:**

| Path | Purpose |
|---|---|
| `/` | Main dashboard — table of all VPS with buttons |
| `/admin` | Admin panel — stats, logs, broadcast, destroy all |
| `/api` | JSON list of all VPS |
| `/vps/<name>` | JSON detail |
| `/action/<name>/start|stop|restart|destroy|tunnel` | Run an action |

**Expose via Pinggy:**

```bash
pkill -f 'pinggy.*5000'
nohup ssh -p 443 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  -o ServerAliveInterval=30 -R0:localhost:5000 free@a.pinggy.io \
  > /tmp/pinggy-dash.log 2>&1 &
sleep 5 && cat /tmp/pinggy-dash.log
```

> 🔒 **Security:** the dashboard has full control over every VPS. If `DASHBOARD_OPEN=true`, anyone with the URL can destroy everything. Use key mode, or put it behind Nginx + basic auth, or bind Flask to `127.0.0.1` and access via SSH tunnel.

---

## 🐧 Supported OS Templates

| Key | Pretty Name |
|---|---|
| `debian11` | Debian 11 Bullseye |
| `debian12` | Debian 12 Bookworm |
| `debian13` | Debian 13 Trixie |
| `ubuntu20` | Ubuntu 20.04 Focal |
| `ubuntu22` | Ubuntu 22.04 Jammy |
| `ubuntu24` | Ubuntu 24.04 Noble |
| `alma8` | AlmaLinux 8 |
| `alma9` | AlmaLinux 9 |
| `rocky9` | Rocky Linux 9 |
| `centos9` | CentOS Stream 9 |
| `fedora40` | Fedora 40 |
| `arch` | Arch Linux |
| `kali` | Kali Rolling |
| `opensuse` | openSUSE Leap 15.5 |

Add your own in the `SUPPORTED` dict inside `bot.py`.

---

## 🐛 Troubleshooting

<details>
<summary><b>ensurepip is not available — venv creation fails</b></summary>

```bash
apt install -y python3-full python3.12-venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```
</details>

<details>
<summary><b>externally-managed-environment when installing pip packages</b></summary>

PEP 668 blocks system pip. Use a venv:

```bash
cd /root/vps-deployerbot
source venv/bin/activate
pip install -r requirements.txt
```

Never use `--break-system-packages`.
</details>

<details>
<summary><b>No module named 'discord'</b></summary>

Wrong Python. Use the venv one:

```bash
sudo /root/vps-deployerbot/venv/bin/python /root/vps-deployerbot/bot.py
```
</details>

<details>
<summary><b>Device "lxcbr0" does not exist</b></summary>

```bash
apt install --reinstall -y lxc-net dnsmasq
systemctl enable --now lxc-net
systemctl restart lxc-net
ip addr show lxcbr0
```
</details>

<details>
<summary><b>lxc-attach: Failed to get init pid</b></summary>

Container isn't running:

```bash
lxc-info -n <name>
lxc-start -n <name> -d
sleep 5
lxc-attach -n <name>
```
</details>

<details>
<summary><b>Connection closed by &lt;ip&gt; port XXXX</b></summary>

sshd inside the container is missing host keys:

```bash
lxc-attach -n <name>
apt update && apt install -y openssh-server
ssh-keygen -A       # ← the missing piece
echo 'root:YourPass123' | chpasswd
sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
/usr/sbin/sshd
exit
```
</details>

<details>
<summary><b>Connection reset by 172.236.148.125</b></summary>

Pinggy tunnel expired or container stopped. Regenerate:

```
!vps tunnel <name>
```
</details>

<details>
<summary><b>systemctl: Unit vps-deployerbot.service not found</b></summary>

```bash
sudo cp systemd/vps-deployerbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now vps-deployerbot
```
</details>

<details>
<summary><b>Bot crash loop</b></summary>

```bash
journalctl -u vps-deployerbot -n 40 --no-pager
# or run in foreground:
/root/vps-deployerbot/venv/bin/python /root/vps-deployerbot/bot.py
```
</details>

Full error list in the [docs site](#) or in `errors.html`.

---

## ❓ FAQ

<details>
<summary>Can I run this on a free host?</summary>

No free tier supports nested LXC with root. **Oracle Cloud Always Free** (ARM, 12 GB RAM) is the closest. **Hetzner CX22** at ~€4/mo is the cheapest reliable paid option.
</details>

<details>
<summary>How many VPS can it run?</summary>

Depends on host RAM. Each 512 MB VPS uses 512 MB. A 4 GB host handles ~6 comfortably. Set `MAX_VPS_PER_USER` and per-guild caps.
</details>

<details>
<summary>Can I make the bot public?</summary>

Yes. Enable **Public Bot** in the Discord Developer Portal → Bot. But you MUST add role-gating or anyone can fill your disk. Or give people the repo and let them self-host.
</details>

<details>
<summary>Why does Pinggy keep disconnecting?</summary>

Free tier kills tunnels after 60 minutes. Run the auto-restart loop, upgrade to Pinggy Pro, or switch to sshx.
</details>

<details>
<summary>Where are the containers stored?</summary>

`/var/lib/lxc/<container-name>/`. Rootfs at `rootfs/`, config at `config`.
</details>

---

## 📁 Project Structure

```
vps-deployerbot/
├── bot.py                      # The entire bot (single file)
├── requirements.txt
├── .env                        # Your secrets (gitignored)
├── .env.example                # Template
├── .gitignore
├── README.md
├── LICENSE
├── systemd/
│   └── vps-deployerbot.service
└── vps.db                      # SQLite (auto-created)
```

---

## 🗺 Roadmap

- [ ] Slash command coverage for every prefix command
- [ ] KVM support (real virtualization, not just containers)
- [ ] Multi-node cluster (deploy across several hosts)
- [ ] OAuth2 login for the dashboard
- [ ] Public API with rate limiting
- [ ] Web-based VNC console

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/amazing`
3. Commit: `git commit -m "add amazing feature"`
4. Push: `git push origin feature/amazing`
5. Open a Pull Request

Keep it clean, keep it working.

---

## 📜 License

MIT — see [LICENSE](LICENSE).

You can use this commercially. You can't claim you wrote it. Keep the credits.

---

## 💖 Credits

| Role | Name |
|---|---|
| Original author | **Vasplayz90** |
| Organization | **ArizNodesLabs** |
| Container engine | [LXC](https://linuxcontainers.org/) |
| Tunnel service | [Pinggy.io](https://pinggy.io/) |
| Browser shell | [sshx](https://sshx.io/) |
| Discord library | [discord.py](https://github.com/Rapptz/discord.py) |

---

<div align="center">

**ArizNodesLabs × Vasplayz90**

*Deploy VPS from Discord. Because why not.*

[⭐ Star this repo](https://github.com/ariznodes-og/vps-deployerbot) if it helped

</div>
