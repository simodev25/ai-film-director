"""Local schematic floor plan of loc_001 (PIL only, no model, no cost)."""
from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFont

CLEAN = '--clean' in sys.argv  # no text, legend or camera marker (model conditioning)

OUT = Path(__file__).with_name('floor-plan-schematic-v2-clean.png' if CLEAN else 'floor-plan-schematic-v2.png')
W, H = 1600, 1000
im = Image.new('RGB', (W, H), (236, 233, 226))
d = ImageDraw.Draw(im)


def f(s):
    try:
        return ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', s)
    except OSError:
        return ImageFont.load_default()


F, FS, FB = f(22), f(18), f(30)
U = 115
ox, oy = 170, 90
RW, RD = 6, 7


def R(x0, y0, x1, y1, **k):
    d.rectangle([ox + x0 * U, oy + y0 * U, ox + x1 * U, oy + y1 * U], **k)


def T(x, y, s, font=F, fill=(30, 30, 30), anchor='mm'):
    if CLEAN:
        return
    d.text((ox + x * U, oy + y * U), s, font=font, fill=fill, anchor=anchor)


R(0, 0, RW, RD, fill=(205, 170, 120))
wall, t = (40, 40, 40), 12
d.line([ox, oy, ox + RW * U, oy], fill=wall, width=t)
d.line([ox + RW * U, oy, ox + RW * U, oy + RD * U], fill=wall, width=t)
d.line([ox, oy, ox, oy + 5.2 * U], fill=wall, width=t)
d.line([ox, oy + 6.4 * U, ox, oy + RD * U], fill=wall, width=t)
for x in range(0, int(RW * U), 24):
    d.line([ox + x, oy + RD * U, ox + x + 12, oy + RD * U], fill=(120, 120, 120), width=4)
R(1.9, -0.08, 3.9, 0.08, fill=(120, 170, 200))
T(2.9, -0.35, 'BAIE VITRÉE (ville de nuit)', FS)
R(1.6, 0.05, 1.9, 0.25, fill=(170, 160, 140))
R(3.9, 0.05, 4.2, 0.25, fill=(170, 160, 140))
T(2.9, 0.45, 'rideaux', FS, (90, 80, 60))
d.line([ox, oy + 5.2 * U, ox + 1.2 * U, oy + 5.2 * U], fill=(90, 60, 30), width=8)
d.arc([ox - 1.2 * U, oy + 4.0 * U, ox + 1.2 * U, oy + 6.4 * U], 0, 90, fill=(90, 60, 30), width=2)
T(-0.7, 5.7, 'ENTRÉE', FS)
T(-0.7, 6.0, '(couloir)', FS)
R(0.05, 6.45, 0.35, 6.9, fill=(60, 60, 60))
T(0.45, 6.7, 'porte-manteau', FS, anchor='lm')
R(1.2, 2.7, 4.7, 5.3, fill=(60, 62, 66))
T(4.2, 5.05, 'tapis sombre', FS, (220, 220, 220))
sofa = (70, 72, 76)
R(0.5, 1.5, 4.2, 2.6, fill=sofa, outline=(20, 20, 20), width=3)
R(0.5, 2.6, 1.6, 5.0, fill=sofa, outline=(20, 20, 20), width=3)
R(0.5, 1.5, 4.2, 1.85, fill=(50, 52, 56))
R(0.5, 1.5, 0.85, 5.0, fill=(50, 52, 56))
T(2.6, 2.2, 'CANAPÉ EN L (gris foncé)', F, (240, 240, 240))
T(1.2, 3.9, 'plaid', FS, (220, 220, 220))
R(0.15, 0.4, 0.75, 1.0, fill=(140, 100, 60))
d.ellipse([ox + 0.25 * U, oy + 0.5 * U, ox + 0.65 * U, oy + 0.9 * U], fill=(255, 190, 80))
T(0.15, 0.25, 'lampe ambrée', FS, anchor='lm')
d.ellipse([ox + 0.9 * U, oy + 0.3 * U, ox + 1.5 * U, oy + 0.9 * U], fill=(60, 120, 60))
T(1.75, 0.6, 'plante', FS, anchor='lm')
R(2.0, 3.0, 3.8, 4.4, fill=(130, 85, 45), outline=(60, 40, 20), width=3)
T(2.9, 3.7, 'TABLE BASSE', F, (250, 240, 220))
R(5.55, 0.2, 6.0, 2.1, fill=(100, 70, 40), outline=(40, 30, 20), width=2)
T(5.45, 1.15, 'bibliothèque', FS, anchor='rm')
R(5.45, 2.6, 6.0, 5.8, fill=(120, 80, 45), outline=(40, 30, 20), width=2)
R(5.3, 3.1, 5.42, 5.3, fill=(30, 30, 30))
d.line([ox + 5.28 * U, oy + 3.1 * U, ox + 5.28 * U, oy + 5.3 * U], fill=(90, 230, 160), width=4)
T(5.15, 4.0, 'TV', FB, (20, 90, 60), anchor='rm')
T(5.2, 5.55, 'face au canapé', FS, (20, 90, 60), anchor='rm')
T(5.4, 6.05, 'meuble TV', FS, anchor='rm')
d.ellipse([ox + 5.5 * U, oy + 5.85 * U, ox + 5.95 * U, oy + 6.3 * U], fill=(60, 120, 60))
cx, cy = ox + 0.6 * U, oy + 6.6 * U
if not CLEAN:
    d.polygon([(cx, cy), (cx + 0.9 * U, cy - 1.3 * U), (cx + 1.6 * U, cy - 0.6 * U)], fill=(200, 40, 40))
T(2.4, 6.6, 'caméra de la planche quatre angles', FS, (170, 30, 30), anchor='lm')
T(3.0, 7.35, 'mur côté caméra : non montré sur les images (pointillés)', FS, (90, 90, 90))
# v2: framed pictures seen on panel-top-right (user: « il manque un tableau »)
R(0.03, 1.15, 0.12, 1.75, fill=(20, 20, 20))
T(0.2, 1.3, 'tableau', FS, anchor='lm')
R(5.88, 2.15, 5.97, 2.75, fill=(20, 20, 20))
T(5.8, 2.38, 'tableau', FS, anchor='rm')
lx = ox + RW * U + 160
if not CLEAN:
  d.text((lx, oy), 'Salon loc_001 — plan schématique v2', font=FB, fill=(20, 20, 20))
if not CLEAN:
 for i, s in enumerate(['Brouillon gratuit, dessiné localement (sans IA).',
                       'Lu depuis la planche quatre angles.',
                       'Vue de dessus, baie vitrée en haut.',
                       'Échelle approximative, sans mesures.',
                       "À corriger par l'utilisateur."]):
  d.text((lx, oy + 60 + i * 34), s, font=F, fill=(50, 50, 50))
im.save(OUT)
