"""
主視窗 UI — GTK3
Apple 微暖美學 × DeepMind 前衛科技感
修正：__init__.py、相對 import、AppIndicator 托盤
"""
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GLib, Pango

import sys
import subprocess
import threading
from pathlib import Path

# 確保 src 在 path 中（修正 import 問題）
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.commands import CommandLibrary
from src.core.clipboard import copy_to_clipboard, run_in_terminal


# ── CSS 樣式（整合原 styles.css）────────────────────────────
CSS = """
* {
    font-family: "SF Pro Display", "Helvetica Neue", "Segoe UI", Ubuntu, sans-serif;
}

window#main-window {
    background-color: rgba(22, 20, 18, 0.97);
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 28px 80px rgba(0,0,0,0.32);
}

#main-window GtkBox {
    background-color: transparent;
}

/* ── Search ── */
#search-entry {
    background-color: rgba(255,255,255,0.07);
    border: 1.5px solid rgba(255,255,255,0.12);
    border-radius: 14px;
    color: #F0EDE8;
    font-size: 15px;
    padding: 12px 16px;
    caret-color: #E86A58;
}
#search-entry:focus {
    border-color: #4A90E2;
    background-color: rgba(255,255,255,0.11);
    box-shadow: 0 0 0 3px rgba(74,144,226,0.15);
}

/* ── Tab Bar ── */
#tab-bar {
    background-color: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 14px;
    padding: 6px 10px;
}
.tab-btn {
    background-color: rgba(255,255,255,0.05);
    border: 1px solid transparent;
    border-radius: 10px;
    color: rgba(255,255,255,0.55);
    font-size: 12px;
    font-weight: 700;
    padding: 6px 14px;
    transition: all 150ms ease;
}
.tab-btn:hover {
    background-color: rgba(255,255,255,0.12);
    color: rgba(255,255,255,0.9);
}
.tab-btn.active {
    background-color: rgba(28, 41, 60, 0.65);
    border-color: rgba(74,144,226,0.4);
    color: #FFFFFF;
}

/* ── Category Header ── */
.cat-header {
    color: rgba(255,255,255,0.60);
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.5px;
    padding: 10px 20px 3px 20px;
}

/* ── Command Row ── */
.cmd-row {
    border-radius: 18px;
    padding: 16px 16px;
    transition: background-color 120ms ease, transform 120ms ease;
    border: 1px solid rgba(255,255,255,0.12);
    background-color: rgba(255,255,255,0.04);
    margin-bottom: 8px;
}
.cmd-row:hover {
    background-color: rgba(255,255,255,0.14);
}
.cmd-row:selected {
    background-color: rgba(74,144,226,0.18);
}

.cmd-mono {
    color: #F7F5F2;
    font-family: "SF Mono", "JetBrains Mono", "Fira Code", "Cascadia Code", monospace;
    font-size: 13.5px;
    font-weight: 600;
}
.cmd-desc {
    color: rgba(255,255,255,0.75);
    font-size: 11.5px;
}
.cmd-cat-badge {
    color: rgba(255,255,255,0.85);
    background-color: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 999px;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 8px;
    margin-top: 4px;
}

/* ── Action Buttons ── */
.btn-copy {
    background-color: rgba(74,144,226,0.12);
    border: 1px solid rgba(74,144,226,0.25);
    border-radius: 7px;
    color: #4A90E2;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 9px;
    min-width: 52px;
}
.btn-copy:hover {
    background-color: rgba(74,144,226,0.25);
}
.btn-copy.ok {
    background-color: rgba(126,211,33,0.15);
    border-color: rgba(126,211,33,0.4);
    color: #7ED321;
}
.btn-run {
    background-color: rgba(232,106,88,0.14);
    border: 1px solid rgba(232,106,88,0.28);
    border-radius: 8px;
    color: #E86A58;
    font-size: 12px;
    font-weight: 700;
    padding: 6px 12px;
    min-width: 56px;
}
.btn-run:hover {
    background-color: rgba(232,106,88,0.28);
}
/* ── Scrollbar ── */
scrollbar { background-color: transparent; border: none; }
scrollbar slider {
    background-color: rgba(255,255,255,0.12);
    border-radius: 4px;
    min-width: 4px;
}

/* ── Footer ── */
#footer {
    color: rgba(255,255,255,0.50);
    font-size: 10.5px;
    padding: 5px 0 7px 0;
}

/* ── Count badge ── */
#count-lbl {
    color: rgba(255,255,255,0.60);
    font-size: 11px;
}
"""


