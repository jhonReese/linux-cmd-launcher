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
import math
import subprocess
import threading
from pathlib import Path

# 確保 src 在 path 中（修正 import 問題）
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.commands import CommandLibrary
from src.core.clipboard import copy_to_clipboard, run_in_terminal


# ── CSS 樣式 — Apple Warm Tech Dark ──────────────────────────
# Color tokens (Apple HIG dark mode, warm-shifted):
#   Window bg   : #141210   Card L1: #1E1C19   Card L2: #252220
#   Border      : #282420   Hover  : #2E2B27   Selected: #1B2D47
#   Text primary: #F5F5F7   Text 2 : #9A9590   Text 3  : #6E6A65
#   Blue accent : #4A90E2   Coral  : #E86A58   Green   : #34C759
CSS = """
* {
    font-family: "SF Pro Display", "Inter", "Helvetica Neue", Ubuntu, sans-serif;
}

window#main-window {
    background-color: #141210;
    border-radius: 14px;
    border: 1px solid #2A2724;
}

/* Kill default white backgrounds on GTK containers */
GtkListBox, list {
    background-color: transparent;
}
#main-window GtkBox,
#main-window GtkScrolledWindow,
#main-window GtkViewport {
    background-color: transparent;
}

/* ── Search ── */
#search-entry {
    background-color: #1E1C19;
    border: 1.5px solid #2E2B27;
    border-radius: 12px;
    color: #F5F5F7;
    font-size: 15px;
    padding: 12px 16px;
    caret-color: #E86A58;
}
#search-entry:focus {
    border-color: #4A90E2;
    background-color: #222018;
}

/* ── Tab Bar ── */
#tab-bar {
    background-color: #1A1815;
    border: 1px solid #282420;
    border-radius: 12px;
    padding: 5px 8px;
}
.tab-btn {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    color: #6E6A65;
    font-size: 12px;
    font-weight: 700;
    padding: 6px 14px;
}
.tab-btn:hover {
    background-color: #252220;
    color: #C8C4BE;
}
.tab-btn.active {
    background-color: #1B2D47;
    border-color: #2D4A70;
    color: #F5F5F7;
}

/* ── Category Header ── */
.cat-header {
    color: #6E6A65;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.5px;
    padding: 14px 20px 4px 20px;
}

/* ── Command Row ── */
row.cmd-row,
.cmd-row {
    border-radius: 12px;
    padding: 14px 16px;
    border: 1px solid #252220;
    background-color: #1E1C19;
    margin-bottom: 6px;
}
row.cmd-row:hover,
.cmd-row:hover {
    background-color: #252220;
    border-color: #2E2B27;
}
row.cmd-row:selected,
.cmd-row:selected,
row.cmd-row:focus,
.cmd-row:focus {
    background-color: #1B2D47;
    border-color: #4A90E2;
}

.cmd-mono {
    color: #F5F5F7;
    font-family: "SF Mono", "JetBrains Mono", "Fira Code", "Cascadia Code", monospace;
    font-size: 13.5px;
    font-weight: 600;
}
.cmd-desc {
    color: #9A9590;
    font-size: 11.5px;
}
.cmd-cat-badge {
    color: #A8A4A0;
    background-color: #252220;
    border: 1px solid #2E2B27;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 8px;
    margin-top: 4px;
}

/* ── Action Buttons ── */
.btn-copy {
    background-color: #1B2D47;
    border: 1px solid #2D4A70;
    border-radius: 8px;
    color: #4A90E2;
    font-size: 11px;
    font-weight: 700;
    padding: 5px 10px;
    min-width: 52px;
}
.btn-copy:hover {
    background-color: #243A5C;
}
.btn-copy.ok {
    background-color: #1A3020;
    border-color: #2A4F30;
    color: #34C759;
}
.btn-run {
    background-color: #3A1E1A;
    border: 1px solid #5A2E28;
    border-radius: 8px;
    color: #E86A58;
    font-size: 12px;
    font-weight: 700;
    padding: 5px 12px;
    min-width: 56px;
}
.btn-run:hover {
    background-color: #4A2820;
}

/* ── Scrollbar ── */
scrollbar { background-color: transparent; border: none; }
scrollbar slider {
    background-color: #3A3733;
    border-radius: 4px;
    min-width: 5px;
    min-height: 5px;
}
/* ── 強制覆蓋系統主題白底 ── */
list {
    background-color: #1C1A15;
    background-image: none;
}
listboxrow {
    background-color: transparent;
    background-image: none;
}
listboxrow:hover {
    background-color: rgba(255,255,255,0.07);
    background-image: none;
}
listboxrow:selected,
listboxrow:selected:focus {
    background-color: rgba(74,144,226,0.20);
    background-image: none;
}

/* ── Pin button ── */
.btn-pin {
    color: #6E6A65;
    font-size: 13px;
    padding: 2px 6px;
    border-radius: 6px;
}
.btn-pin.active {
    background-color: #2A3A20;
    color: #34C759;
}

/* ── Footer ── */
#footer {
    color: #6E6A65;
    font-size: 10.5px;
    padding: 5px 0 7px 0;
}

/* ── Count badge ── */
#count-lbl {
    color: #9A9590;
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
        # Force dark background — overrides GTK theme default (white) on ListBoxRow
        dark = Gdk.RGBA()
        dark.parse("#1E1C19")
        self.override_background_color(Gtk.StateFlags.NORMAL, dark)
        hover = Gdk.RGBA()
        hover.parse("#252220")
        self.override_background_color(Gtk.StateFlags.PRELIGHT, hover)
        sel = Gdk.RGBA()
        sel.parse("#1B2D47")
        self.override_background_color(Gtk.StateFlags.SELECTED, sel)

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
        self.connect("realize",        lambda *_: GLib.timeout_add(80, self._setup_shape))
        self.connect("configure-event", lambda *_: GLib.idle_add(self._setup_shape))

        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)
        self.set_app_paintable(True)

        self._pinned = False
        self.connect("key-press-event",  self._on_key)
        self.connect("focus-out-event",  self._on_focus_out)

    def _apply_css(self):
        p = Gtk.CssProvider()
        p.load_from_data(CSS.encode("utf-8"))
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), p,
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    def _setup_shape(self):
        """Clip window to a rounded rectangle using X11 shape extension.
        Works without a compositor — no alpha blending needed."""
        gdk_win = self.get_window()
        if gdk_win is None:
            return False
        w, h = self.get_size()   # actual window size, not layout allocation
        if w < 2 or h < 2:
            return False
        try:
            import cairo as _cairo
            r = 14
            surf = _cairo.ImageSurface(_cairo.Format.A8, w, h)
            ctx  = _cairo.Context(surf)
            ctx.set_source_rgba(1, 1, 1, 1)
            ctx.arc(r,     r,     r, math.pi,       3 * math.pi / 2)
            ctx.arc(w - r, r,     r, -math.pi / 2,  0)
            ctx.arc(w - r, h - r, r, 0,              math.pi / 2)
            ctx.arc(r,     h - r, r, math.pi / 2,   math.pi)
            ctx.close_path()
            ctx.fill()
            region = Gdk.cairo_region_create_from_surface(surf)
            gdk_win.shape_combine_region(region, 0, 0)
        except Exception:
            pass  # cairo unavailable or WSLg quirk — fall back to CSS radius
        return False

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
            '<span foreground="#E86A58" font="17">⌨</span>'
            '<span foreground="#F5F5F7" font="15" font_weight="bold"> CMD Launcher</span>'
        )
        icon_lbl.set_hexpand(True)
        icon_lbl.set_xalign(0)
        hdr.pack_start(icon_lbl, True, True, 0)

        self._count_lbl = Gtk.Label(label="")
        self._count_lbl.set_name("count-lbl")
        hdr.pack_start(self._count_lbl, False, False, 8)

        self._pin_btn = Gtk.Button(label="📌")
        self._pin_btn.set_relief(Gtk.ReliefStyle.NONE)
        self._pin_btn.get_style_context().add_class("btn-pin")
        self._pin_btn.connect("clicked", self._toggle_pin)
        self._pin_btn.set_tooltip_text("Pin — stay visible when focus leaves")
        hdr.pack_end(self._pin_btn, False, False, 0)

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
            '<span foreground="#6E6A65" font="10.5">'
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

    # ── Pin ───────────────────────────────────────────────
    def _toggle_pin(self, *_):
        self._pinned = not self._pinned
        ctx = self._pin_btn.get_style_context()
        if self._pinned:
            ctx.add_class("active")
        else:
            ctx.remove_class("active")

    def _on_focus_out(self, widget, event):
        if not self._pinned:
            self.hide()

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
