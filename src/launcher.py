# src/launcher.py
import argparse
import signal
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from ui.window import LauncherWindow
import os

APP_VERSION = "1.0.0"


def write_pid():
    with open("/tmp/cmd-launcher.pid", "w") as f:
        f.write(str(os.getpid()))


def main():
    parser = argparse.ArgumentParser(description="CMD Launcher")
    parser.add_argument(
        "-v", "--version", action="store_true", help="Print version and exit"
    )
    args = parser.parse_args()

    if args.version:
        print(f"v{APP_VERSION}")
        return

    write_pid()
    window = LauncherWindow()

    def on_sigusr1(signum, frame):
        # 必須透過 GLib.idle_add 回到 GTK 主執行緒
        GLib.idle_add(window.toggle)

    signal.signal(signal.SIGUSR1, on_sigusr1)

    # 啟動後隱藏，背景待命
    window.hide()
    Gtk.main()


if __name__ == "__main__":
    main()
