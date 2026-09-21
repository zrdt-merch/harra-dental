"""
Membuat favicon, apple-touch-icon, icon PWA, dan og-image dari assets/logo.png
tanpa mengubah warna atau menggambar ulang logo.

Pemakaian (di folder repo):
    pip install pillow
    python make_assets.py

Hasil:
    favicon.ico
    assets/favicon-32.png, apple-touch-icon.png, icon-192.png, icon-512.png
    assets/og-image.png  (1200x630)
"""
from PIL import Image, ImageDraw, ImageFont, ImageChops

BG = (252, 251, 248)        # warm white
INK = (61, 59, 56)          # charcoal
MUTED = (107, 103, 95)
GOLD = (200, 155, 50)

# Ikon persegi diambil dari bagian kiri logo (huruf H + simbol gigi).
# Jika hasil crop kurang pas, ubah angka ini (1.0 = lebar sama dengan tinggi logo).
ICON_CROP_RATIO = 1.0

FONT_CANDIDATES = [
    "PlusJakartaSans-SemiBold.ttf", "PlusJakartaSans-Regular.ttf",
    "C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

def font(size):
    for p in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()

def trim(img):
    """Buang margin transparan / putih di sekeliling logo."""
    img = img.convert("RGBA")
    alpha = img.getchannel("A")
    if alpha.getextrema()[0] < 255:
        box = alpha.getbbox()
    else:
        white = Image.new("RGB", img.size, (255, 255, 255))
        diff = ImageChops.difference(img.convert("RGB"), white).convert("L").point(lambda v: 255 if v > 12 else 0)
        box = diff.getbbox()
    return img.crop(box) if box else img

def on_bg(img, size, pad_ratio=0.14):
    canvas = Image.new("RGB", (size, size), BG)
    inner = int(size * (1 - pad_ratio * 2))
    w, h = img.size
    scale = min(inner / w, inner / h)
    r = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    canvas.paste(r, ((size - r.width) // 2, (size - r.height) // 2), r)
    return canvas

logo = trim(Image.open("assets/logo.png"))
lw, lh = logo.size

# --- ikon persegi ---
side = min(lw, int(lh * ICON_CROP_RATIO))
icon_src = logo.crop((0, 0, side, lh))

on_bg(icon_src, 512).save("assets/icon-512.png", optimize=True)
on_bg(icon_src, 192).save("assets/icon-192.png", optimize=True)
on_bg(icon_src, 180, 0.12).save("assets/apple-touch-icon.png", optimize=True)
on_bg(icon_src, 32, 0.04).save("assets/favicon-32.png", optimize=True)
on_bg(icon_src, 256, 0.06).save("favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])

# --- OG image 1200x630 ---
W, H = 1200, 630
og = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(og)

target_w = 560
scale = target_w / lw
lg = logo.resize((target_w, int(lh * scale)), Image.LANCZOS)
if lg.height > 230:
    scale = 230 / lh
    lg = logo.resize((int(lw * scale), 230), Image.LANCZOS)

x = (W - lg.width) // 2
y = 150
og.paste(lg, (x, y), lg)

d.line([(W // 2 - 40, y + lg.height + 44), (W // 2 + 40, y + lg.height + 44)], fill=GOLD, width=3)

t1 = "Spesialis Konservasi Gigi Purwokerto"
f1 = font(38)
w1 = d.textlength(t1, font=f1)
d.text(((W - w1) / 2, y + lg.height + 76), t1, font=f1, fill=INK)

t2 = "Arcawinangun, Purwokerto Timur"
f2 = font(26)
w2 = d.textlength(t2, font=f2)
d.text(((W - w2) / 2, y + lg.height + 132), t2, font=f2, fill=MUTED)

og.save("assets/og-image.png", optimize=True)
print("Selesai: favicon.ico + assets/(favicon-32, apple-touch-icon, icon-192, icon-512, og-image)")
