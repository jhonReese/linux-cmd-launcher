# cmd-launcher

A keyboard-driven command cheatsheet panel for Linux desktops.  
Press `Super + O` anywhere to bring up a searchable, dark-themed overlay of your personal command library — then dismiss it just as fast.

Built for the kind of workflow where reaching for the mouse is already too slow.

<img src="assets/image.png" width="720" alt="cmd-launcher panel" />

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

Then launch with:

```bash
cmd-launcher
```

The process runs in the background and listens for `Super + O`.

---

## Configuration

Edit `~/.local/share/cmd-launcher/config/commands.json` to define your command groups:

```json
{
  "name": "Git",
  "color": "#4A90E2",
  "commands": [
    { "cmd": "git log --oneline -10", "desc": "Recent commits" },
    { "cmd": "git stash pop",         "desc": "Restore stash" }
  ]
}
```

Each group takes a `name`, a `color` (used as the category accent), and a list of `{ cmd, desc }` entries.

---

## Uninstall

```bash
./uninstall.sh
```

---

## Privacy

- No API keys or credentials are stored anywhere
- Only the `Super + O` key combination is intercepted — no other keystrokes are logged or transmitted
- All data remains local

- Linux (X11 or Wayland)
- Python 3.8+
- GTK 3


---

## WSL2 / WSLg Setup

Since `pynput` cannot listen globally in WSLg, the hotkey is triggered from Windows via AutoHotkey.

### Requirements
- [AutoHotkey v2](https://www.autohotkey.com/)
- WSL2 with WSLg enabled

### AutoHotkey Script
Create a file `cmd-launcher.ahk` on Windows:

```ahk
#Requires AutoHotkey v2.0
^!o:: {
    RunWait("wsl.exe bash -c `"kill -SIGUSR1 $(cat /tmp/cmd-launcher.pid)`"",,  "Hide")
}
```

Run this script at Windows startup via Task Scheduler or Startup folder.

### Known Limitation
On WSLg (Wayland), the window appears in the taskbar when toggled but may not automatically raise to foreground. This is a compositor-level restriction — clicking the taskbar icon will bring it up.
