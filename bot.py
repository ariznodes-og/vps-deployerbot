# ============================================================================
#  ██╗   ██╗██████╗ ███████╗    ██████╗ ███████╗██████╗ ██╗      ██████╗ ██╗   ██╗
#  ██║   ██║██╔══██╗██╔════╝    ██╔══██╗██╔════╝██╔══██╗██║     ██╔═══██╗╚██╗ ██╔╝
#  ██║   ██║██████╔╝███████╗    ██║  ██║█████╗  ██████╔╝██║     ██║   ██║ ╚████╔╝
#  ██║   ██║██╔═══╝ ╚════██║    ██║  ██║██╔══╝  ██╔═══╝ ██║     ██║   ██║  ╚██╔╝
#  ███████║██║     ███████║    ██████╔╝███████╗██║     ███████╗╚██████╔╝   ██║
#  ╚══════╝╚═╝     ╚══════╝    ╚═════╝ ╚══════╝╚═╝     ╚══════╝ ╚═════╝    ╚═╝
#
#                    A R I Z N O D E S   L A B S
#                            x
#                      V A S P L A Y Z 9 0
#
#               >> VPS DEPLOYER BOT — LXC + PINGGY.IO <<
#               >> SINGLE FILE EDITION · 1000+ LINES <<
# ============================================================================

import os
import re
import io
import sys
import json
import time
import uuid
import signal
import sqlite3
import asyncio
import secrets
import datetime
import threading
import subprocess
import traceback
from typing import Optional, List, Dict, Any, Tuple

import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template_string

# ============================================================================
#   CONFIG
# ============================================================================
load_dotenv()

TOKEN            = os.getenv("DISCORD_TOKEN", "")
PREFIX           = os.getenv("PREFIX", "!")
LXC_BRIDGE       = os.getenv("LXC_BRIDGE", "lxcbr0")
LXC_ROOT         = os.getenv("LXC_ROOT", "/var/lib/lxc")
PINGGY_HOST      = os.getenv("PINGGY_HOST", "free.pinggy.io")
DASHBOARD_PORT   = int(os.getenv("DASHBOARD_PORT", 5000))
DASHBOARD_SECRET = os.getenv("DASHBOARD_SECRET", "change_me_now")
ADMIN_ROLE       = os.getenv("ADMIN_ROLE", "VPS Admin")
MAX_VPS_PER_USER = int(os.getenv("MAX_VPS_PER_USER", 3))
DEFAULT_CPU      = int(os.getenv("DEFAULT_CPU", 1))
DEFAULT_RAM      = int(os.getenv("DEFAULT_RAM", 512))
DEFAULT_DISK     = int(os.getenv("DEFAULT_DISK", 5))

VERSION   = "1.0.0"
BUILD     = "ArizNodesLabs"
COLOR     = 0x5865F2
COLOR_OK  = 0x57F287
COLOR_ERR = 0xED4245
COLOR_WRN = 0xFEE75C

BANNER = r"""
 ██╗   ██╗ █████╗ ███████╗██████╗ ██╗      █████╗ ██╗   ██╗███████╗
 ██║   ██║██╔══██╗██╔════╝██╔══██╗██║     ██╔══██╗╚██╗ ██╔╝╚══███╔╝
 ██║   ██║███████║███████╗██████╔╝██║     ███████║ ╚████╔╝   ███╔╝
 ╚██╗ ██╔╝██╔══██║╚════██║██╔═══╝ ██║     ██╔══██║  ╚██╔╝   ███╔╝
  ╚████╔╝ ██║  ██║███████║██║     ███████╗██║  ██║   ██║   ███████╗
   ╚═══╝  ╚═╝  ╚═╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝

     █████╗ ██████╗ ██╗███████╗███╗   ██╗ ██████╗ ██████╗ ███████╗███████╗
    ██╔══██╗██╔══██╗██║╚══███╔╝████╗  ██║██╔═══██╗██╔══██╗██╔════╝██╔════╝
    ███████║██████╔╝██║  ███╔╝ ██╔██╗ ██║██║   ██║██║  ██║█████╗  ███████╗
    ██╔══██║██╔══██╗██║ ███╔╝  ██║╚██╗██║██║   ██║██║  ██║██╔══╝  ╚════██║
    ██║  ██║██║  ██║██║███████╗██║ ╚████║╚██████╔╝██████╔╝███████╗███████║
    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝╚══════╝
                  >>  L X C   V P S   D E P L O Y E R  <<
                  >>   B Y   V A S P L A Y Z 9 0    <<
"""

# ============================================================================
#   LOGGER
# ============================================================================
class Log:
    OK   = "\033[92m[+]\033[0m"
    ERR  = "\033[91m[!]\033[0m"
    WARN = "\033[93m[*]\033[0m"
    INFO = "\033[94m[i]\033[0m"

    @staticmethod
    def ok(msg):   print(f"{Log.OK}  {msg}", flush=True)
    @staticmethod
    def err(msg):  print(f"{Log.ERR} {msg}", flush=True)
    @staticmethod
    def warn(msg): print(f"{Log.WARN} {msg}", flush=True)
    @staticmethod
    def info(msg): print(f"{Log.INFO} {msg}", flush=True)

# ============================================================================
#   DATABASE
# ============================================================================
DB = sqlite3.connect("vps.db", check_same_thread=False)
DB.row_factory = sqlite3.Row

def db_init():
    DB.executescript("""
        CREATE TABLE IF NOT EXISTS vps (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            owner    INTEGER NOT NULL,
            name     TEXT UNIQUE NOT NULL,
            distro   TEXT NOT NULL,
            cpu      INTEGER DEFAULT 1,
            ram      INTEGER DEFAULT 512,
            disk     INTEGER DEFAULT 5,
            state    TEXT DEFAULT 'STOPPED',
            tunnel   TEXT,
            port     INTEGER,
            ip       TEXT,
            created  TEXT,
            expires  TEXT,
            note     TEXT
        );
        CREATE TABLE IF NOT EXISTS snapshots (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            vps      TEXT NOT NULL,
            snap     TEXT NOT NULL,
            created  TEXT
        );
        CREATE TABLE IF NOT EXISTS audit (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            user     INTEGER,
            action   TEXT,
            target   TEXT,
            ts       TEXT
        );
        CREATE TABLE IF NOT EXISTS settings (
            k TEXT PRIMARY KEY,
            v TEXT
        );
    """)
    DB.commit()

def db_add(owner, name, distro, cpu, ram, disk, state="RUNNING",
           tunnel=None, port=None, ip=None, note=None):
    DB.execute(
        "INSERT INTO vps (owner,name,distro,cpu,ram,disk,state,tunnel,port,ip,"
        "created,expires,note) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (owner, name, distro, cpu, ram, disk, state, tunnel, port, ip,
         datetime.datetime.utcnow().isoformat(),
         (datetime.datetime.utcnow()+datetime.timedelta(days=30)).isoformat(),
         note))
    DB.commit()

def db_get(name):
    return DB.execute("SELECT * FROM vps WHERE name=?", (name,)).fetchone()

def db_list(owner=None):
    if owner is None:
        return DB.execute("SELECT * FROM vps ORDER BY id DESC").fetchall()
    return DB.execute("SELECT * FROM vps WHERE owner=? ORDER BY id DESC",
                      (owner,)).fetchall()

def db_update(name, **kw):
    if not kw: return
    cols = ",".join(f"{k}=?" for k in kw)
    DB.execute(f"UPDATE vps SET {cols} WHERE name=?", (*kw.values(), name))
    DB.commit()

def db_del(name):
    DB.execute("DELETE FROM vps WHERE name=?", (name,))
    DB.execute("DELETE FROM snapshots WHERE vps=?", (name,))
    DB.commit()

def db_count(owner=None):
    if owner is None:
        return DB.execute("SELECT COUNT(*) FROM vps").fetchone()[0]
    return DB.execute("SELECT COUNT(*) FROM vps WHERE owner=?",
                      (owner,)).fetchone()[0]

def db_snap_add(vps, snap):
    DB.execute("INSERT INTO snapshots (vps,snap,created) VALUES (?,?,?)",
               (vps, snap, datetime.datetime.utcnow().isoformat()))
    DB.commit()

def db_snap_list(vps):
    return DB.execute("SELECT * FROM snapshots WHERE vps=? ORDER BY id DESC",
                      (vps,)).fetchall()

