#!/bin/bash
VENV="/home/wsl/.local/share/cmd-launcher/.venv"
SRC="/home/wsl/.local/share/cmd-launcher/src"
PIDFILE="/tmp/cmd-launcher.pid"
LOGFILE="/tmp/cmd-launcher.log"

export DISPLAY=:0
export WAYLAND_DISPLAY=wayland-0
export XDG_RUNTIME_DIR=/run/user/$(id -u)

echo "[$(date)] toggle.sh triggered" >> /tmp/toggle-debug.log

# 如果 process 已在執行，發送 SIGUSR1 切換視窗
if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if kill -0 "$PID" 2>/dev/null; then
        kill -USR1 "$PID"
        echo "[$(date)] sent SIGUSR1 to PID $PID" >> /tmp/toggle-debug.log
        exit 0
    fi
    rm -f "$PIDFILE"
fi

# 啟動新 process
nohup env -i \
    HOME=$HOME \
    PATH=/usr/bin:/bin \
    DISPLAY=$DISPLAY \
    WAYLAND_DISPLAY=$WAYLAND_DISPLAY \
    XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR \
    PYTHONPATH="$SRC:/usr/lib/python3/dist-packages:$VENV/lib/python3.10/site-packages" \
    "$VENV/bin/python3" -S \
    "$SRC/launcher.py" >> "$LOGFILE" 2>&1 &

echo $! > "$PIDFILE"
echo "[$(date)] launched PID $(cat $PIDFILE)" >> /tmp/toggle-debug.log

# 等待啟動後自動顯示視窗
sleep 0.5
kill -USR1 $(cat "$PIDFILE")
echo "[$(date)] sent initial SIGUSR1 to show window" >> /tmp/toggle-debug.log
