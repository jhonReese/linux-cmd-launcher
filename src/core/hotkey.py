"""
全域快捷鍵監聽模組
監聽 Ctrl+Alt+O（WSL/X11 相容版本）
Super 鍵在 WSL 會被 Windows 攔截，改用 Ctrl+Alt+O
"""
from pynput import keyboard
from typing import Callable, Set
import threading


class HotkeyListener:
    """
    監聽 Ctrl + Alt + O。
    - 只追蹤目標組合鍵，不記錄其他任何輸入
    - daemon thread，主程式結束自動清理
    - 支援 WSL / Linux X11 / Wayland
    """
    TARGET_COMBO = {
        keyboard.Key.ctrl,
        keyboard.Key.alt,
        keyboard.KeyCode.from_char('o')
    }

    def __init__(self, callback: Callable):
        self.callback   = callback
        self._pressed:  Set = set()
        self._lock      = threading.Lock()
        self._triggered = False
        self._listener  = None

    def _normalize(self, key):
        if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            return keyboard.Key.ctrl
        if key in (keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
            return keyboard.Key.alt
        return key

    def _on_press(self, key):
        with self._lock:
            norm = self._normalize(key)
            if norm in self.TARGET_COMBO:
                self._pressed.add(norm)
                if self.TARGET_COMBO.issubset(self._pressed) and not self._triggered:
                    self._triggered = True
                    threading.Thread(target=self.callback, daemon=True).start()

    def _on_release(self, key):
        with self._lock:
            norm = self._normalize(key)
            self._pressed.discard(norm)
            if norm in self.TARGET_COMBO:
                self._triggered = False

    def start(self):
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self._listener.daemon = True
        self._listener.start()

    def stop(self):
        if self._listener:
            self._listener.stop()
