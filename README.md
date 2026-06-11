# ⌨️ CMD Launcher

> Press **`Super + O`** anywhere on your Linux desktop to instantly
> pop up your personal command cheatsheet.

> Demo animation is referenced in the UI but not included in this repository.
>
> If you want to add one, place `assets/demo.gif` in the repo.
>
## ✨ Features

- 🚀 **One-key toggle** — `Super + O` shows/hides the panel
- 🔍 **Fuzzy search** — filter commands in real-time
- 📋 **One-click copy** — click any row to copy to clipboard
- 🎨 **Apple × DeepMind aesthetic** — dark glass UI
- 📝 **Fully customizable** — edit `config/commands.json`
- 🔒 **Privacy-first** — no keylogging, no network calls

## 📦 Quick Install

```bash
git clone https://github.com/YOUR_USERNAME/cmd-launcher.git
cd cmd-launcher
chmod +x install.sh
./install.sh
```

Then run:
```bash
cmd-launcher
```

Check the app version with:
```bash
cmd-launcher --version
```

## 🪟 Windows (WSLg) Setup

1. Install AutoHotkey v2 on Windows.
2. Add this script to a `.ahk` file and run it on startup:

```ahk
autoTrim := true
^!o::
    RunWait("wsl.exe bash -c `"kill -SIGUSR1 $(cat /tmp/cmd-launcher.pid)`"", "", "Hide")
    Return
```

3. Make sure WSLg is running and `cmd-launcher` is started inside WSL.
4. If the panel does not appear, install `xdotool` in WSL and restart the app.

## 🛠 Add Your Own Commands

Edit `~/.local/share/cmd-launcher/config/commands.json`:

```json
{
  "name": "🔥 My Custom",
  "color": "#E86A58",
  "commands": [
    { "cmd": "your-command", "desc": "What it does" },
    { "cmd": "docker ps -a", "desc": "List all Docker containers" },
    { "cmd": "grep -rn 'pattern' .", "desc": "Search text recursively" },
    { "cmd": "python3 -m venv .venv", "desc": "Create a Python virtualenv" }
  ]
}
```

The shipped sample config already includes categories for system, Docker, Git, Python, and more.

## 🗑 Uninstall

```bash
./uninstall.sh
```

## 🔒 Security Notes

- No API keys or passwords are stored anywhere
- All data is local — no network requests
- Only `Super+O` combo is detected; no other keystrokes are logged
- Config files contain no sensitive information

## 📋 Requirements

- Linux (X11 or Wayland)
- Python 3.8+
- GTK 3

**Competitors**

- **rofi** — A mature, C-based launcher focused on speed, scripting and many "modes" (run, window, ssh, script). Rofi is highly optimised, themes-capable, and now has Wayland support; it's a powerful drop-in replacement for dmenu but is a lower-level tool compared to `cmd-launcher`.
- **Ulauncher** — A Python/GTK application launcher with a rich extensions ecosystem (plugins, themes, calculator, file mode). Ulauncher is feature-rich and production-ready for desktop use; it supports extension APIs and a larger user base.
- **Albert** — A Qt/C++ keyboard launcher with a plugin system and tight performance. Albert is more full-featured with cross-desktop integration and many community plugins.
- **Cerebro** — An Electron-based cross-platform launcher that supports plugins and integrations; heavier but cross-platform.

How `cmd-launcher` compares:

- **Purpose**: `cmd-launcher` is a lightweight, privacy-first command cheatsheet and quick-run helper (JSON-configured commands), not a full extension/plugin platform.
- **Implementation**: small Python + GTK3 app — easy to read and extend for Python developers.
- **WSLg**: includes pragmatic WSLg-specific behavior (SIGUSR1 toggle + optional `xdotool` fallback) to improve Windows+WSLg workflows.
- **Scope**: intentionally minimal — focuses on discoverable commands, fuzzy search, copy-to-clipboard, and tight privacy guarantees.
- **When to pick other projects**: choose `rofi`/`albert`/`ulauncher` if you need a mature ecosystem, plugins, shell integration, or extremely high performance.

If you'd like, I can add a short link list with comparisons to specific features (extensions, theming, Wayland support) for each project.

## 競品功能比較

| Project | Language | Plugins / Extensions | Wayland support | Theming | Focus |
|---|---:|:---:|:---:|:---:|---|
| rofi | C | scripts/plugins via script mode | Yes (native Wayland backend available) | Advanced (rasi themes) | Fast, scriptable launcher & dmenu replacement |
| Ulauncher | Python/GTK | Yes (extensions ecosystem) | Partial (X11 primary; Wayland via XWayland) | Themes supported | App launcher with extensions (GUI-heavy) |
| Albert | C++/Qt | Yes (plugins) | X11 primary (Wayland support varies) | Themes | High-performance, plugin-driven launcher |
| Cerebro | Electron | Yes (plugins) | Cross-platform (Wayland depends on platform) | Theming via web UI | Cross-platform, plugin-centric launcher |
| cmd-launcher (this project) | Python/GTK3 | Minimal (JSON-config) | Works on X11/WSLg; includes xdotool fallback | Lightweight CSS-like GTK styling | Simple commands cheatsheet, fuzzy search, privacy-first |

Notes:
- `rofi` offers the most flexibility for power users and scripts and is the best choice when low-level control, performance, and deep Wayland/XCB handling are required.
- `Ulauncher` and `Albert` provide richer extension ecosystems; choose them if you need plugins (file search, clipboard history, web lookups).
- `cmd-launcher` is intentionally minimal and easy to customize via `config/commands.json` — best when you want a privacy-focused, lightweight command palette rather than a full app-store of extensions.

## 安裝難易度與支援細節

| Project | Install Complexity | Wayland / X11 Notes | Source |
|---|---:|---:|---|
| rofi | Moderate — build from source for latest Wayland features; packages available in distros | Native Wayland backend (since 2025); may require meson build options | https://github.com/davatorium/rofi |
| Ulauncher | Easy — Python package / distro packages available | Primarily X11; Wayland support via XWayland; ongoing v6 rewrite | https://github.com/Ulauncher/Ulauncher |
| Albert | Moderate — C++/Qt build or distro packages | X11-first; Wayland integration varies by platform | https://github.com/albertlauncher/albert |
| Cerebro | Easy — Electron app, cross-platform installers | Cross-platform; Wayland behavior depends on Electron/host | https://github.com/cerebro-app/cerebro |
| cmd-launcher | Easy — Bash installer copies files and prepares venv; WSLg users should install `xdotool` for best behavior | Works on X11 and WSLg; includes a pragmatic `xdotool` fallback for WSLg when `present()` is unreliable | This repo |

If you want, I can add direct install commands and distro-specific notes for each competitor.
