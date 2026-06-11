![demo 1](<assets/錄製內容 2026-06-11 221634_1.gif>)
# cmd-launcher

**You know the command exists. You just can't remember the exact flags.
Ctrl+Alt+O — panel opens. Type. Copy. Done.**


> **One-key command cheatsheet for Linux & WSLg.**
> Press `Ctrl+Alt+O` (WSL/WSLg) or `Super+O` (native Linux) to instantly pop up
> a fuzzy-searchable, keyboard-navigable command palette — no mouse required.

---

## Why CMD Launcher?

Most launchers are _app launchers_ — they find and open programs.
CMD Launcher solves a different problem: **you know a command exists, but can't remember the exact syntax.**
It's a personal, always-available cheat sheet with zero-friction copy-and-run.

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
![demo 3](<assets/錄製內容 2026-06-11 222002_3.gif>)


- 📋 **Enter to copy** — copies highlighted command to clipboard instantly
- ▶️ **Shift+Enter to run** — opens command directly in your terminal

- 🕐 **Recent tab** — tracks your last 8 used commands
![demo 2](<assets/錄製內容 2026-06-11 221833_2.gif>)


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

Expected output — all 16 tests pass:

```
tests/test_commands.py::TestLoad::test_categories_loaded         PASSED
tests/test_commands.py::TestLoad::test_command_count             PASSED
tests/test_commands.py::TestLoad::test_malformed_json_returns_empty PASSED
tests/test_commands.py::TestSearch::test_exact_cmd_match         PASSED
tests/test_commands.py::TestSearch::test_fuzzy_typo_match        PASSED
... (16 total)
```

### Run the full UI

```bash
cd /mnt/c/Users/user/linux-cmd-launcher
export DISPLAY=:0   # WSLg sets this automatically; only needed if unset
python3 src/launcher.py
```

The terminal prints:
```
✅ CMD Launcher v1.0.0 is running.
   Shortcut : Ctrl + Alt + O
```

Press `Ctrl+Alt+O` to toggle. Test:
- Arrow keys navigate the list
- `Enter` copies the highlighted command
- `Shift+Enter` opens the command in a terminal
- Type `"htpo"` to verify fuzzy search catches typos
- Type `"git log"` to verify multi-word search

### Full install test

```bash
chmod +x install.sh && ./install.sh
cmd-launcher
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

- No API keys or credentials are stored anywhere
- Only the `Super + O` key combination is intercepted — no other keystrokes are logged or transmitted
- All data remains local

- Linux (X11 or Wayland/WSLg)
- Python 3.9+
- GTK 3

---

## 競品功能比較 (Competitor Comparison)

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

---

## 安裝難易度與支援細節

| Project | Install | Wayland / X11 | Source |
|---|---|---|---|
| **cmd-launcher** | `./install.sh` (one script) | X11 + WSLg (xdotool fallback) | https://github.com/jhonReese/linux-cmd-launcher |
| rofi | distro pkg or build | Native Wayland backend (2025+) | https://github.com/davatorium/rofi |
| Ulauncher | distro pkg / pip | X11-first; Wayland via XWayland | https://github.com/Ulauncher/Ulauncher |
| Albert | distro pkg or build | X11-first; varies | https://github.com/albertlauncher/albert |
| Cerebro | Electron installer | Cross-platform | https://github.com/cerebroapp/cerebro |
