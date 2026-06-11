#!/usr/bin/env bash
# Record a short demo and convert to GIF. Requires ffmpeg and gifsicle.
set -euo pipefail
OUT_DIR="assets"
OUT_NAME="demo.gif"
DURATION=${1:-5}
FPS=15
WIDTH=640
TMP_MP4="/tmp/cmd-launcher-demo.mp4"
mkdir -p "$OUT_DIR"
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg not found. Install ffmpeg to record demo." >&2
  exit 1
fi
if ! command -v gifsicle >/dev/null 2>&1; then
  echo "gifsicle not found. Install gifsicle to optimise GIF." >&2
  echo "You can still generate a GIF, but optimisation will be skipped."
  GIFSICLE=false
else
  GIFSICLE=true
fi
# Try to detect display for X11/WSLg
DISPLAY_VAR=${DISPLAY:-:0}
# Fallback to X11 grab size if possible; note WSLg may require a window compositor.
VIDEO_SIZE="${WIDTH}x480"
echo "Recording ${DURATION}s from display ${DISPLAY_VAR} with size ${VIDEO_SIZE}..."
ffmpeg -y -video_size "$VIDEO_SIZE" -framerate $FPS -f x11grab -i "$DISPLAY_VAR" -t $DURATION -vcodec libx264 -preset ultrafast "$TMP_MP4" || {
  echo "ffmpeg recording failed. Try adjusting DISPLAY, use a supported graphical session, or set a valid capture size." >&2
  exit 2
}
# Convert to GIF
ffmpeg -y -i "$TMP_MP4" -vf "fps=${FPS},scale=${WIDTH}:-1:flags=lanczos" -f gif - | gifsicle --optimize=3 --colors 256 > "$OUT_DIR/$OUT_NAME" || {
  # If gifsicle fails, try ffmpeg-only conversion
  ffmpeg -y -i "$TMP_MP4" -vf "fps=${FPS},scale=${WIDTH}:-1:flags=lanczos" "$OUT_DIR/$OUT_NAME"
}
rm -f "$TMP_MP4"
if [ "$GIFSICLE" = true ]; then
  echo "Optimized GIF saved to $OUT_DIR/$OUT_NAME"
else
  echo "GIF saved to $OUT_DIR/$OUT_NAME (not optimized)"
fi