class CommandRow(Gtk.ListBoxRow):
    def __init__(self, cmd: str, desc: str,
                 color: str = "#4A90E2", category: str = "",
                 library: CommandLibrary = None):
        super().__init__()
        self.cmd_text = cmd
        self.library  = library
        self.get_style_context().add_class("cmd-row")

        outer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        outer.set_margin_start(10)
        outer.set_margin_end(10)
        outer.set_margin_top(10)
        outer.set_margin_bottom(10)

        # 色彩指示條
        bar = Gtk.DrawingArea()
        bar.set_size_request(3, -1)
        bar.connect("draw", self._draw_bar, color)
        outer.pack_start(bar, False, False, 0)

        # 文字區塊
        txt = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        txt.set_hexpand(True)

        cmd_lbl = Gtk.Label(label=cmd, xalign=0)
        cmd_lbl.get_style_context().add_class("cmd-mono")
        cmd_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        cmd_lbl.set_xalign(0)
        cmd_lbl.set_line_wrap(False)
        txt.pack_start(cmd_lbl, False, False, 0)

        if category:
            cat_lbl = Gtk.Label(label=category, xalign=0)
            cat_lbl.get_style_context().add_class("cmd-cat-badge")
            cat_lbl.set_xalign(0)
            txt.pack_start(cat_lbl, False, False, 0)

        desc_lbl = Gtk.Label(label=desc, xalign=0)
        desc_lbl.get_style_context().add_class("cmd-desc")
        desc_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        desc_lbl.set_line_wrap(True)
        desc_lbl.set_max_width_chars(65)
        txt.pack_start(desc_lbl, False, False, 0)

        outer.pack_start(txt, True, True, 0)

        # 按鈕區
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)

        self.copy_btn = Gtk.Button(label="Copy")
        self.copy_btn.get_style_context().add_class("btn-copy")
        self.copy_btn.connect("clicked", self._on_copy)
        btn_box.pack_start(self.copy_btn, False, False, 0)

        run_btn = Gtk.Button(label="Run ▶")
        run_btn.get_style_context().add_class("btn-run")
        run_btn.connect("clicked", self._on_run)
        btn_box.pack_start(run_btn, False, False, 0)

        outer.pack_end(btn_box, False, False, 0)
        self.add(outer)

    def _draw_bar(self, w, cr, color):
        try:
            r = int(color[1:3], 16)/255
            g = int(color[3:5], 16)/255
            b = int(color[5:7], 16)/255
        except Exception:
            r, g, b = 0.29, 0.56, 0.89
        cr.set_source_rgba(r, g, b, 0.75)
        cr.rectangle(0, 5, 3, w.get_allocated_height() - 10)
        cr.fill()

    def _on_copy(self, btn):
        if self.library:
            self.library.record_use(self.cmd_text)
        ok = copy_to_clipboard(self.cmd_text)
        if ok:
            btn.set_label("✓ OK")
            btn.get_style_context().add_class("ok")
            GLib.timeout_add(1400, self._reset_copy_btn)

    def _reset_copy_btn(self):
        self.copy_btn.set_label("Copy")
        self.copy_btn.get_style_context().remove_class("ok")
        return False

    def _on_run(self, btn):
        if self.library:
            self.library.record_use(self.cmd_text)
        run_in_terminal(self.cmd_text)