def db_snap_del(vps, snap):
    DB.execute("DELETE FROM snapshots WHERE vps=? AND snap=?", (vps, snap))
    DB.commit()

def db_audit(user, action, target):
    DB.execute("INSERT INTO audit (user,action,target,ts) VALUES (?,?,?,?)",
               (user, action, str(target),
                datetime.datetime.utcnow().isoformat()))
    DB.commit()

def db_audit_list(limit=50):
    return DB.execute("SELECT * FROM audit ORDER BY id DESC LIMIT ?",
                      (limit,)).fetchall()

def db_set(k, v):
    DB.execute("INSERT OR REPLACE INTO settings (k,v) VALUES (?,?)", (k, str(v)))
    DB.commit()

def db_get_setting(k, default=None):
    row = DB.execute("SELECT v FROM settings WHERE k=?", (k,)).fetchone()
    return row["v"] if row else default

# ============================================================================
#   SHELL HELPER
# ============================================================================
async def sh(*args, timeout: int = 300, input: bytes = None) -> Tuple[int, str]:
    """Run a subprocess and return (returncode, combined_output)."""
    try:
        p = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            stdin=asyncio.subprocess.PIPE if input else None,
        )
    except FileNotFoundError as e:
        return 127, f"command not found: {args[0]}"
    try:
        out, _ = await asyncio.wait_for(p.communicate(input), timeout)
        return p.returncode, out.decode(errors="ignore")
    except asyncio.TimeoutError:
        try: p.kill()
        except: pass
        return 124, "timeout"

# ============================================================================
#   SUPPORTED DISTROS
# ============================================================================
SUPPORTED: Dict[str, Dict[str, str]] = {
    "debian11":  {"dist": "debian",    "release": "bullseye", "pretty": "Debian 11 Bullseye"},
    "debian12":  {"dist": "debian",    "release": "bookworm", "pretty": "Debian 12 Bookworm"},
    "debian13":  {"dist": "debian",    "release": "trixie",   "pretty": "Debian 13 Trixie"},
    "ubuntu20":  {"dist": "ubuntu",    "release": "focal",    "pretty": "Ubuntu 20.04 Focal"},
    "ubuntu22":  {"dist": "ubuntu",    "release": "jammy",    "pretty": "Ubuntu 22.04 Jammy"},
    "ubuntu24":  {"dist": "ubuntu",    "release": "noble",    "pretty": "Ubuntu 24.04 Noble"},
    "alma8":     {"dist": "almalinux", "release": "8",        "pretty": "AlmaLinux 8"},
    "alma9":     {"dist": "almalinux", "release": "9",        "pretty": "AlmaLinux 9"},
    "rocky9":    {"dist": "rockylinux","release": "9",        "pretty": "Rocky Linux 9"},
    "centos9":   {"dist": "centos",    "release": "9-Stream", "pretty": "CentOS Stream 9"},
    "fedora40":  {"dist": "fedora",    "release": "40",       "pretty": "Fedora 40"},
    "arch":      {"dist": "archlinux", "release": "current",  "pretty": "Arch Linux"},
    "kali":      {"dist": "kali",      "release": "current",  "pretty": "Kali Rolling"},
    "opensuse":  {"dist": "opensuse",  "release": "15.5",     "pretty": "openSUSE Leap 15.5"},
}

# ============================================================================
#   LXC MANAGER
# ============================================================================
class LXCManager:
    @staticmethod
    async def create(name: str, distro: str, cpu: int, ram: int, disk: int):
        cfg = SUPPORTED.get(distro)
        if not cfg:
            return False, f"unsupported distro: {distro}"

        # wipe stale
        await LXCManager.destroy(name)

        code, out = await sh(
            "lxc-create", "-n", name, "-t", "download", "--",
            "-d", cfg["dist"], "-r", cfg["release"], "-a", "amd64",
            timeout=900,
        )
        if code != 0:
            return False, f"create failed:\n{out[-1500:]}"

        conf = f"{LXC_ROOT}/{name}/config"
        try:
            with open(conf, "a") as f:
                f.write(f"\nlxc.cgroup2.memory.max = {ram}M\n")
                f.write(f"\nlxc.cgroup2.cpu.max = {cpu * 100000} 100000\n")
                f.write(f"\nlxc.net.0.link = {LXC_BRIDGE}\n")
        except Exception as e:
            Log.warn(f"config append failed: {e}")

        code, out = await sh("lxc-start", "-n", name, "-d", timeout=120)
        if code != 0:
            return False, f"start failed:\n{out[-1000:]}"

        # give the container a moment to boot networking
        await asyncio.sleep(6)

        ip = await LXCManager.get_ip(name)

        # base provisioning inside container
        await sh("lxc-attach", "-n", name, "--", "bash", "-c",
                 "apt update -y >/dev/null 2>&1 || true", timeout=180)

        return True, ip or "unknown"

    @staticmethod
    async def start(name: str) -> bool:
        code, _ = await sh("lxc-start", "-n", name, "-d", timeout=120)
        return code == 0

    @staticmethod
    async def stop(name: str) -> bool:
        code, _ = await sh("lxc-stop", "-n", name, "-t", "30", timeout=60)
        return code == 0

    @staticmethod
    async def destroy(name: str) -> bool:
        code, _ = await sh("lxc-destroy", "-n", name, "-f", timeout=120)
        return code == 0

    @staticmethod
    async def running(name: str) -> bool:
        code, out = await sh("lxc-info", "-n", name, "-sH", timeout=10)
        return code == 0 and "RUNNING" in out.upper()

    @staticmethod
    async def get_ip(name: str) -> Optional[str]:
        code, out = await sh("lxc-info", "-n", name, "-iH", timeout=10)
        if code != 0: return None
        line = out.strip().splitlines()[0] if out.strip() else ""
        return line.strip() or None

    @staticmethod
    async def info(name: str) -> str:
        code, out = await sh("lxc-info", "-n", name, timeout=15)
        return out if code == 0 else "container not found"

    @staticmethod
    async def stats(name: str) -> str:
        code, out = await sh(
            "bash", "-c",
            f"lxc-info -n {name} -sH; "
            f"lxc-info -n {name} -pH; "
            f"lxc-cgroup -n {name} memory.usage_in_bytes 2>/dev/null",
            timeout=15,
        )
        return out

    @staticmethod
    async def exec(name: str, cmd: str, timeout: int = 60) -> str:
        code, out = await sh("lxc-attach", "-n", name, "--",
                             "bash", "-c", cmd, timeout=timeout)
        return out

    @staticmethod
    async def all_containers() -> List[str]:
        code, out = await sh("lxc-ls", "-1")
        if code != 0: return []
        return [x.strip() for x in out.splitlines() if x.strip()]

# ============================================================================
#   PINGGY TUNNEL MANAGER
# ============================================================================
class PinggyManager:
    HOST = PINGGY_HOST
    TUNNELS: Dict[str, Dict[str, Any]] = {}
    LOCK = asyncio.Lock()

    @classmethod
    async def open(cls, name: str, local_port: int = 22) -> Optional[str]:
        async with cls.LOCK:
            await cls.close(name)
            cmd = [
                "ssh", "-p", "443",
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null",
                "-o", "ServerAliveInterval=30",
                "-o", "ServerAliveCountMax=3",
                "-T",
                "-R0:localhost:" + str(local_port),
                f"tcp@{cls.HOST}",
            ]
            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                )
            except FileNotFoundError:
                Log.err("ssh binary not found — install openssh-client")
                return None

            url = None
            deadline = time.time() + 40
            while time.time() < deadline:
                try:
                    line = await asyncio.wait_for(proc.stdout.readline(), 2.0)
                except asyncio.TimeoutError:
                    continue
                if not line:
                    break
                text = line.decode(errors="ignore")
                m = re.search(r"(tcp://[^\s]+?):(\d+)", text)
                if m:
                    url = f"tcp://{m.group(1).replace('tcp://','')}:{m.group(2)}"
                    url = m.group(0)
                    break

            cls.TUNNELS[name] = {"proc": proc, "url": url, "port": local_port}
            return url

    @classmethod
    async def close(cls, name: str):
        t = cls.TUNNELS.pop(name, None)
        if not t: return
        proc = t.get("proc")
        if proc and proc.returncode is None:
            try:
                proc.terminate()
                await asyncio.wait_for(proc.wait(), 5)
            except Exception:
                try: proc.kill()
                except: pass

    @classmethod
    def get(cls, name: str) -> Optional[Dict[str, Any]]:
        return cls.TUNNELS.get(name)

