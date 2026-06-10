#!/usr/bin/env bash
set -euo pipefail

APP_NAME="cmd-launcher"
echo "🗑  Uninstalling $APP_NAME..."

rm -rf "$HOME/.local/share/$APP_NAME"
rm -f  "$HOME/.local/bin/$APP_NAME"
rm -f  "$HOME/.config/autostart/$APP_NAME.desktop"

echo "✅ Uninstalled successfully."
