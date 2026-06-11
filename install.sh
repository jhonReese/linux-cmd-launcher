#!/usr/bin/env bash
# ============================================================
# CMD Launcher — 一鍵安裝腳本 v1.0.0
# 支援：Ubuntu 20.04+ / Debian 11+ / Arch / Fedora 36+
# [[3]](#__3) (DigitalOcean best practices)
# ============================================================
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="cmd-launcher"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
BIN_PATH="$HOME/.local/bin/$APP_NAME"
CFG_DIR="$HOME/.config/$APP_NAME"
AUTOSTART="$HOME/.config/autostart/$APP_NAME.desktop"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo -e "${GREEN}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ⌨  CMD Launcher — Installer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${NC}"

# ── 1. 系統依賴 ──────────────────────────────────────────
echo "📦 Installing system dependencies..."
if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y \
        python3 python3-pip python3-venv \
        python3-gi python3-gi-cairo \
        gir1.2-gtk-3.0 \
        gir1.2-appindicator3-0.1 \
        xdotool xclip wl-clipboard \
        libgtk-3-dev 2>/dev/null || true
elif command -v pacman &>/dev/null; then
    sudo pacman -Sy --noconfirm \
        python python-pip python-gobject \
        gtk3 libappindicator-gtk3 xdotool xclip
elif command -v dnf &>/dev/null; then
    sudo dnf install -y \
        python3 python3-pip python3-gobject \
        gtk3 libappindicator-gtk3 xdotool xclip
else
    echo -e "${YELLOW}⚠ Unknown package manager. Install manually:${NC}"
    echo "  python3, python3-gi, gtk3, xclip, xdotool"
fi

# Verify important tools are available (best-effort)
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠ python3 not found in PATH. Please install Python 3 before proceeding.${NC}" >&2
    exit 1
fi

# Check xdotool availability and warn if missing (WSLg users will want this)
if ! command -v xdotool >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠ xdotool not found. It is recommended for WSLg visibility fixes.${NC}\n  Try: sudo apt install xdotool" >&2 || true
fi

# ── 2. 安裝程式 ──────────────────────────────────────────
echo ""
echo "📁 Copying files to $INSTALL_DIR..."
rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cp -r "$REPO_DIR/src"    "$INSTALL_DIR/"
cp -r "$REPO_DIR/config" "$INSTALL_DIR/"
cp -r "$REPO_DIR/assets" "$INSTALL_DIR/"
cp    "$REPO_DIR/requirements.txt" "$INSTALL_DIR/"

# ── 3. 確保 __init__.py 存在（修正 import 問題）──────────
touch "$INSTALL_DIR/src/__init__.py"
touch "$INSTALL_DIR/src/ui/__init__.py"
touch "$INSTALL_DIR/src/core/__init__.py"

# ── 4. 產生圖示 ──────────────────────────────────────────
echo "🎨 Generating icon..."
python3 "$INSTALL_DIR/assets/generate_icon.py" 2>/dev/null || true

# ── 5. 虛擬環境 ──────────────────────────────────────────
echo ""
echo "🐍 Setting up Python virtual environment..."
PYTHON3_BIN=$(command -v python3.12 2>/dev/null \
    || command -v python3.11 2>/dev/null \
    || command -v python3.10 2>/dev/null \
    || command -v python3.9  2>/dev/null \
    || command -v python3    2>/dev/null || true)
if [ -z "$PYTHON3_BIN" ]; then
    echo -e "${YELLOW}✗ Cannot find python3. Please install Python 3 before proceeding.${NC}" >&2
    exit 1
fi
echo "   Using: $PYTHON3_BIN ($("$PYTHON3_BIN" --version))"
"$PYTHON3_BIN" -m venv --system-site-packages "$INSTALL_DIR/.venv"
"$INSTALL_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$INSTALL_DIR/.venv/bin/pip" install --quiet \
    pynput \
    PyGObject \
    Pillow

# ── 6. 建立啟動腳本 ──────────────────────────────────────
mkdir -p "$HOME/.local/bin"
cat > "$BIN_PATH" << SCRIPT
#!/usr/bin/env bash
cd "$INSTALL_DIR"
exec "$INSTALL_DIR/.venv/bin/python3" "$INSTALL_DIR/src/launcher.py" "\$@"
SCRIPT
chmod +x "$BIN_PATH"

# ── 7. PATH 設定 ─────────────────────────────────────────
for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [[ -f "$rc" ]] && ! grep -q 'local/bin' "$rc"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$rc"
    fi
done

# ── 8. 使用者設定目錄（首次安裝複製預設設定）────────────
mkdir -p "$CFG_DIR"
if [[ ! -f "$CFG_DIR/commands.json" ]]; then
    cp "$REPO_DIR/config/commands.json" "$CFG_DIR/commands.json"
    echo "📝 Default config copied to $CFG_DIR/commands.json"
fi

# ── 9. XDG Autostart ─────────────────────────────────────
mkdir -p "$HOME/.config/autostart"
cat > "$AUTOSTART" << DESKTOP
[Desktop Entry]
Type=Application
Name=CMD Launcher
Comment=Linux Command Cheatsheet (Ctrl+Alt+O)
Exec=$BIN_PATH
Icon=$INSTALL_DIR/assets/icon.png
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
DESKTOP

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Installation complete!"
echo ""
echo "  ▶  Run now  :  $APP_NAME"
echo "  ⌨  Shortcut :  Ctrl+Alt+O  (WSL) / Super+O  (native Linux)"
echo "  📝 Config   :  $CFG_DIR/commands.json"
echo "  🗑  Uninstall:  ./uninstall.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${NC}"
