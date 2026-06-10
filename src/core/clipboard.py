"""剪貼簿工具：複製指令到系統剪貼簿（跨桌面環境）"""
import subprocess
import shutil


def copy_to_clipboard(text: str) -> bool:
    tools = [
        (["xclip", "-selection", "clipboard"], "xclip"),
        (["xsel", "--clipboard", "--input"],    "xsel"),
        (["wl-copy"],                            "wl-copy"),
    ]
    for cmd, bin_name in tools:
        if shutil.which(bin_name):
            try:
                proc = subprocess.Popen(
                    cmd, stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                proc.communicate(input=text.encode("utf-8"))
                return proc.returncode == 0
            except Exception:
                continue
    return False


def run_in_terminal(cmd: str) -> bool:
    """在新終端機視窗中執行指令（新增功能）"""
    terminals = [
        ["gnome-terminal", "--", "bash", "-c", f"{cmd}; exec bash"],
        ["xterm",          "-e", f"bash -c '{cmd}; exec bash'"],
        ["konsole",        "-e", f"bash -c '{cmd}; exec bash'"],
        ["xfce4-terminal", "-e", f"bash -c '{cmd}; exec bash'"],
    ]
    for t in terminals:
        if shutil.which(t[0]):
            try:
                subprocess.Popen(t, stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)
                return True
            except Exception:
                continue
    return False
