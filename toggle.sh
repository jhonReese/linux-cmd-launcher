#!/bin/bash
VENV="/home/wsl/.local/share/cmd-launcher/.venv"
SRC="/home/wsl/.local/share/cmd-launcher/src"
PIDFILE="/tmp/cmd-launcher.pid"
LOGFILE="/tmp/cmd-launcher.log"

export DISPLAY=:0
export WAYLAND_DISPLAY=wayland-0
export XDG_RUNTIME_DIR=/run/user/$(id -u)

echo "[$(date)] toggle.sh triggered" >> /tmp/toggle-debug.log

# Simple logger
log() {
    echo "[$(date)] $*" >> /tmp/toggle-debug.log
}

# Environment sanity checks
if [ ! -d "$SRC" ]; then
    log "ERROR: source dir $SRC not found"
    echo "ERROR: source dir $SRC not found" >&2
    exit 2
fi

if [ ! -x "$VENV/bin/python3" ]; then
    # Try to auto-detect a common install location for the virtualenv
    alt1="$HOME/.local/share/cmd-launcher/.venv"
    alt2="$HOME/.local/share/$USER/.venv"
    if [ -x "$alt1/bin/python3" ]; then
        VENV="$alt1"
        log "Auto-detected VENV at $VENV"
    elif [ -x "$alt2/bin/python3" ]; then
        VENV="$alt2"
        log "Auto-detected VENV at $VENV"
    else
        log "virtualenv python not found at $VENV/bin/python3 — will fallback to system python if available"
        # Fallback: use system python if available
        if command -v python3 >/dev/null 2>&1; then
            PYEXE=$(command -v python3)
            log "Falling back to system python: $PYEXE"
            USE_SYSTEM_PYTHON=1
        else
            log "ERROR: no suitable python executable found"
            echo "ERROR: virtualenv python not found and system python unavailable" >&2
            exit 3
        fi
    fi
fi

if [ -z "$XDG_RUNTIME_DIR" ] || [ ! -d "$XDG_RUNTIME_DIR" ]; then
    log "WARNING: XDG_RUNTIME_DIR not set or missing: $XDG_RUNTIME_DIR"
    echo "WARNING: XDG_RUNTIME_DIR not set or missing: $XDG_RUNTIME_DIR" >&2
fi

if [ -z "$DISPLAY" ]; then
    log "WARNING: DISPLAY is empty"
    echo "WARNING: DISPLAY is empty" >&2
fi

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
    if [ "${USE_SYSTEM_PYTHON:-0}" = "1" ]; then
        PYCMD="$PYEXE"
    else
        PYCMD="$VENV/bin/python3"
    fi

    "$PYCMD" -S \
    "$SRC/launcher.py" >> "$LOGFILE" 2>&1 &

if [ $? -ne 0 ]; then
    log "ERROR: failed to launch $PYCMD"
    echo "ERROR: failed to launch $PYCMD" >&2
    exit 4
fi

if [ "${USE_SYSTEM_PYTHON:-0}" = "1" ]; then
    echo "WARNING: Launched with system python ($PYCMD). Consider installing the bundled venv for reproducible behavior: run the installer or create a venv at $alt1 and install required packages." >&2
    log "Launched with system python; recommended to create venv at $alt1"
fi

echo $! > "$PIDFILE"
echo "[$(date)] launched PID $(cat $PIDFILE)" >> /tmp/toggle-debug.log

# 等待啟動後自動顯示視窗
sleep 0.5
kill -USR1 $(cat "$PIDFILE")
echo "[$(date)] sent initial SIGUSR1 to show window" >> /tmp/toggle-debug.log

exit 0
