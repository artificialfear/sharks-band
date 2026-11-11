"""Rebuild the IHS Sharks logo as 'IHS BAND' with clean transparent edges.
Letters: Anton (IHS) and Archivo Black (BAND), sheared for italic,
white fill + teal inner stroke + black outer stroke. The clean standalone shark sits on top.
"""
import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from scipy import ndimage as nd

S = 2                       # supersample factor; final output is 1000x1000
W = H = 1000 * S
TEAL = (35, 150, 146)
ANTON = '/tmp/fonts/fontsource-anton-5.3.0/package/files/anton-latin-400-normal.ttf'
ARCHIVO = '/tmp/fonts/fontsource-archivo-black-5.3.0/package/files/archivo-black-latin-400-normal.ttf'
SHARK = '/home/claude/sharks-band/assets/shark.png'
OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/logo/ihs-band-logo.png'

def text_mask(txt, font_path, box, shear=0.17, tracking=0.0):
    """Render txt, fit it exactly into box=(x0,y0,x1,y1) on the canvas, then shear (italic)."""
    f = ImageFont.truetype(font_path, 600)
    # draw letter by letter so we can control tracking
    widths = [f.getbbox(c)[2] - f.getbbox(c)[0] for c in txt]
    gap = int(tracking * 600)
    tw = sum(widths) + gap * (len(txt) - 1) + 200
    tmp = Image.new('L', (tw, 1000), 0); d = ImageDraw.Draw(tmp)
    x = 100
    for c, w in zip(txt, widths):
        bx = f.getbbox(c)
        d.text((x - bx[0], 100), c, font=f, fill=255); x += w + gap
    tmp = tmp.crop(tmp.getbbox())
    x0, y0, x1, y1 = [v * S for v in box]
    bw, bh = x1 - x0, y1 - y0
    # pre-shrink width so the sheared result fits the box
    inner_w = int(bw - shear * bh)
    tmp = tmp.resize((inner_w, bh), Image.LANCZOS)
    # shear: x' = x + shear*(h - y)  (slants to the right)
    sh = tmp.transform((bw, bh), Image.AFFINE, (1, shear, -shear * bh, 0, 1, 0), Image.BICUBIC)
    canvas = Image.new('L', (W, H), 0); canvas.paste(sh, (x0, y0))
    return np.asarray(canvas).astype(float) / 255

def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]; return (x * x + y * y) <= r * r

def grow(m, r):
    return nd.grey_dilation(m, footprint=disk(int(r * S)))

ihs  = text_mask('IHS',  ANTON,   (262, 45, 838, 492), shear=0.11, tracking=0.03)
band = text_mask('BAND', ARCHIVO, (58, 512, 942, 792), shear=0.12, tracking=0.03)
letters = np.maximum(ihs, band)

black = grow(letters, 26)            # outer black stroke (merges the two words into one badge)
teal  = grow(letters, 9)             # teal inner stroke

img = np.zeros((H, W, 4))
def layer(mask, rgb):
    a = mask[..., None]
    img[..., :3] = img[..., :3] * (1 - a) + np.array(rgb) * a
    img[..., 3:] = img[..., 3:] * (1 - a) + 255 * a
layer(black, (0, 0, 0))
layer(teal, TEAL)
layer(letters, (255, 255, 255))
base = Image.fromarray(img.clip(0, 255).astype(np.uint8), 'RGBA')

# shark: same placement as the original logo (scale 0.714 of the 1024px cutout, at 140,236 on a 1000 canvas)
sh = Image.open(SHARK).convert('RGBA')
sc = 0.714 * S
sh = sh.resize((round(sh.width * sc), round(sh.height * sc)), Image.LANCZOS)
base.alpha_composite(sh, (140 * S, 236 * S))

out = base.resize((1000, 1000), Image.LANCZOS)
out = out.crop(out.getbbox())
out.save(OUT, optimize=True)
print(OUT, out.size)
