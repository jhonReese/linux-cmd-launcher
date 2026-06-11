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
    """在新終端機視窗中執行指令。"""
    candidates = [
        ["gnome-terminal", "--", "bash", "-ic", f"{cmd}; exec bash"],
        ["konsole", "-e", "bash", "-ic", f"{cmd}; exec bash"],
        ["xfce4-terminal", "-e", "bash", "-ic", f"{cmd}; exec bash"],
        ["tilix", "-e", "bash", "-ic", f"{cmd}; exec bash"],
        ["mate-terminal", "--", "bash", "-ic", f"{cmd}; exec bash"],
        ["lxterminal", "-e", "bash", "-ic", f"{cmd}; exec bash"],
        ["alacritty", "-e", "bash", "-lc", f"{cmd}; exec bash"],
        ["kitty", "bash", "-ic", f"{cmd}; exec bash"],
        ["terminator", "-x", "bash", "-ic", f"{cmd}; exec bash"],
        ["xterm", "-e", f"bash -ic '{cmd}; exec bash'"],
    ]

    for t in candidates:
        if shutil.which(t[0]):
            try:
                subprocess.Popen(t, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
                return True
            except Exception:
                continue

    # WSL / Windows Terminal fallback
    if shutil.which("wt.exe"):
        try:
            subprocess.Popen(
                ["wt.exe", "wsl", "bash", "-ic", f"{cmd}; exec bash"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            return True
        except Exception:
            pass

    if shutil.which("wsl.exe"):
        try:
            subprocess.Popen(
                ["wsl.exe", "bash", "-ic", f"{cmd}; exec bash"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            return True
        except Exception:
            pass

    return False