class LauncherWindow(Gtk.Window):
    def __init__(self, library: CommandLibrary):
        super().__init__()
        self.set_name("main-window")
        self.library       = library
        self._search_timer = None
        self._current_tab  = "all"   # all | recent

        self._setup_window()
        self._apply_css()
        self._build_ui()
        self._show_tab("all")

    # ── 視窗設定 ──────────────────────────────────────────
    def _setup_window(self):
        self.set_title("CMD Launcher")
        self.set_default_size(760, 620)
        self.set_resizable(True)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)

        screen = Gdk.Screen.get_default()
        def _center_window(w):
            w.move((screen.get_width()-760)//2, (screen.get_height()-620)//2)
        self.connect("realize", _center_window)

        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)
        self.set_app_paintable(True)

        self.connect("key-press-event",  self._on_key)
        self.connect("focus-out-event",  lambda *_: self.hide())
        self.connect("draw",             self._on_draw)

    def _on_draw(self, widget, cr):
        """繪製圓角背景（需要 compositing）"""
        cr.set_source_rgba(0, 0, 0, 0)
        cr.set_operator(1)  # CLEAR
        cr.paint()
        return False

    def _apply_css(self):
        p = Gtk.CssProvider()
        p.load_from_data(CSS.encode("utf-8"))
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), p,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    # ── UI 建構 ───────────────────────────────────────────
    def _build_ui(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        root.set_margin_start(18)
        root.set_margin_end(18)
        root.set_margin_top(18)
        root.set_margin_bottom(14)
        self.add(root)

        # ── 標題列 ──
        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        icon_lbl = Gtk.Label()
        icon_lbl.set_markup(
            '<span foreground="#E86A58" font="18">⌨</span>'
            '<span foreground="#F0EDE8" font="15" font_weight="bold"> CMD Launcher</span>'
        )
        icon_lbl.set_hexpand(True)
        icon_lbl.set_xalign(0)
        hdr.pack_start(icon_lbl, True, True, 0)

        self._count_lbl = Gtk.Label(label="")
        self._count_lbl.set_name("count-lbl")
        hdr.pack_start(self._count_lbl, False, False, 8)

        close = Gtk.Button(label="✕")
        close.set_relief(Gtk.ReliefStyle.NONE)
        close.get_style_context().add_class("btn-close")
        close.connect("clicked", lambda *_: self.hide())
        close.set_tooltip_text("Close")
        hdr.pack_end(close, False, False, 0)
        root.pack_start(hdr, False, False, 0)

        # ── 搜尋框 ──
        self._search = Gtk.SearchEntry()
        self._search.set_name("search-entry")
        self._search.set_placeholder_text(
            "Search commands…   ↑↓ navigate  ·  Enter copy  ·  Shift+Enter run  ·  Esc close"
        )
        self._search.set_margin_top(14)
        self._search.set_margin_bottom(10)
        self._search.connect("changed", self._on_search)
        root.pack_start(self._search, False, False, 0)

        # ── Tab Bar ──
        tab_bar = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=4, name="tab-bar"
        )
        tab_bar.set_margin_bottom(6)

        self._tab_all    = Gtk.Button(label="All Commands")
        self._tab_recent = Gtk.Button(label="⏱ Recent")
        for btn, tab in [(self._tab_all, "all"), (self._tab_recent, "recent")]:
            btn.get_style_context().add_class("tab-btn")
            btn.connect("clicked", lambda b, t=tab: self._show_tab(t))
            tab_bar.pack_start(btn, False, False, 0)
        root.pack_start(tab_bar, False, False, 0)

        # ── 捲動清單 ──
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        self._scroll_adj = scroll.get_vadjustment()
        root.pack_start(scroll, True, True, 0)

        self._listbox = Gtk.ListBox()
        self._listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._listbox.set_activate_on_single_click(True)
        self._listbox.connect("row-activated", self._on_row_activated)
        scroll.add(self._listbox)

        # ── Footer ──
        footer = Gtk.Label(name="footer")
        footer.set_markup(
            '<span foreground="#999999" font="10.5">'
            'Ctrl+Alt+O toggle  ·  ↑↓ navigate  ·  Enter copy  ·  Shift+Enter run  ·  Esc close'
            '</span>'
        )
        footer.set_margin_top(10)
        root.pack_end(footer, False, False, 0)

    # ── Tab 切換 ──────────────────────────────────────────
    def _show_tab(self, tab: str):
        self._current_tab = tab
        for btn, t in [(self._tab_all, "all"), (self._tab_recent, "recent")]:
            ctx = btn.get_style_context()
            if t == tab: ctx.add_class("active")
            else:        ctx.remove_class("active")

        query = self._search.get_text().strip()
        if query:
            self._do_search(query)
        elif tab == "recent":
            self._populate_recent()
        else:
            self._populate_all()

    # ── 清單填充 ──────────────────────────────────────────
    def _clear(self):
        for c in self._listbox.get_children():
            self._listbox.remove(c)

    def _populate_all(self):
        self._clear()
        total = 0
        for cat in self.library.categories:
            # 分類標題
            hr = Gtk.ListBoxRow()
            hr.set_selectable(False)
            hr.set_activatable(False)
            lbl = Gtk.Label(label=cat["name"].upper(), xalign=0)
            lbl.get_style_context().add_class("cat-header")
            hr.add(lbl)
            self._listbox.add(hr)

            for item in cat.get("commands", []):
                row = CommandRow(
                    cmd=item["cmd"], desc=item["desc"],
                    color=cat.get("color","#4A90E2"),
                    library=self.library
                )
                self._listbox.add(row)
                total += 1

        self._count_lbl.set_text(f"{total} commands")
        self._listbox.show_all()

    def _populate_recent(self):
        self._clear()
        recent = self.library.recent
        if not recent:
            r = Gtk.ListBoxRow()
            r.set_selectable(False)
            lbl = Gtk.Label()
            lbl.set_markup(
                '<span foreground="rgba(255,255,255,0.4)" font="13">'
                'No recent commands yet</span>'
            )
            lbl.set_margin_top(30)
            r.add(lbl)
            self._listbox.add(r)
        else:
            for h in recent:
                cmd = h["cmd"]
                row = CommandRow(
                    cmd=cmd,
                    desc=f"Used: {h['time'][:16].replace('T',' ')}",
                    color="#F2A65A",
                    category="Recent",
                    library=self.library
                )
                self._listbox.add(row)
        self._count_lbl.set_text(f"{len(recent)} recent")
        self._listbox.show_all()

    def _populate_search(self, query: str):
        self._clear()
        results = self.library.search(query)
        if not results:
            r = Gtk.ListBoxRow()
            r.set_selectable(False)
            lbl = Gtk.Label()
            lbl.set_markup(
                f'<span foreground="rgba(255,255,255,0.3)" font="13">'
                f'No results for "{query}"</span>'
            )
            lbl.set_margin_top(30)
            r.add(lbl)
            self._listbox.add(r)
            self._count_lbl.set_text("0 results")
        else:
            for item in results:
                row = CommandRow(
                    cmd=item["cmd"], desc=item["desc"],
                    color=item.get("color","#4A90E2"),
                    category=item.get("category",""),
                    library=self.library
                )
                self._listbox.add(row)
            self._count_lbl.set_text(f"{len(results)} results")
        self._listbox.show_all()

    # ── 鍵盤導航 ──────────────────────────────────────────
    def _navigate_list(self, direction: int):
        """Move selection up (-1) or down (+1) through CommandRow items."""
        rows = [c for c in self._listbox.get_children()
                if isinstance(c, CommandRow)]
        if not rows:
            return
        selected = self._listbox.get_selected_row()
        if not isinstance(selected, CommandRow):
            target = rows[0] if direction == 1 else rows[-1]
        else:
            idx = rows.index(selected)
            target = rows[(idx + direction) % len(rows)]
        self._listbox.select_row(target)
        self._listbox.grab_focus()

        def _scroll_to():
            alloc = target.get_allocation()
            if alloc.y >= 0:
                self._scroll_adj.set_value(max(0, alloc.y - 60))
            return False
        GLib.idle_add(_scroll_to)

    # ── 事件處理 ──────────────────────────────────────────
    def _on_search(self, entry):
        if self._search_timer:
            GLib.source_remove(self._search_timer)
        self._search_timer = GLib.timeout_add(
            120, self._do_search, entry.get_text()
        )

    def _do_search(self, query: str):
        if query.strip():
            self._populate_search(query)
        elif self._current_tab == "recent":
            self._populate_recent()
        else:
            self._populate_all()
        self._search_timer = None
        return False

    def _on_row_activated(self, lb, row):
        if isinstance(row, CommandRow):
            row._on_copy(row.copy_btn)

    def _on_key(self, widget, event):
        keyval = event.keyval
        mods   = event.state

        if keyval == Gdk.KEY_Escape:
            self.hide()
            return True

        if keyval == Gdk.KEY_Down:
            self._navigate_list(1)
            return True

        if keyval == Gdk.KEY_Up:
            rows = [c for c in self._listbox.get_children()
                    if isinstance(c, CommandRow)]
            sel = self._listbox.get_selected_row()
            if rows and sel == rows[0]:
                # At top of list — return focus to search entry
                self._listbox.unselect_all()
                self._search.grab_focus()
            else:
                self._navigate_list(-1)
            return True

        if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            shift = bool(mods & Gdk.ModifierType.SHIFT_MASK)
            # Use selected row, or fall back to first CommandRow
            target = self._listbox.get_selected_row()
            if not isinstance(target, CommandRow):
                for child in self._listbox.get_children():
                    if isinstance(child, CommandRow):
                        target = child
                        break
            if isinstance(target, CommandRow):
                if shift:
                    target._on_run(None)   # Shift+Enter → Run in terminal
                else:
                    target._on_copy(target.copy_btn)  # Enter → Copy
            return True

        return False

    def toggle(self):
        visible = self.get_visible()
        active  = self.is_active()
        if visible and active:
            self.hide()
        elif visible and not active:
            self.present()
            self.grab_focus()
            GLib.idle_add(self._search.grab_focus)
        else:
            self._do_show()

    def _do_show(self):
        self._search.set_text("")
        self._show_tab("all")
        self.show_all()
        self.present()
        self.grab_focus()
        GLib.idle_add(self._search.grab_focus)
        GLib.timeout_add(100, self._do_raise)
        return False

    def _do_raise(self):
        self.set_keep_above(True)
        self.present()
        window = self.get_window()
        if window is not None:
            try:
                if hasattr(window, "get_xid"):
                    xid = window.get_xid()
                    if xid:
                        subprocess.Popen([
                            "xdotool", "windowactivate", "--sync", str(xid)
                        ])
            except (FileNotFoundError, OSError):
                pass
            except Exception:
                pass
        GLib.timeout_add(300, lambda: self.set_keep_above(False) or False)
        return False
