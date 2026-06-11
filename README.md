# CMD Launcher

> **One-key command cheatsheet for Linux & WSLg.**
> Press `Ctrl+Alt+O` (WSL/WSLg) or `Super+O` (native Linux) to pop up
> a fuzzy-searchable, keyboard-navigable command palette — no mouse required.

![demo1](assets/demo1.gif)
![demo2](assets/demo2.gif)
![demo3](assets/demo3.gif)


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

---

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `Ctrl+Alt+O` | Toggle window (WSL / WSLg) |
| `Super+O` | Toggle window (native Linux X11) |
| `↓` / `↑` | Navigate list |
| `Enter` | Copy highlighted command |
| `Shift+Enter` | Run in terminal |
| `Esc` | Close |

---

## Installation

```bash
git clone https://github.com/jhonReese/linux-cmd-launcher.git
cd linux-cmd-launcher
chmod +x install.sh && ./install.sh
```

```bash
cmd-launcher
```

---

## Windows (WSLg) Setup

CMD Launcher runs inside WSL and surfaces a GTK window via WSLg.

### Recommended: AutoHotkey v2

1. Install [AutoHotkey v2](https://www.autohotkey.com/)
1. Create a `.ahk` file:

```ahk
^!o::
    RunWait("wsl.exe bash -c `"kill -SIGUSR1 $(cat /tmp/cmd-launcher.pid)`"", "", "Hide")
    Return
```

1. Run on Windows startup. Start `cmd-launcher` in WSL — AHK toggles it via SIGUSR1.

If the window doesn't appear: `sudo apt install xdotool`

---

## Add Your Own Commands

Edit `~/.config/cmd-launcher/commands.json`:

```json
{
  "name": "My Shortcuts",
  "color": "#E86A58",
  "commands": [
    { "cmd": "kubectl get pods -A", "desc": "List all pods" },
    { "cmd": "terraform plan",      "desc": "Preview infra changes" }
  ]
}
```

---

## Requirements

- Linux, WSL2 + WSLg, or X11
- Python 3.9+
- GTK 3

---

## Uninstall

```bash
./uninstall.sh
```