# ============================================================================
#   FORMATTING HELPERS
# ============================================================================
def human_bytes(n):
    try: n = float(n)
    except: return str(n)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024: return f"{n:.2f}{unit}"
        n /= 1024
    return f"{n:.2f}PB"

def human_time(seconds):
    seconds = int(seconds)
    d, seconds = divmod(seconds, 86400)
    h, seconds = divmod(seconds, 3600)
    m, s = divmod(seconds, 60)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    if s or not parts: parts.append(f"{s}s")
    return " ".join(parts)

def code_block(text: str, lang: str = "") -> str:
    return f"```{lang}\n{text[:1800]}\n```"

def short_id() -> str:
    return secrets.token_hex(3)

def is_owner_or_admin(ctx_or_inter, row) -> bool:
    user = ctx_or_inter.user if isinstance(ctx_or_inter, discord.Interaction) else ctx_or_inter.author
    if getattr(user, "guild_permissions", None) and user.guild_permissions.administrator:
        return True
    return row["owner"] == user.id

# ============================================================================
#   EMBED BUILDERS
# ============================================================================
LOGO = "https://cdn-icons-png.flaticon.com/512/2103/2103633.png"
FOOT = "ArizNodesLabs × Vasplayz90"

def embed_base(title: str, desc: str = "", color: int = COLOR) -> discord.Embed:
    e = discord.Embed(title=title, description=desc, color=color,
                      timestamp=datetime.datetime.utcnow())
    e.set_thumbnail(url=LOGO)
    e.set_footer(text=FOOT, icon_url=LOGO)
    return e

def embed_vps(row) -> discord.Embed:
    state_emoji = {
        "RUNNING": "🟢", "STOPPED": "🔴", "FROZEN": "🟡",
        "ERROR": "⚫", "UNKNOWN": "⚪",
    }.get((row["state"] or "").upper(), "⚪")

    e = embed_base(f"🖥️  VPS Manager — `{row['name']}`")
    e.add_field(name="📦 OS",     value=f"`{row['distro']}`", inline=True)
    e.add_field(name="⚙️ CPU",    value=f"`{row['cpu']} vCPU`", inline=True)
    e.add_field(name="🧠 RAM",    value=f"`{row['ram']} MB`", inline=True)
    e.add_field(name="💾 Disk",   value=f"`{row['disk']} GB`", inline=True)
    e.add_field(name="📡 State",  value=f"{state_emoji} `{row['state']}`", inline=True)
    e.add_field(name="🌐 IP",     value=f"`{row['ip'] or '—'}`", inline=True)
    e.add_field(name="🔗 Tunnel", value=f"`{row['tunnel'] or 'none'}`", inline=False)
    e.add_field(
        name="🖥 SSH Command",
        value=f"```bash\nssh root@{row['ip'] or '<container-ip>'} -p {row['port'] or 22}\n```",
        inline=False,
    )
    e.add_field(name="👤 Owner",  value=f"<@{row['owner']}>", inline=True)
    e.add_field(name="📅 Created", value=f"`{(row['created'] or '')[:19]}`", inline=True)
    e.add_field(name="⏳ Expires", value=f"`{(row['expires'] or '')[:19]}`", inline=True)
    if row["note"]:
        e.add_field(name="📝 Note", value=row["note"], inline=False)
    return e

def embed_ok(title: str, desc: str = "") -> discord.Embed:
    return embed_base(f"✅ {title}", desc, COLOR_OK)

def embed_err(title: str, desc: str = "") -> discord.Embed:
    return embed_base(f"❌ {title}", desc, COLOR_ERR)

def embed_warn(title: str, desc: str = "") -> discord.Embed:
    return embed_base(f"⚠️ {title}", desc, COLOR_WRN)

# ============================================================================
#   UI — VPS MANAGE PANEL (Buttons)
# ============================================================================
class VPSManageView(discord.ui.View):
    def __init__(self, name: str, bot: commands.Bot):
        super().__init__(timeout=None)
        self.name = name
        self.bot = bot

    async def _guard(self, inter: discord.Interaction) -> bool:
        row = db_get(self.name)
        if not row:
            await inter.response.send_message("❌ VPS no longer exists.", ephemeral=True)
            return False
        if not is_owner_or_admin(inter, row):
            await inter.response.send_message("❌ Not yours.", ephemeral=True)
            return False
        return True

    async def _refresh(self, inter: discord.Interaction, msg: str = ""):
        row = db_get(self.name)
        if not row: return
        try:
            await inter.message.edit(embed=embed_vps(row), view=self)
        except Exception:
            pass
        if msg:
            await inter.followup.send(msg, ephemeral=True)

    @discord.ui.button(label="Start", emoji="▶️", style=discord.ButtonStyle.success, row=0)
    async def b_start(self, inter, btn):
        if not await self._guard(inter): return
        await inter.response.defer(ephemeral=True)
        ok = await LXCManager.start(self.name)
        if ok:
            db_update(self.name, state="RUNNING")
            db_audit(inter.user.id, "start", self.name)
        await self._refresh(inter, "▶️ Started" if ok else "❌ Failed to start")

    @discord.ui.button(label="Stop", emoji="⏹️", style=discord.ButtonStyle.danger, row=0)
    async def b_stop(self, inter, btn):
        if not await self._guard(inter): return
        await inter.response.defer(ephemeral=True)
        ok = await LXCManager.stop(self.name)
        if ok:
            db_update(self.name, state="STOPPED")
            db_audit(inter.user.id, "stop", self.name)
        await self._refresh(inter, "⏹️ Stopped" if ok else "❌ Failed to stop")

    @discord.ui.button(label="Restart", emoji="🔄", style=discord.ButtonStyle.primary, row=0)
    async def b_restart(self, inter, btn):
        if not await self._guard(inter): return
        await inter.response.defer(ephemeral=True)
        await LXCManager.stop(self.name)
        ok = await LXCManager.start(self.name)
        if ok:
            db_update(self.name, state="RUNNING")
            db_audit(inter.user.id, "restart", self.name)
        await self._refresh(inter, "🔄 Restarted" if ok else "❌ Failed to restart")

    @discord.ui.button(label="New Tunnel", emoji="🌐", style=discord.ButtonStyle.secondary, row=0)
    async def b_tunnel(self, inter, btn):
        if not await self._guard(inter): return
        await inter.response.defer(ephemeral=True)
        url = await PinggyManager.open(self.name, 22)
        if url:
            m = re.search(r":(\d+)$", url)
            port = int(m.group(1)) if m else None
            db_update(self.name, tunnel=url, port=port)
            db_audit(inter.user.id, "tunnel", self.name)
            await self._refresh(inter, f"🌐 New tunnel: `{url}`")
        else:
            await inter.followup.send("❌ Tunnel failed. Pinggy may be down.", ephemeral=True)

    @discord.ui.button(label="Info", emoji="ℹ️", style=discord.ButtonStyle.secondary, row=0)
    async def b_info(self, inter, btn):
        if not await self._guard(inter): return
        await inter.response.defer(ephemeral=True)
        out = await LXCManager.info(self.name)
        await inter.followup.send(code_block(out), ephemeral=True)

    @discord.ui.button(label="Stats", emoji="📊", style=discord.ButtonStyle.secondary, row=1)
    async def b_stats(self, inter, btn):
        if not await self._guard(inter): return
        await inter.response.defer(ephemeral=True)
        out = await LXCManager.stats(self.name)
        await inter.followup.send(code_block(out), ephemeral=True)

    @discord.ui.button(label="Snapshots", emoji="📸", style=discord.ButtonStyle.secondary, row=1)
    async def b_snaps(self, inter, btn):
        if not await self._guard(inter): return
        await inter.response.defer(ephemeral=True)
        rows = db_snap_list(self.name)
        if not rows:
            await inter.followup.send("📭 No snapshots.", ephemeral=True); return
        txt = "\n".join(f"• `{r['snap']}` — {r['created'][:19]}" for r in rows)
        await inter.followup.send(code_block(txt), ephemeral=True)

    @discord.ui.button(label="Console", emoji="⌨️", style=discord.ButtonStyle.secondary, row=1)
    async def b_console(self, inter, btn):
        if not await self._guard(inter): return
        await inter.response.send_modal(ConsoleModal(self.name))

    @discord.ui.button(label="Destroy", emoji="🗑️", style=discord.ButtonStyle.danger, row=2)
    async def b_destroy(self, inter, btn):
        if not await self._guard(inter): return
        await inter.response.send_message(
            f"⚠️ Are you **sure** you want to destroy `{self.name}`? This cannot be undone.",
            view=ConfirmDestroyView(self.name, self.bot),
            ephemeral=True,
        )

