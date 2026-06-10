"""
執行一次即可產生 assets/icon.png
需要：pip install Pillow
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def generate():
    size = 64
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 圓形背景
    draw.ellipse([2, 2, size-2, size-2], fill="#E86A58")
    # 鍵盤圖示（簡化）
    draw.rectangle([14, 22, 50, 42], fill="white", outline="white", width=1)
    for x in range(16, 50, 8):
        draw.rectangle([x, 25, x+5, 30], fill="#E86A58")
    draw.rectangle([20, 34, 44, 39], fill="#E86A58")

    out = Path(__file__).parent / "icon.png"
    img.save(out)
    print(f"✅ Icon saved to {out}")

if __name__ == "__main__":
    generate()
