# cmd-launcher
![demo1](assets/demo1.gif)

> **One-key command cheatsheet for Linux & WSLg.**
> Press `Ctrl+Alt+O` (WSL/WSLg) or `Super+O` (native Linux) to instantly pop up
> a fuzzy-searchable, keyboard-navigable command palette — no mouse required.

---

**## Why CMD Launcher?**

**Most launchers are _app launchers_ — they find and open programs.
CMD Launcher solves a different problem: **you know a command exists, but can't remember the exact syntax.**
It's a personal, always-available cheat sheet with zero-friction copy-and-run.**
- 你知道某個指令，但卻記不住確切的語法。這就是CMD Launcher 解決的問題
就像一份隨時可用的私人速查表，讓你輕鬆複製貼上。


**Issues related to window focus and hotkey conflicts in the Windows WSLg (Windows Subsystem for Linux GUI) environment.**
- 解決 Windows WSLg（Windows Subsystem for Linux GUI）的視窗與熱鍵衝突。
- Linux internal hotkey listening (such as pynput) often fails when crossing operating systems.
--- Linux 內部的熱鍵監聽（如 pynput）在跨 OS 時經常失效
- GTK 3's native window.present() often fails to force the window to the foreground due to permission restrictions of Microsoft Wayland Compositor (Focus Stealing Prevention).
--- GTK 3 原生的 window.present() 常常因為微軟 Wayland 合成器（Compositor）的權限限制，無法成功將視窗強行推至最前端（Focus Stealing Prevention）。


| What makes it different | Detail |
|---|---|
| **WSLg first-class** | Only launcher with SIGUSR1 toggle + `xdotool` fallback for Windows+WSLg users |
| **Zero network** | No telemetry, no API calls, no update checks — ever |
| **JSON config** | Add your own commands in 30 seconds, no scripting required |
| **Keyboard-first** | Arrow keys navigate, Enter copies, Shift+Enter runs — never touch the mouse |
| **Fuzzy + multi-word** | `"htpo"` finds `htop`; `"git log"` matches `git log --oneline` |
| **Tiny footprint** | ~1 MB installed, one Python process, no background daemons |
| **Readable codebase** | ~600 lines of Python — fork and customize in an afternoon |

---

- 🚀 **One-key toggle** — `Ctrl+Alt+O` (WSL) / `Super+O` (native Linux)
- ⌨️ **Full keyboard navigation** — `↑↓` move through results; never leave the keyboard
  
- 🔍 **Fuzzy + multi-word search** — typos and partial queries both work
![demo3](assets/demo3.gif)
- 📋 **Enter to copy** — copies highlighted command to clipboard instantly
- ▶️ **Shift+Enter to run** — opens command directly in your terminal

- 🕐 **Recent tab** — tracks your last 8 used commands
![demo2](assets/demo2.gif)
- 🎨 **Apple × DeepMind aesthetic** — dark glass UI, high-contrast text, color-coded categories
- 📝 **Fully customizable** — edit `~/.config/cmd-launcher/commands.json`
- 🔒 **Privacy-first** — no keylogging beyond `Ctrl+Alt+O`, no network, no data collection
- 📦 **70+ built-in commands** — covering files, git, docker, network, python, permissions

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|---|---|
| `Ctrl+Alt+O` | Toggle window (WSL / WSLg) |
| `Super+O` | Toggle window (native Linux X11) |
| `↓` / `↑` | Navigate command list |
| `Enter` | Copy highlighted command to clipboard |
| `Shift+Enter` | Run highlighted command in terminal |
| `Esc` | Close window |
| Click row | Copy command to clipboard |
| Click **Run ▶** | Run command in terminal |

---

## Why

Terminal muscle memory has limits. I kept a text file of commands I use across ML experiments, git workflows, and system maintenance — and I kept forgetting where it was. This is the structured version of that file, with a global hotkey and fuzzy search.

---

## Features

- **Global toggle** — `Super + O` shows and hides the panel from any context
- **Fuzzy search** — filters commands in real-time as you type
- **One-click copy** — click any row to copy the command to clipboard
- **Fully local** — no network requests, no keylogging beyond the registered hotkey combo
- **JSON-driven config** — add, remove, or reorganize commands without touching the code

---

## Requirements

- Linux (X11 or Wayland via XWayland)
- Python 3.8+
- GTK 3

---

## Installation

