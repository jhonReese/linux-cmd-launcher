#!/bin/bash
# Create a 1x1 transparent GIF placeholder at assets/demo.gif
set -euo pipefail
mkdir -p "$(dirname "$(dirname "$0")")/assets" >/dev/null 2>&1 || true
cat > assets/demo.gif << 'BASE64'
R0lGODlhAQABAPAAAP///wAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==
BASE64
# decode
base64 -d assets/demo.gif > assets/demo.tmp && mv assets/demo.tmp assets/demo.gif
chmod 644 assets/demo.gif
echo "Created assets/demo.gif (1x1 transparent GIF)"
