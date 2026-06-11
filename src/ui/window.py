# src/ui/window.py
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
import subprocess


class LauncherWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="CMD Launcher")
        self.set_default_size(600, 400)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_keep_above(True)  # 提示 compositor 保持置頂
        self.connect("delete-event", self.hide_on_delete)
        self._build_ui()

    def _build_ui(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        self.add(box)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("搜尋指令...")
        box.pack_start(self.search_entry, False, False, 0)

        self.listbox = Gtk.ListBox()
        scroll = Gtk.ScrolledWindow()
        scroll.add(self.listbox)
        box.pack_start(scroll, True, True, 0)

    def hide_on_delete(self, *args):
        self.hide()
        return True  # 攔截關閉事件，只 hide 不 destroy

    def toggle(self):
        """由 SIGUSR1 觸發，GTK 主執行緒安全呼叫"""
        if self.get_visible():
            self.hide()
        else:
            self._do_show()

    def _do_show(self):
        self.show_all()
        if not self.get_realized():
            self.realize()
        # GTK3 在 WSLg 下能做的最大努力
        self.present()

        window = self.get_window()
        if window is not None:
            try:
                if hasattr(window, "get_xid"):
                    xid = window.get_xid()
                    if xid:
                        subprocess.Popen(
                            ["xdotool", "windowactivate", "--sync", str(xid)]
                        )
            except (FileNotFoundError, OSError):
                pass
            try:
                window.raise_()
            except Exception:
                pass
        # 真正的焦點搶佔由 Windows AHK 端處理（見下方 AHK 腳本）
