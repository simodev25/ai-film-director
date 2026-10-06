"""Free local camera-placement board for scene_001 (PIL only, no model, no cost).

Reuses the geometry of the user-approved schematic floor plan
(references/schematic/loc_001/draw_plan.py, registry order 10).
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).with_name('scene_001-camera-plan.png')
W, H = 1800, 1100
im = Image.new('RGB', (W, H), (236, 233, 226))
d = ImageDraw.Draw(im)


def f(s):
    try:
        return ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', s)
    except OSError:
        return ImageFont.load_default()


F, FS, FB, FN = f(20), f(16), f(28), f(22)
U, ox, oy = 110, 120, 230
RW, RD = 6, 7


def P(x, y):
    return (ox + x * U, oy + y * U)


def R(x0, y0, x1, y1, **k):
    d.rectangle([*P(x0, y0), *P(x1, y1)], **k)


# exterior strip (rain) above the window wall
R(-0.6, -1.9, RW + 0.6, -0.05, fill=(40, 48, 58))
for i in range(0, int((RW + 1.2) * U), 18):
    x = ox - 0.6 * U + i
    d.line([x, oy - 1.85 * U, x - 10, oy - 1.7 * U], fill=(120, 150, 170), width=1)
    d.line([x + 6, oy - 1.1 * U, x - 4, oy - 0.95 * U], fill=(120, 150, 170), width=1)
d.text(P(0.0, -1.75), 'EXTÉRIEUR — pluie, nuit', font=FS, fill=(220, 225, 230))

# room (same geometry as approved schematic v2)
R(0, 0, RW, RD, fill=(205, 170, 120))
wall = (40, 40, 40)
d.line([*P(0, 0), *P(RW, 0)], fill=wall, width=12)
d.line([*P(RW, 0), *P(RW, RD)], fill=wall, width=12)
d.line([*P(0, 0), *P(0, 5.2)], fill=wall, width=12)
d.line([*P(0, 6.4), *P(0, RD)], fill=wall, width=12)
d.line([*P(0, RD), *P(RW, RD)], fill=wall, width=12)
R(1.9, -0.08, 3.9, 0.08, fill=(120, 170, 200))
d.line([*P(0, 5.2), *P(1.2, 5.2)], fill=(90, 60, 30), width=8)
d.arc([*P(-1.2, 4.0), *P(1.2, 6.4)], 0, 90, fill=(90, 60, 30), width=2)
d.text(P(-1.05, 5.65), 'porte', font=FS, fill=(30, 30, 30))
R(1.2, 2.7, 4.7, 5.3, fill=(60, 62, 66))
sofa = (70, 72, 76)
R(0.5, 1.5, 4.2, 2.6, fill=sofa, outline=(20, 20, 20), width=2)
R(0.5, 2.6, 1.6, 5.0, fill=sofa, outline=(20, 20, 20), width=2)
R(0.15, 0.4, 0.75, 1.0, fill=(140, 100, 60))
d.ellipse([*P(0.25, 0.5), *P(0.65, 0.9)], fill=(255, 190, 80))
d.ellipse([*P(0.9, 0.3), *P(1.5, 0.9)], fill=(60, 120, 60))
R(2.0, 3.0, 3.8, 4.4, fill=(130, 85, 45), outline=(60, 40, 20), width=2)
R(5.55, 0.2, 6.0, 2.1, fill=(100, 70, 40))
R(5.45, 2.6, 6.0, 5.8, fill=(120, 80, 45))
R(5.3, 3.1, 5.42, 5.3, fill=(30, 30, 30))
d.line([*P(5.28, 3.1), *P(5.28, 5.3)], fill=(90, 230, 160), width=4)
d.text(P(4.55, 4.05), 'TV', font=FN, fill=(20, 90, 60))
d.text(P(2.45, 2.0), 'canapé', font=FS, fill=(230, 230, 230))

# Marc path (dotted): door -> past cats -> front of sofa return
path = [(0.7, 5.8), (1.4, 5.5), (2.0, 4.9), (1.9, 3.9), (1.25, 3.8)]
for a, b in zip(path, path[1:]):
    d.line([*P(*a), *P(*b)], fill=(150, 30, 30), width=3)
d.ellipse([*P(1.1, 3.65), *P(1.4, 3.95)], fill=(150, 30, 30))
d.text(P(0.6, 3.05), 'Marc', font=FS, fill=(255, 210, 210))
# cats
d.ellipse([*P(2.1, 5.45), *P(2.35, 5.7)], fill=(110, 95, 75))
d.text(P(2.4, 5.55), 'tigré', font=FS, fill=(60, 50, 40))
d.ellipse([*P(3.0, 2.0), *P(3.25, 2.25)], fill=(235, 215, 170), outline=(120, 100, 60))
d.text(P(3.3, 2.0), 'Persan', font=FS, fill=(235, 225, 200))

# cats at the end of the scene (shot 10): beside Marc
d.ellipse([*P(1.15, 4.2), *P(1.4, 4.45)], outline=(110, 95, 75), width=3)
d.ellipse([*P(1.75, 3.7), *P(2.0, 3.95)], outline=(200, 180, 130), width=3)
# cameras: number, position, heading in degrees (0 = east/right, 90 = south/down)
CAMS = [
    (1, (2.9, -1.2), 100, 'move'),
    (2, (2.9, -0.15), 110, 'move'),
    (3, (2.4, 1.15), 115, None),
    (4, (2.5, 5.0), 160, None),
    (5, (2.4, 6.2), 260, None),
    (6, (2.7, 3.4), 135, None),
    (7, (3.4, 2.9), 165, None),
    (8, (3.0, 1.2), 95, None),
    (9, (2.3, 2.95), 150, None),
    (10, (0.25, 3.8), 0, None),
]
overlay = Image.new('RGBA', im.size, (0, 0, 0, 0))
od = ImageDraw.Draw(overlay)
for n, (x, y), head, kind in CAMS:
    cx, cy = P(x, y)
    if head is not None:
        a1, a2 = math.radians(head - 22), math.radians(head + 22)
        L = 0.75 * U
        od.polygon([(cx, cy), (cx + L * math.cos(a1), cy + L * math.sin(a1)),
                    (cx + L * math.cos(a2), cy + L * math.sin(a2))], fill=(210, 40, 40, 70), outline=(170, 30, 30, 255))
im.paste(Image.alpha_composite(im.convert('RGBA'), overlay).convert('RGB'))
d = ImageDraw.Draw(im)
for n, (x, y), head, kind in CAMS:
    cx, cy = P(x, y)
    if kind == 'move':
        a = math.radians(head)
        d.line([cx, cy, cx + 0.8 * U * math.cos(a), cy + 0.8 * U * math.sin(a)], fill=(255, 255, 255), width=3)
    if head is None:
        d.rectangle([cx - 16, cy - 16, cx + 16, cy + 16], outline=(170, 30, 30), width=3)
    d.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=(255, 255, 255), outline=(170, 30, 30), width=3)
    d.text((cx, cy), str(n), font=FS, fill=(170, 30, 30), anchor='mm')

# shot list
lx = ox + RW * U + 120
d.text((lx, 40), 'Scène 1 — le retour : placement caméra', font=FB, fill=(20, 20, 20))
d.text((lx, 80), 'Brouillon gratuit, sans IA · 10 plans · 48 s · coupes franches', font=F, fill=(70, 70, 70))
SHOTS = [
    ('01', '6 s', 'Dehors, pluie : avancée lente vers la baie vitrée'),
    ('02', '6 s', 'Traversée de la vitre ; au fond la porte s\'ouvre'),
    ('03', '4 s', 'Fixe : Marc entre, referme la porte (couloir faible, neutre)'),
    ('04', '6 s', 'Ras du sol : le tigré se frotte contre ses jambes'),
    ('05', '4 s', 'Bas : le Persan descend du canapé et s\'approche'),
    ('06', '4 s', 'Marc avance vers nous et passe sans regarder les chats'),
    ('07', '4 s', 'Il se laisse tomber sur le retour du canapé'),
    ('08', '4 s', 'Marc prend la télécommande et allume lui-même la TV'),
    ('09', '4 s', 'Visage 3/4 éclairé en vert par l\'écran'),
    ('10', '6 s', 'De dos, derrière Marc, vers la TV ; les chats à côté de lui'),
]
y = 140
for n, dur, txt in SHOTS:
    d.ellipse([lx, y - 2, lx + 30, y + 28], fill=(255, 255, 255), outline=(170, 30, 30), width=3)
    d.text((lx + 15, y + 13), str(int(n)), font=FS, fill=(170, 30, 30), anchor='mm')
    d.text((lx + 45, y + 2), f'{dur}  {txt}', font=F, fill=(30, 30, 30))
    y += 52
y += 20
for s in ['Cône rouge = ce que voit la caméra · trait blanc = mouvement',
          'Trait rouge = trajet de Marc · ronds pâles = chats à la fin (plan 10)',
          'Plans 01–09 : caméra côté baie (porte à droite, TV à gauche à l\'écran)',
          'Plan 10 : caméra derrière Marc, vers la TV (choix utilisateur)']:
    d.text((lx, y), s, font=FS, fill=(70, 70, 70))
    y += 30
im.save(OUT)