```bash
git clone https://github.com/jhonReese/linux-cmd-launcher.git
cd linux-cmd-launcher
chmod +x install.sh
./install.sh
```

Then launch:
```bash
cmd-launcher
```

Check version:
```bash
cmd-launcher --version
```

---

## 🪟 Windows (WSLg) Setup

CMD Launcher runs inside WSL and surfaces a GTK window via WSLg.
The `Ctrl+Alt+O` hotkey is handled natively inside WSL (Windows intercepts `Super`).

### Option A — AutoHotkey v2 (recommended for hotkey from Windows desktop)

1. Install [AutoHotkey v2](https://www.autohotkey.com/) on Windows.
2. Create a `.ahk` file with:

```ahk
^!o::
    RunWait("wsl.exe bash -c `"kill -SIGUSR1 $(cat /tmp/cmd-launcher.pid)`"", "", "Hide")
    Return
```

3. Run the `.ahk` file on Windows startup.
4. Start `cmd-launcher` inside WSL — the AHK script toggles it via `SIGUSR1`.

### Option B — toggle.sh directly

```bash
# From anywhere in WSL:
bash /path/to/linux-cmd-launcher/toggle.sh
```

`toggle.sh` auto-starts the app if not running, or toggles it if already active.

### WSLg tip

If the window doesn't appear, install `xdotool`:
```bash
sudo apt install xdotool
```
CMD Launcher uses `xdotool windowactivate` as a fallback when GTK's `present()` is unreliable under WSLg compositing.

---

## 🛠 Add Your Own Commands

Edit `~/.config/cmd-launcher/commands.json` (created on first install):

```json
{
  "name": "🔥 My Shortcuts",
  "color": "#E86A58",
  "commands": [
    { "cmd": "kubectl get pods -A",   "desc": "List all Kubernetes pods" },
    { "cmd": "terraform plan",        "desc": "Preview infra changes" },
    { "cmd": "make build",            "desc": "Build the project" }
  ]
}
```

Add the new category object to the `"categories"` array. Changes take effect next time the window opens.

---

## 🧪 Local WSL Testing

### Prerequisites

```bash
sudo apt-get install -y \
  python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
  xclip xdotool python3-pip
pip3 install pynput pytest
```

### Run unit tests (no display needed)

```bash
cd /mnt/c/Users/user/linux-cmd-launcher
python3 -m pytest tests/ -v
```

### Run the full UI

```bash
cd /mnt/c/Users/user/linux-cmd-launcher
python3 src/launcher.py
```

---

## 🗑 Uninstall

```bash
./uninstall.sh
```

---

## 🔒 Security Notes

- Only `Ctrl+Alt+O` is monitored; no other keystrokes are logged
- All data is local — zero network requests
- Config files contain no sensitive information
- History stored in `~/.config/cmd-launcher/history.json` (plain JSON, yours to delete)

---

## Competitor Comparison

| Feature | **CMD Launcher** | rofi | Ulauncher | Albert | Cerebro |
|---|:---:|:---:|:---:|:---:|:---:|
| Command palette / cheatsheet | ✅ | Scripted | Extension | Extension | Extension |
| Fuzzy + multi-word search | ✅ | ✅ | ✅ | ✅ | ✅ |
| Arrow-key navigation | ✅ | ✅ | ✅ | ✅ | ✅ |
| Enter copy / Shift+Enter run | ✅ | Via script | Extension | Extension | Extension |
| **WSLg out-of-the-box** | ✅ | ❌ | ❌ | ❌ | ❌ |
| Zero network / privacy-first | ✅ | ✅ | ❌ | ❌ | ❌ |
| JSON config (no scripting) | ✅ | Partial | ❌ | ❌ | ❌ |
| One-line install | ✅ | ❌ | ✅ | Partial | ✅ |
| Language | Python/GTK3 | C | Python/GTK | C++/Qt | Electron |
| Binary size | ~1 MB | ~2 MB | ~50 MB | ~30 MB | ~200 MB |

### When to pick something else

| If you need… | Use instead |
|---|---|
| App launcher + plugin ecosystem | Ulauncher or Albert |
| Ultra-low latency, power scripting | rofi |
| Cross-platform (macOS/Windows native) | Cerebro |
| Shell completion integration | fzf + shell aliases |

CMD Launcher is intentionally minimal. It does one thing well: **instant access to your personal command library**.
