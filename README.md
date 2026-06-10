# ⌨️ CMD Launcher

> Press **`Super + O`** anywhere on your Linux desktop to instantly
> pop up your personal command cheatsheet.

![demo](assets/demo.gif)

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

## 🛠 Add Your Own Commands

Edit `~/.local/share/cmd-launcher/config/commands.json`:

```json
{
  "name": "🔥 My Custom",
  "color": "#E86A58",
  "commands": [
    { "cmd": "your-command", "desc": "What it does" }
  ]
}
```

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
