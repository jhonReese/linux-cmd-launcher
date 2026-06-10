"""
主程式入口
- Super+O 全域快捷鍵
- 系統托盤圖示（AppIndicator / StatusIcon fallback）
- --version / --help CLI flags
"""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

import signal
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.hotkey   import HotkeyListener
from src.core.commands import CommandLibrary
from src.ui.window     import LauncherWindow

__version__ = "1.0.0"


def _try_appindicator(window: LauncherWindow):
    """嘗試建立 AppIndicator3 托盤圖示（Ubuntu/GNOME）"""
    try:
        gi.require_version("AppIndicator3", "0.1")
        from gi.repository import AppIndicator3

        icon_path = str(
            Path(__file__).parent.parent / "assets" / "icon.png"
        )
        ind = AppIndicator3.Indicator.new(
            "cmd-launcher", icon_path,
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        ind.set_title("CMD Launcher")

        menu = Gtk.Menu()
        item_show  = Gtk.MenuItem(label="Show  (Super+O)")
        item_quit  = Gtk.MenuItem(label="Quit")
        item_show.connect("activate", lambda *_: GLib.idle_add(window.toggle))
        item_quit.connect("activate", lambda *_: Gtk.main_quit())
        menu.append(item_show)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(item_quit)
        menu.show_all()
        ind.set_menu(menu)
        return ind
    except Exception:
        # Fallback：StatusIcon（舊版 GNOME / XFCE）
        try:
            icon_path = str(
                Path(__file__).parent.parent / "assets" / "icon.png"
            )
            si = Gtk.StatusIcon.new_from_file(icon_path)
            si.set_tooltip_text("CMD Launcher  (Super+O)")
            si.connect("activate",    lambda *_: GLib.idle_add(window.toggle))
            si.connect("popup-menu",  lambda icon, btn, t: _status_menu(icon, btn, t))
            return si
        except Exception:
            return None


def _status_menu(icon, button, time):
    menu = Gtk.Menu()
    quit_item = Gtk.MenuItem(label="Quit CMD Launcher")
    quit_item.connect("activate", lambda *_: Gtk.main_quit())
    menu.append(quit_item)
    menu.show_all()
    menu.popup(None, None, Gtk.StatusIcon.position_menu, icon, button, time)


def main():
    parser = argparse.ArgumentParser(
        prog="cmd-launcher",
        description="Linux Command Cheatsheet Launcher"
    )
    parser.add_argument("--version", action="version",
                        version=f"cmd-launcher {__version__}")
    parser.parse_args()

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    library = CommandLibrary()
    window  = LauncherWindow(library)

    def on_hotkey():
        GLib.idle_add(window.toggle)

    hotkey = HotkeyListener(callback=on_hotkey)
    hotkey.start()

    tray = _try_appindicator(window)

    print(f"✅ CMD Launcher v{__version__} is running.")
    print("   Shortcut : Super + O")
    print("   Quit     : Ctrl + C  or tray → Quit\n")

    try:
        Gtk.main()
    except KeyboardInterrupt:
        pass
    finally:
        hotkey.stop()
        print("\n👋 Stopped.")


if __name__ == "__main__":
    main()