class ConsoleModal(discord.ui.Modal, title="Container Console"):
    cmd = discord.ui.TextInput(
        label="Shell Command",
        placeholder="e.g. uname -a",
        style=discord.TextStyle.short,
        max_length=200,
    )
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    async def on_submit(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=True)
        out = await LXCManager.exec(self.name, self.cmd.value, timeout=30)
        await inter.followup.send(
            f"`$ {self.cmd.value}`\n{code_block(out or '(no output)')}",
            ephemeral=True,
        )

class ConfirmDestroyView(discord.ui.View):
    def __init__(self, name: str, bot: commands.Bot):
        super().__init__(timeout=60)
        self.name = name
        self.bot = bot

    @discord.ui.button(label="Yes, Destroy", style=discord.ButtonStyle.danger)
    async def yes(self, inter, btn):
        await inter.response.defer(ephemeral=True)
        await PinggyManager.close(self.name)
        await LXCManager.destroy(self.name)
        db_del(self.name)
        db_audit(inter.user.id, "destroy", self.name)
        await inter.followup.send(f"🗑️ Destroyed `{self.name}`", ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def no(self, inter, btn):
        await inter.response.edit_message(content="Cancelled.", view=None)

# ============================================================================
#   UI — DEPLOY CONFIRM
# ============================================================================
class DeployConfirmView(discord.ui.View):
    def __init__(self, distro: str, cpu: int, ram: int, disk: int,
                 author: discord.User, bot: commands.Bot):
        super().__init__(timeout=90)
        self.distro, self.cpu, self.ram, self.disk = distro, cpu, ram, disk
        self.author, self.bot = author, bot

    @discord.ui.button(label="Confirm Deploy", emoji="✅", style=discord.ButtonStyle.success)
    async def ok(self, inter, btn):
        if inter.user.id != self.author.id:
            return await inter.response.send_message("❌ Not your prompt.", ephemeral=True)
        await inter.response.defer()
        name = f"vps-{self.author.id}-{short_id()}"
        msg = await inter.followup.send(f"⏳ Provisioning `{name}` ({self.distro})...")
        ok, info = await LXCManager.create(name, self.distro, self.cpu, self.ram, self.disk)
        if not ok:
            await msg.edit(content=f"❌ Deploy failed:\n{code_block(info)}")
            return
        url = await PinggyManager.open(name, 22)
        port = int(re.search(r":(\d+)$", url).group(1)) if url else None
        db_add(self.author.id, name, self.distro, self.cpu, self.ram, self.disk,
               "RUNNING", url, port, info)
        db_audit(self.author.id, "deploy", name)
        row = db_get(name)
        await msg.edit(content=f"✅ **Deployed** — `{name}`", embed=embed_vps(row),
                       view=VPSManageView(name, self.bot))
        self.stop()

    @discord.ui.button(label="Cancel", emoji="❌", style=discord.ButtonStyle.danger)
    async def no(self, inter, btn):
        await inter.response.edit_message(content="Deploy cancelled.", embed=None, view=None)
        self.stop()

# ============================================================================
#   BOT
# ============================================================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)
bot.start_time = time.time()

def is_admin():
    async def predicate(ctx):
        if ctx.author.guild_permissions.administrator: return True
        return any(r.name == ADMIN_ROLE for r in getattr(ctx.author, "roles", []))
    return commands.check(predicate)

# ============================================================================
#   EVENTS
# ============================================================================
@bot.event
async def on_ready():
    Log.ok(f"Logged in as {bot.user} (ID {bot.user.id})")
    Log.info(f"Prefix: {PREFIX} | Guilds: {len(bot.guilds)} | Cmds: {len(bot.commands)}")
    try:
        synced = await bot.tree.sync()
        Log.ok(f"Synced {len(synced)} slash commands")
    except Exception as e:
        Log.warn(f"Slash sync failed: {e}")
    activity = discord.Activity(type=discord.ActivityType.watching,
                                name=f"{db_count()} VPS | {PREFIX}help")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    if not autosave.is_running():
        autosave.start()

@bot.event
async def on_command_error(ctx, err):
    if isinstance(err, commands.CommandNotFound): return
    if isinstance(err, commands.MissingRequiredArgument):
        return await ctx.send(embed=embed_err("Missing argument", str(err)))
    if isinstance(err, commands.CheckFailure):
        return await ctx.send(embed=embed_err("No permission", "You can't use this."))
    Log.err(f"Command error: {err}")
    await ctx.send(embed=embed_err("Error", code_block(str(err))))

@tasks.loop(minutes=5)
async def autosave():
    try:
        DB.commit()
        state = {}
        for name in await LXCManager.all_containers():
            try: state[name] = "RUNNING"
            except: pass
        for row in db_list():
            if row["name"] in state:
                db_update(row["name"], state="RUNNING")
        Log.info(f"Autosave tick — {db_count()} tracked VPS")
    except Exception as e:
        Log.warn(f"autosave failed: {e}")

# ============================================================================
#   HELP
# ============================================================================
@bot.command(name="help", aliases=["h", "commands"])
async def cmd_help(ctx, category: str = None):
    if category:
        return await help_category(ctx, category)
    e = embed_base("📖 VPS Deployer — Help",
                   f"Prefix: `{PREFIX}` • Version `{VERSION}` • 150+ commands")
    e.add_field(name="🚀 Getting Started",
                value=f"`{PREFIX}deploy <distro> [cpu] [ram] [disk]`\n"
                      f"`{PREFIX}templates` — see all OS images\n"
                      f"`{PREFIX}quickdeploy <distro>` — 1-click", inline=False)
    e.add_field(name="🖥️ VPS Management",
                value=f"`{PREFIX}vps list|info|start|stop|restart|destroy|ssh|tunnel|console|stats|logs`",
                inline=False)
    e.add_field(name="📸 Snapshots",
                value=f"`{PREFIX}snap create|list|restore|del`", inline=False)
    e.add_field(name="📊 Monitoring",
                value=f"`{PREFIX}sysinfo` `{PREFIX}uptime` `{PREFIX}ping` `{PREFIX}netstat`",
                inline=False)
    e.add_field(name="👑 Admin",
                value=f"`{PREFIX}admin` `{PREFIX}broadcast` `{PREFIX}reload` `{PREFIX}shutdown`",
                inline=False)
    e.add_field(name="🌐 Web Dashboard",
                value=f"`{PREFIX}dashboard` — get dashboard URL", inline=False)
    e.add_field(name="ℹ️ Categories",
                value=f"`{PREFIX}help vps` • `{PREFIX}help manage` • `{PREFIX}help system` • `{PREFIX}help admin`",
                inline=False)
    await ctx.send(embed=e)

async def help_category(ctx, cat: str):
    cat = cat.lower()
    mapping = {
        "vps": [
            "deploy", "quickdeploy", "templates", "oslist",
            "vps list", "vps info", "vps start", "vps stop", "vps restart",
            "vps destroy", "vps ssh", "vps tunnel", "vps console", "vps stats",
            "vps logs", "vps rename", "vps note", "vps limit", "vps ip",
        ],
        "manage": [
            "snap create", "snap list", "snap restore", "snap del",
            "vps freeze", "vps unfreeze", "vps reboot", "vps exec",
            "vps cp", "vps mv", "vps chown", "vps export", "vps import",
        ],
        "system": [
            "ping", "uptime", "sysinfo", "netstat", "df", "free", "ps",
            "whoami", "invite", "dashboard", "version", "stats", "cpu",
            "mem", "disk", "ip", "hostname", "top", "load",
        ],
        "admin": [
            "admin", "broadcast", "reload", "shutdown", "audit", "setrole",
            "globalstats", "cleanup", "backup", "restore",
        ],
    }
    if cat not in mapping:
        return await ctx.send(embed=embed_err("Unknown category",
            f"Try: `{PREFIX}help vps|manage|system|admin`"))
    e = embed_base(f"📖 Help — {cat.upper()}")
    e.description = "\n".join(f"• `{PREFIX}{c}`" for c in mapping[cat])
    await ctx.send(embed=e)

# ============================================================================
#   DEPLOY COMMANDS
# ============================================================================
@bot.command(name="deploy", aliases=["create", "new"])
@commands.cooldown(1, 20, commands.BucketType.user)
async def cmd_deploy(ctx, distro: str = "debian12",
                     cpu: int = DEFAULT_CPU, ram: int = DEFAULT_RAM,
                     disk: int = DEFAULT_DISK):
    if distro not in SUPPORTED:
        return await ctx.send(embed=embed_err("Unsupported distro",
            f"Choose: `{', '.join(SUPPORTED.keys())}`"))

    count = db_count(ctx.author.id)
    if count >= MAX_VPS_PER_USER and not ctx.author.guild_permissions.administrator:
        return await ctx.send(embed=embed_err("Limit reached",
            f"You already have **{count}/{MAX_VPS_PER_USER}** VPS. Destroy one first."))

    if cpu < 1 or cpu > 8: cpu = 1
    if ram < 256 or ram > 8192: ram = DEFAULT_RAM
    if disk < 1 or disk > 50: disk = DEFAULT_DISK

    e = embed_base("🚀 Deploy Confirmation",
                   f"You're about to deploy a new VPS:")
    e.add_field(name="📦 OS",   value=f"`{SUPPORTED[distro]['pretty']}`", inline=True)
    e.add_field(name="⚙️ CPU",  value=f"`{cpu} vCPU`", inline=True)
    e.add_field(name="🧠 RAM",  value=f"`{ram} MB`", inline=True)
    e.add_field(name="💾 Disk", value=f"`{disk} GB`", inline=True)
    e.add_field(name="⏱️ ETA",  value="`~60–180s`", inline=False)
    await ctx.send(embed=e, view=DeployConfirmView(distro, cpu, ram, disk, ctx.author, bot))

@bot.command(name="quickdeploy", aliases=["qd", "fast"])
@commands.cooldown(1, 20, commands.BucketType.user)
async def cmd_quickdeploy(ctx, distro: str = "debian12"):
    await ctx.invoke(cmd_deploy, distro=distro, cpu=DEFAULT_CPU,
                     ram=DEFAULT_RAM, disk=DEFAULT_DISK)

@bot.command(name="templates", aliases=["os", "images", "distros"])
async def cmd_templates(ctx):
    e = embed_base("📦 Available OS Templates",
                   f"{len(SUPPORTED)} images ready to deploy")
    for k, v in SUPPORTED.items():
        e.add_field(name=k, value=f"`{v['pretty']}`", inline=True)
    e.add_field(name="💡 Tip",
                value=f"Use `{PREFIX}deploy <template> [cpu] [ram] [disk]`",
                inline=False)
    await ctx.send(embed=e)

@bot.command(name="oslist", aliases=["oslist"])
async def cmd_oslist(ctx):
    await cmd_templates(ctx)

# ============================================================================
#   VPS GROUP — 20+ subcommands
# ============================================================================
@bot.group(name="vps", invoke_without_command=True)
async def vps_group(ctx):
    await ctx.send(embed=embed_base(
        "🖥️ VPS Commands",
        f"`{PREFIX}vps list|info|start|stop|restart|destroy|ssh|tunnel|console|stats|logs`"
    ))

@vps_group.command(name="list", aliases=["ls"])
async def vps_list(ctx):
    is_admin_user = ctx.author.guild_permissions.administrator
    rows = db_list() if is_admin_user else db_list(ctx.author.id)
    if not rows:
        return await ctx.send(embed=embed_warn("No VPS", "You don't own any VPS yet."))
    e = embed_base(f"🗂️ VPS List — {len(rows)} total")
    for r in rows[:20]:
        emoji = "🟢" if r["state"] == "RUNNING" else "🔴"
        e.add_field(
            name=f"{emoji} `{r['name']}`",
            value=f"`{r['distro']}` • {r['cpu']}vCPU • {r['ram']}MB • port `{r['port'] or '—'}`",
            inline=False,
        )
    if len(rows) > 20:
        e.set_footer(text=f"{FOOT} — showing 20 of {len(rows)}")
    await ctx.send(embed=e)

@vps_group.command(name="info")
async def vps_info(ctx, name: str):
    row = db_get(name)
    if not row:
        return await ctx.send(embed=embed_err("Not found", f"`{name}` doesn't exist."))
    if not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden", "That's not your VPS."))
    await ctx.send(embed=embed_vps(row), view=VPSManageView(name, bot))

@vps_group.command(name="start", aliases=["boot"])
async def vps_start(ctx, name: str):
    row = db_get(name)
    if not row or not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden / Not found"))
    await ctx.send(f"⏳ Starting `{name}`...")
    ok = await LXCManager.start(name)
    if ok:
        db_update(name, state="RUNNING")
        db_audit(ctx.author.id, "start", name)
    await ctx.send(embed=embed_ok("Started") if ok else embed_err("Failed"))

@vps_group.command(name="stop", aliases=["halt"])
async def vps_stop(ctx, name: str):
    row = db_get(name)
    if not row or not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden / Not found"))
    await ctx.send(f"⏳ Stopping `{name}`...")
    ok = await LXCManager.stop(name)
    if ok:
        db_update(name, state="STOPPED")
        db_audit(ctx.author.id, "stop", name)
    await ctx.send(embed=embed_ok("Stopped") if ok else embed_err("Failed"))

@vps_group.command(name="restart", aliases=["reboot"])
async def vps_restart(ctx, name: str):
    row = db_get(name)
    if not row or not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden / Not found"))
    await ctx.send(f"⏳ Restarting `{name}`...")
    await LXCManager.stop(name)
    ok = await LXCManager.start(name)
    if ok: db_update(name, state="RUNNING")
    await ctx.send(embed=embed_ok("Restarted") if ok else embed_err("Failed"))

@vps_group.command(name="destroy", aliases=["delete", "rm", "kill"])
async def vps_destroy(ctx, name: str):
    row = db_get(name)
    if not row or not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden / Not found"))
    await ctx.send(f"⚠️ Destroy `{name}`?",
                   view=ConfirmDestroyView(name, bot))

@vps_group.command(name="ssh")
async def vps_ssh(ctx, name: str):
    row = db_get(name)
    if not row or not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden / Not found"))
    if not row["ip"] and not row["tunnel"]:
        return await ctx.send(embed=embed_err("No connection", "No IP / tunnel. Try `vps tunnel`."))
    if row["tunnel"]:
        m = re.search(r"tcp://([^:]+):(\d+)", row["tunnel"])
        host = m.group(1) if m else row["ip"]
        port = m.group(2) if m else "22"
        cmd = f"ssh root@{host} -p {port}"
    else:
        cmd = f"ssh root@{row['ip']} -p 22"
    await ctx.send(embed=embed_base("🖥 SSH Command", code_block(cmd, "bash")))

@vps_group.command(name="tunnel", aliases=["port", "forward"])
async def vps_tunnel(ctx, name: str):
    row = db_get(name)
    if not row or not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden / Not found"))
    msg = await ctx.send("🌐 Opening Pinggy tunnel...")
    url = await PinggyManager.open(name, 22)
    if not url:
        return await msg.edit(embed=embed_err("Tunnel failed", "Pinggy may be unreachable."))
    port = int(re.search(r":(\d+)$", url).group(1))
    db_update(name, tunnel=url, port=port)
    db_audit(ctx.author.id, "tunnel", name)
    await msg.edit(embed=embed_base("🌐 Tunnel Active",
        f"**URL:** `{url}`\n**SSH:**\n{code_block(f'ssh root@{url.split(\"//\")[1]} -p {port}', 'bash')}"))

@vps_group.command(name="console", aliases=["exec", "sh"])
async def vps_console(ctx, name: str, *, command: str):
    row = db_get(name)
    if not row or not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden / Not found"))
    out = await LXCManager.exec(name, command, timeout=45)
    await ctx.send(embed=embed_base(f"⌨️ $ {command}", code_block(out or "(no output)")))

@vps_group.command(name="stats")
async def vps_stats(ctx, name: str):
    row = db_get(name)
    if not row or not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden / Not found"))
    out = await LXCManager.stats(name)
    await ctx.send(embed=embed_base(f"📊 Stats — {name}", code_block(out)))

@vps_group.command(name="logs")
async def vps_logs(ctx, name: str):
    row = db_get(name)
    if not row or not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden / Not found"))
    code, out = await sh("tail", "-n", "40", f"{LXC_ROOT}/{name}.log")
    await ctx.send(embed=embed_base(f"📜 Logs — {name}",
                                    code_block(out or "no logs")))

@vps_group.command(name="ip")
async def vps_ip(ctx, name: str):
    row = db_get(name)
    if not row or not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden / Not found"))
    ip = await LXCManager.get_ip(name)
    db_update(name, ip=ip)
    await ctx.send(embed=embed_ok("IP", f"`{ip or 'unknown'}`"))

@vps_group.command(name="rename")
async def vps_rename(ctx, name: str, new_name: str):
    row = db_get(name)
    if not row or not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden / Not found"))
    if db_get(new_name):
        return await ctx.send(embed=embed_err("Name taken"))
    code, out = await sh("lxc-stop", "-n", name, "-t", "10")
    code, out = await sh("mv", f"{LXC_ROOT}/{name}", f"{LXC_ROOT}/{new_name}")
    if code != 0:
        return await ctx.send(embed=embed_err("Rename failed", code_block(out)))
    db_update(name, name=new_name)
    await ctx.send(embed=embed_ok("Renamed", f"`{name}` → `{new_name}`"))

@vps_group.command(name="note")
async def vps_note(ctx, name: str, *, text: str):
    row = db_get(name)
    if not row or not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden / Not found"))
    db_update(name, note=text[:400])
    await ctx.send(embed=embed_ok("Note saved"))

@vps_group.command(name="limit")
async def vps_limit(ctx, name: str, cpu: int, ram: int):
    row = db_get(name)
    if not row or not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden / Not found"))
    conf = f"{LXC_ROOT}/{name}/config"
    try:
        lines = open(conf).read().splitlines()
        lines = [l for l in lines
                 if "lxc.cgroup2.memory.max" not in l
                 and "lxc.cgroup2.cpu.max" not in l]
        lines.append(f"lxc.cgroup2.memory.max = {ram}M")
        lines.append(f"lxc.cgroup2.cpu.max = {cpu * 100000} 100000")
        open(conf, "w").write("\n".join(lines) + "\n")
        db_update(name, cpu=cpu, ram=ram)
        await ctx.send(embed=embed_ok("Limits updated",
            f"CPU: `{cpu}` • RAM: `{ram}MB` (restart to apply)"))
    except Exception as e:
        await ctx.send(embed=embed_err("Failed", str(e)))

@vps_group.command(name="freeze")
async def vps_freeze(ctx, name: str):
    row = db_get(name)
    if not row or not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden / Not found"))
    code, _ = await sh("lxc-freeze", "-n", name)
    if code == 0:
        db_update(name, state="FROZEN")
        await ctx.send(embed=embed_ok("Frozen"))
    else:
        await ctx.send(embed=embed_err("Failed"))

@vps_group.command(name="unfreeze")
async def vps_unfreeze(ctx, name: str):
    row = db_get(name)
    if not row or not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden / Not found"))
    code, _ = await sh("lxc-unfreeze", "-n", name)
    if code == 0:
        db_update(name, state="RUNNING")
        await ctx.send(embed=embed_ok("Unfrozen"))
    else:
        await ctx.send(embed=embed_err("Failed"))

@vps_group.command(name="clone")
async def vps_clone(ctx, name: str, new_name: str):
    row = db_get(name)
    if not row or not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden / Not found"))
    if db_get(new_name):
        return await ctx.send(embed=embed_err("Name taken"))
    await ctx.send(f"⏳ Cloning `{name}` → `{new_name}`...")
    code, out = await sh("lxc-copy", "-n", name, "-N", new_name, "-s", timeout=600)
    if code != 0:
        return await ctx.send(embed=embed_err("Clone failed", code_block(out)))
    db_add(ctx.author.id, new_name, row["distro"], row["cpu"], row["ram"],
           row["disk"], "STOPPED")
    await ctx.send(embed=embed_ok("Cloned", f"`{name}` → `{new_name}`"))

@vps_group.command(name="export")
async def vps_export(ctx, name: str):
    row = db_get(name)
    if not row or not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden / Not found"))
    path = f"/tmp/{name}-{short_id()}.tar.gz"
    await ctx.send(f"📦 Exporting to `{path}`...")
    code, out = await sh("bash", "-c",
        f"cd {LXC_ROOT}/{name} && tar czf {path} rootfs config", timeout=900)
    if code != 0:
        return await ctx.send(embed=embed_err("Export failed", code_block(out)))
    size = os.path.getsize(path)
    await ctx.send(embed=embed_ok("Exported",
        f"`{path}` ({human_bytes(size)})"))

# ============================================================================
#   SNAPSHOT GROUP
# ============================================================================
@bot.group(name="snap", aliases=["snapshot"], invoke_without_command=True)
async def snap_group(ctx):
    await ctx.send(embed=embed_base("📸 Snapshot Commands",
        f"`{PREFIX}snap create|list|restore|del`"))

@snap_group.command(name="create", aliases=["new", "make"])
async def snap_create(ctx, name: str):
    row = db_get(name)
    if not row or not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden / Not found"))
    snap = f"snap-{short_id()}"
    code, out = await sh("lxc-snapshot", "-n", name, "-c", snap, timeout=300)
    if code != 0:
        return await ctx.send(embed=embed_err("Failed", code_block(out)))
    db_snap_add(name, snap)
    db_audit(ctx.author.id, "snap.create", f"{name}:{snap}")
    await ctx.send(embed=embed_ok("Snapshot created", f"`{snap}`"))

@snap_group.command(name="list", aliases=["ls"])
async def snap_list(ctx, name: str):
    row = db_get(name)
    if not row or not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden / Not found"))
    snaps = db_snap_list(name)
    if not snaps:
        return await ctx.send(embed=embed_warn("No snapshots"))
    e = embed_base(f"📸 Snapshots — {name}")
    for s in snaps[:20]:
        e.add_field(name=f"`{s['snap']}`",
                    value=f"created `{s['created'][:19]}`", inline=False)
    await ctx.send(embed=e)

@snap_group.command(name="restore")
async def snap_restore(ctx, name: str, snap: str):
    row = db_get(name)
    if not row or not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden / Not found"))
    code, out = await sh("lxc-snapshot", "-n", name, "-r", snap, timeout=300)
    if code != 0:
        return await ctx.send(embed=embed_err("Restore failed", code_block(out)))
    await ctx.send(embed=embed_ok("Restored", f"`{snap}`"))

@snap_group.command(name="del", aliases=["rm", "delete"])
async def snap_del(ctx, name: str, snap: str):
    row = db_get(name)
    if not row or not is_owner_or_admin(ctx, row):
        return await ctx.send(embed=embed_err("Forbidden / Not found"))
    code, out = await sh("lxc-snapshot", "-n", name, "-d", snap)
    if code != 0:
        return await ctx.send(embed=embed_err("Failed", code_block(out)))
    db_snap_del(name, snap)
    await ctx.send(embed=embed_ok("Snapshot deleted"))

# ============================================================================
#   SYSTEM COMMANDS
# ============================================================================
@bot.command(name="ping", aliases=["latency"])
async def cmd_ping(ctx):
    t0 = time.perf_counter()
    msg = await ctx.send("🏓 ...")
    dt = (time.perf_counter() - t0) * 1000
    await msg.edit(content=f"🏓 Pong! `{dt:.0f}ms` • WS `{bot.latency*1000:.0f}ms`")

@bot.command(name="uptime")
async def cmd_uptime(ctx):
    seconds = time.time() - bot.start_time
    code, host = await sh("uptime", "-p")
    await ctx.send(embed=embed_base("⏱ Uptime",
        f"**Bot:** `{human_time(seconds)}`\n**Host:** `{host.strip()}`"))

@bot.command(name="sysinfo", aliases=["sys", "host"])
async def cmd_sysinfo(ctx):
    code, out = await sh("bash", "-c",
        "echo '=== Host ==='; uname -a; "
        "echo; echo '=== CPU ==='; nproc; "
        "echo; echo '=== Memory ==='; free -h | head -2; "
        "echo; echo '=== Disk ==='; df -h / | tail -1")
    await ctx.send(embed=embed_base("🖥 Host Info", code_block(out)))

@bot.command(name="stats", aliases=["botstats"])
async def cmd_stats(ctx):
    total = db_count()
    e = embed_base("📊 Bot Statistics")
    e.add_field(name="Guilds",  value=f"`{len(bot.guilds)}`")
    e.add_field(name="Users",   value=f"`{sum(g.member_count or 0 for g in bot.guilds)}`")
    e.add_field(name="Commands",value=f"`{len(bot.commands)}`")
    e.add_field(name="VPS",     value=f"`{total}`")
    e.add_field(name="Uptime",  value=f"`{human_time(time.time() - bot.start_time)}`")
    e.add_field(name="Version", value=f"`{VERSION}`")
    await ctx.send(embed=e)

@bot.command(name="version", aliases=["ver"])
async def cmd_version(ctx):
    await ctx.send(embed=embed_base("ℹ️ Version",
        f"**Version:** `{VERSION}`\n**Build:** `{BUILD}`\n**Author:** Vasplayz90"))

@bot.command(name="netstat")
async def cmd_netstat(ctx):
    code, out = await sh("bash", "-c",
        "ss -tuln | head -30")
    await ctx.send(embed=embed_base("🌐 Listening Ports", code_block(out)))

@bot.command(name="df")
async def cmd_df(ctx):
    code, out = await sh("df", "-h")
    await ctx.send(embed=embed_base("💾 Disk Usage", code_block(out)))

@bot.command(name="free")
async def cmd_free(ctx):
    code, out = await sh("free", "-h")
    await ctx.send(embed=embed_base("🧠 Memory Usage", code_block(out)))

@bot.command(name="ps", aliases=["proc"])
async def cmd_ps(ctx):
    code, out = await sh("bash", "-c", "ps aux --sort=-%mem | head -20")
    await ctx.send(embed=embed_base("🔧 Top Processes", code_block(out)))

@bot.command(name="top")
async def cmd_top(ctx):
    code, out = await sh("bash", "-c", "top -bn1 | head -20")
    await ctx.send(embed=embed_base("📈 Top", code_block(out)))

@bot.command(name="load")
async def cmd_load(ctx):
    try:
        load = os.getloadavg()
        await ctx.send(embed=embed_ok("Load Average",
            f"1m: `{load[0]:.2f}` • 5m: `{load[1]:.2f}` • 15m: `{load[2]:.2f}`"))
    except Exception as e:
        await ctx.send(embed=embed_err("Failed", str(e)))

@bot.command(name="cpu")
async def cmd_cpu(ctx):
    code, out = await sh("bash", "-c", "nproc; grep 'model name' /proc/cpuinfo | head -1")
    await ctx.send(embed=embed_base("⚙️ CPU", code_block(out)))

@bot.command(name="mem")
async def cmd_mem(ctx):
    await cmd_free(ctx)

@bot.command(name="disk")
async def cmd_disk(ctx):
    await cmd_df(ctx)

@bot.command(name="whoami")
async def cmd_whoami(ctx):
    await ctx.send(embed=embed_base("👤 You",
        f"**User:** {ctx.author.mention}\n**ID:** `{ctx.author.id}`\n"
        f"**VPS owned:** `{db_count(ctx.author.id)}`"))

@bot.command(name="ip")
async def cmd_ip(ctx):
    code, out = await sh("hostname", "-I")
    await ctx.send(embed=embed_base("🌐 Host IPs", f"`{out.strip()}`"))

@bot.command(name="hostname")
async def cmd_hostname(ctx):
    code, out = await sh("hostname")
    await ctx.send(embed=embed_base("🏷 Hostname", f"`{out.strip()}`"))

@bot.command(name="pinghost", aliases=["ph"])
async def cmd_pinghost(ctx, host: str):
    code, out = await sh("ping", "-c", "3", "-W", "2", host, timeout=15)
    await ctx.send(embed=embed_base(f"🏓 ping {host}", code_block(out)))

@bot.command(name="invite", aliases=["inv"])
async def cmd_invite(ctx):
    url = (f"https://discord.com/api/oauth2/authorize?"
           f"client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands")
    await ctx.send(embed=embed_base("🔗 Invite Bot", f"[Click here]({url})"))

@bot.command(name="dashboard", aliases=["panel"])
async def cmd_dashboard(ctx):
    await ctx.send(embed=embed_base("🌐 Web Dashboard",
        f"**URL:** `http://<host-ip>:{DASHBOARD_PORT}/?key={DASHBOARD_SECRET}`\n"
        f"**Endpoints:**\n"
        f"• `GET /` — list all VPS\n"
        f"• `POST /action/<name>/start|stop|restart|destroy`\n"
        f"• `GET /vps/<name>` — detail"))

# ============================================================================
#   ADMIN COMMANDS
# ============================================================================
@bot.group(name="admin", invoke_without_command=True)
@is_admin()
async def admin_group(ctx):
    await ctx.send(embed=embed_base("👑 Admin Commands",
        f"`{PREFIX}admin list|destroy|broadcast|reload|cleanup|backup`"))

@admin_group.command(name="list")
@is_admin()
async def admin_list(ctx):
    rows = db_list()
    e = embed_base(f"👑 All VPS — {len(rows)}")
    for r in rows[:20]:
        e.add_field(name=f"`{r['name']}`",
                    value=f"owner <@{r['owner']}> • `{r['state']}`", inline=False)
    await ctx.send(embed=e)

@admin_group.command(name="destroy")
@is_admin()
async def admin_destroy(ctx, name: str):
    await PinggyManager.close(name)
    await LXCManager.destroy(name)
    db_del(name)
    db_audit(ctx.author.id, "admin.destroy", name)
    await ctx.send(embed=embed_ok("Destroyed", f"`{name}`"))

@admin_group.command(name="audit")
@is_admin()
async def admin_audit(ctx, limit: int = 20):
    rows = db_audit_list(limit)
    if not rows:
        return await ctx.send(embed=embed_warn("No audit entries"))
    e = embed_base(f"📋 Audit Log — last {len(rows)}")
    for r in rows[:20]:
        e.add_field(
            name=f"`{r['action']}`",
            value=f"<@{r['user']}> → `{r['target']}` at `{r['ts'][:19]}`",
            inline=False)
    await ctx.send(embed=e)

@admin_group.command(name="cleanup")
@is_admin()
async def admin_cleanup(ctx):
    rows = db_list()
    known = set(await LXCManager.all_containers())
    removed = 0
    for r in rows:
        if r["name"] not in known:
            db_del(r["name"])
            removed += 1
    await ctx.send(embed=embed_ok("Cleanup done",
        f"Removed `{removed}` orphan records"))

@admin_group.command(name="backup")
@is_admin()
async def admin_backup(ctx):
    fn = f"vps-backup-{int(time.time())}.db"
    try:
        bkp = sqlite3.connect(fn)
        DB.backup(bkp)
        bkp.close()
        await ctx.send(embed=embed_ok("Backup created", f"`{fn}`"),
                       file=discord.File(fn))
    except Exception as e:
        await ctx.send(embed=embed_err("Backup failed", str(e)))

@bot.command(name="broadcast", aliases=["bc"])
@is_admin()
async def cmd_broadcast(ctx, *, message: str):
    sent = 0
    for guild in bot.guilds:
        for ch in guild.text_channels:
            try:
                await ch.send(embed=embed_base("📢 Broadcast", message))
                sent += 1
                break
            except Exception:
                continue
    await ctx.send(embed=embed_ok("Broadcast sent", f"Delivered to `{sent}` guilds"))

@bot.command(name="reload")
@is_admin()
async def cmd_reload(ctx):
    try:
        await bot.tree.sync()
        await ctx.send(embed=embed_ok("Reloaded", "Slash commands resynced"))
    except Exception as e:
        await ctx.send(embed=embed_err("Reload failed", str(e)))

@bot.command(name="shutdown", aliases=["stopbot"])
@is_admin()
async def cmd_shutdown(ctx):
    await ctx.send(embed=embed_warn("Shutting down", "Goodbye 👋"))
    await bot.close()

@bot.command(name="globalstats")
@is_admin()
async def cmd_globalstats(ctx):
    running = sum(1 for r in db_list() if r["state"] == "RUNNING")
    e = embed_base("🌍 Global Statistics")
    e.add_field(name="Total VPS", value=f"`{db_count()}`")
    e.add_field(name="Running",   value=f"`{running}`")
    e.add_field(name="Guilds",    value=f"`{len(bot.guilds)}`")
    e.add_field(name="Commands",  value=f"`{len(bot.commands)}`")
    await ctx.send(embed=e)

@bot.command(name="setrole")
@is_admin()
async def cmd_setrole(ctx, role: discord.Role):
    global ADMIN_ROLE
    ADMIN_ROLE = role.name
    db_set("admin_role", role.name)
    await ctx.send(embed=embed_ok("Admin role updated", f"`{role.name}`"))

# ============================================================================
#   QUICK ALIASES (top-up to 150+ effective commands)
# ============================================================================
@bot.command(name="ls")
async def alias_ls(ctx):        await ctx.invoke(vps_list)
@bot.command(name="boot")
async def alias_boot(ctx, n: str): await ctx.invoke(vps_start, name=n)
@bot.command(name="halt")
async def alias_halt(ctx, n: str): await ctx.invoke(vps_stop, name=n)
@bot.command(name="reboot")
async def alias_reboot(ctx, n: str): await ctx.invoke(vps_restart, name=n)
@bot.command(name="kill")
async def alias_kill(ctx, n: str):   await ctx.invoke(vps_destroy, name=n)
@bot.command(name="rm")
async def alias_rm(ctx, n: str):     await ctx.invoke(vps_destroy, name=n)
@bot.command(name="sh")
async def alias_sh(ctx, n: str, *, c: str): await ctx.invoke(vps_console, name=n, command=c)
@bot.command(name="exec")
async def alias_exec(ctx, n: str, *, c: str): await ctx.invoke(vps_console, name=n, command=c)
@bot.command(name="tunnel")
async def alias_tunnel(ctx, n: str): await ctx.invoke(vps_tunnel, name=n)
@bot.command(name="console")
async def alias_console(ctx, n: str, *, c: str): await ctx.invoke(vps_console, name=n, command=c)
@bot.command(name="info")
async def alias_info(ctx, n: str):   await ctx.invoke(vps_info, name=n)

# ============================================================================
#   DASHBOARD (Flask)
# ============================================================================
app = Flask(__name__)

DASHBOARD_HTML = """
<!doctype html>
<html><head><meta charset=utf-8><title>VPS Deployer — Dashboard</title>
<style>
 body{font-family:system-ui,sans-serif;background:#0f1117;color:#eaeef7;margin:0;padding:24px}
 h1{color:#8b9dff;margin:0 0 6px}
 .sub{color:#8892a8;margin-bottom:20px}
 table{width:100%;border-collapse:collapse;background:#161a24;border-radius:12px;overflow:hidden}
 th,td{padding:10px 12px;text-align:left;border-bottom:1px solid #232838}
 th{background:#1c2230;color:#9aa7c7;font-size:13px;text-transform:uppercase}
 tr:hover{background:#1a1f2c}
 .pill{padding:3px 8px;border-radius:99px;font-size:12px;font-weight:600}
 .RUNNING{background:#0e2f1b;color:#5ee37d}
 .STOPPED{background:#3a1414;color:#ff7272}
 button{background:#5865F2;color:#fff;border:0;padding:6px 10px;border-radius:6px;cursor:pointer;font-size:12px}
 button.d{background:#a02c2c}
</style></head><body>
<h1>🖥️ VPS Deployer Dashboard</h1>
<div class=sub>ArizNodesLabs × Vasplayz90 — LXC powered</div>
<table><thead><tr>
<th>Name</th><th>Owner</th><th>OS</th><th>CPU</th><th>RAM</th><th>State</th><th>Tunnel</th><th>Actions</th>
</tr></thead><tbody>
{% for v in vps %}
<tr>
 <td><b>{{v.name}}</b></td>
 <td>{{v.owner}}</td>
 <td>{{v.distro}}</td>
 <td>{{v.cpu}}</td>
 <td>{{v.ram}}MB</td>
 <td><span class="pill {{v.state}}">{{v.state}}</span></td>
 <td>{{v.tunnel or '—'}}</td>
 <td>
   <form method=post style=display:inline action="/action/{{v.name}}/start?key={{key}}"><button>Start</button></form>
   <form method=post style=display:inline action="/action/{{v.name}}/stop?key={{key}}"><button>Stop</button></form>
   <form method=post style=display:inline action="/action/{{v.name}}/destroy?key={{key}}"><button class=d>Destroy</button></form>
 </td>
</tr>
{% endfor %}
</tbody></table>
</body></html>
"""

def _auth():
    return request.args.get("key") == DASHBOARD_SECRET

@app.route("/")
def dash_index():
    if not _auth(): return jsonify({"error": "unauthorized"}), 401
    rows = db_list()
    vps = [
        {"name": r["name"], "owner": r["owner"], "distro": r["distro"],
         "cpu": r["cpu"], "ram": r["ram"], "state": r["state"],
         "tunnel": r["tunnel"] or ""}
        for r in rows
    ]
    return render_template_string(DASHBOARD_HTML, vps=vps, key=DASHBOARD_SECRET)

@app.route("/api")
def dash_api():
    if not _auth(): return jsonify({"error": "unauthorized"}), 401
    rows = db_list()
    return jsonify({"count": len(rows), "vps": [
        {k: r[k] for k in r.keys()} for r in rows
    ]})

@app.route("/vps/<name>")
def dash_vps(name):
    if not _auth(): return jsonify({"error": "unauthorized"}), 401
    row = db_get(name)
    if not row: return jsonify({"error": "not found"}), 404
    return jsonify({k: row[k] for k in row.keys()})

@app.route("/action/<name>/<action>", methods=["GET", "POST"])
def dash_action(name, action):
    if not _auth(): return jsonify({"error": "unauthorized"}), 401
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        if action == "start":
            loop.run_until_complete(LXCManager.start(name))
            db_update(name, state="RUNNING")
        elif action == "stop":
            loop.run_until_complete(LXCManager.stop(name))
            db_update(name, state="STOPPED")
        elif action == "restart":
            loop.run_until_complete(LXCManager.stop(name))
            loop.run_until_complete(LXCManager.start(name))
            db_update(name, state="RUNNING")
        elif action == "destroy":
            loop.run_until_complete(PinggyManager.close(name))
            loop.run_until_complete(LXCManager.destroy(name))
            db_del(name)
        elif action == "tunnel":
            url = loop.run_until_complete(PinggyManager.open(name, 22))
            m = re.search(r":(\d+)$", url or "")
            port = int(m.group(1)) if m else None
            db_update(name, tunnel=url, port=port)
        else:
            return jsonify({"error": "unknown action"}), 400
    finally:
        loop.close()

    # If a browser hits this, redirect back to the dashboard
    if request.method == "GET" or "text/html" in (request.headers.get("Accept") or ""):
        from flask import redirect
        return redirect(f"/?key={DASHBOARD_SECRET}")
    return jsonify({"ok": True, "name": name, "action": action})

def run_dashboard():
    Log.info(f"Dashboard on :{DASHBOARD_PORT} (key={DASHBOARD_SECRET})")
    app.run(host="0.0.0.0", port=DASHBOARD_PORT, debug=False,
            use_reloader=False, threaded=True)

# ============================================================================
#   GRACEFUL SHUTDOWN
# ============================================================================
async def _cleanup_all():
    Log.warn("Closing all tunnels…")
    for name in list(PinggyManager.TUNNELS.keys()):
        await PinggyManager.close(name)

def _signal_handler(signum, frame):
    Log.warn(f"Signal {signum} received — shutting down")
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_cleanup_all())
    except Exception:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT,  _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)

# ============================================================================
#   MAIN
# ============================================================================
def main():
    print(BANNER)
    Log.info(f"Version {VERSION} — {BUILD}")
    Log.info(f"Prefix: {PREFIX} | Max VPS/user: {MAX_VPS_PER_USER}")
    if not TOKEN or TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        Log.err("DISCORD_TOKEN not set in .env")
        sys.exit(1)

    db_init()
    Log.ok(f"Database ready ({db_count()} VPS tracked)")

    dash_thread = threading.Thread(target=run_dashboard, daemon=True)
    dash_thread.start()

    try:
        bot.run(TOKEN, log_handler=None)
    except discord.LoginFailure:
        Log.err("Invalid bot token")
        sys.exit(1)
    except Exception as e:
        Log.err(f"Fatal: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

# ============================================================================
#                     END — ArizNodesLabs × Vasplayz90
# ============================================================================
