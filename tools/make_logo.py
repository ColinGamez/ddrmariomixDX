"""Compose the ddrmariomixDX banner + icon from extracted game assets."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

W, H = 1600, 480
ARIBLK = 'C:/Windows/Fonts/ariblk.ttf'

# --- background: title-screen sky gradient (soft blue -> white) ---
bg = Image.new('RGBA', (W, H))
arr = np.zeros((H, W, 4), dtype=np.uint8)
top = np.array([120, 200, 245])
bot = np.array([255, 255, 255])
for y in range(H):
    t = y / (H - 1)
    arr[y, :, :3] = (top * (1 - t) + bot * t).astype(np.uint8)
    arr[y, :, 3] = 255
bg = Image.fromarray(arr, 'RGBA')

# --- rainbow ribbon swoosh (from the game's gosen ribbon texture, tinted stripes) ---
draw = ImageDraw.Draw(bg)
ribbon_cols = [(234, 60, 83), (255, 159, 28), (255, 220, 0), (76, 187, 23), (0, 142, 214), (155, 89, 182)]
base_y = H - 40
for i, c in enumerate(ribbon_cols):
    pts = []
    for x in range(0, W + 20, 20):
        import math
        y = base_y - i * 12 - 30 * math.sin((x / W) * 2 * math.pi + i * 0.35)
        pts.append((x, y))
    draw.line(pts, fill=c + (255,), width=11)

# --- Mario: crop the side-view figure from the earlier textured render ---
mario = Image.open('assets/mario/mario_textured.png').convert('RGBA')
right = mario.crop((760, 0, mario.width, mario.height))
a = np.array(right)
cols_nonzero = np.where(a[:, :, 3].max(axis=0) > 0)[0]
rows_nonzero = np.where(a[:, :, 3].max(axis=1) > 0)[0]
right = right.crop((cols_nonzero.min(), rows_nonzero.min(), cols_nonzero.max() + 1, rows_nonzero.max() + 1))
a = np.array(right)
white = (a[:,:,0] > 240) & (a[:,:,1] > 240) & (a[:,:,2] > 240)
a[:,:,3] = np.where(white, 0, 255)
right = Image.fromarray(a, 'RGBA')
scale = 400 / right.height
right = right.resize((int(right.width * scale), 400), Image.LANCZOS)
bg.paste(right, (70, H - right.height - 30), right)

# --- wordmark ---
def outlined_text(base, xy, text, font, fill, outline, ow=8):
    d = ImageDraw.Draw(base)
    x, y = xy
    for dx in range(-ow, ow + 1, 2):
        for dy in range(-ow, ow + 1, 2):
            if dx * dx + dy * dy <= ow * ow:
                d.text((x + dx, y + dy), text, font=font, fill=outline)
    d.text((x, y), text, font=font, fill=fill)

f_big = ImageFont.truetype(ARIBLK, 104)
f_ddr = ImageFont.truetype(ARIBLK, 66)
f_dx  = ImageFont.truetype(ARIBLK, 150)
f_sub = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 34)

# shadow layer
shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
outlined_text(shadow, (520, 60), 'DDR', f_ddr, (0, 0, 0, 160), (0, 0, 0, 160), 4)
outlined_text(shadow, (512, 132), 'MARIO MIX', f_big, (0, 0, 0, 160), (0, 0, 0, 160), 4)
shadow = shadow.filter(ImageFilter.GaussianBlur(6))
bg = Image.alpha_composite(bg, shadow)

outlined_text(bg, (520, 60), 'DDR', f_ddr, (255, 200, 0, 255), (160, 60, 0, 255), 7)
outlined_text(bg, (512, 140), 'MARIO MIX', f_big, (235, 30, 40, 255), (255, 255, 255, 255), 10)
outlined_text(bg, (1330, 122), 'DX', f_dx, (0, 140, 220, 255), (255, 255, 255, 255), 10)
d = ImageDraw.Draw(bg)
d.text((524, 310), 'a DDR Mario Mix decompilation + PC port project', font=f_sub, fill=(25, 60, 100, 255))

# --- music notes from the title screen, scattered ---
for src, xy, ang, s in [
    ('assets/boot_tex/c012/onpu_op00.png', (1330, 30), -18, 96),
    ('assets/boot_tex/c012/onpu_op01.png', (480, 320), 12, 72),
    ('assets/boot_tex/c012/onpu_op02.png', (1460, 330), -8, 84),
]:
    note = Image.open(src).convert('RGBA').resize((s, s), Image.LANCZOS).rotate(ang, expand=True, resample=Image.BICUBIC)
    bg.paste(note, xy, note)

bg.convert('RGB').save('assets/logo/banner.png')
print('banner ->', 'assets/logo/banner.png')

# --- square icon: Mario head-ish crop + DX badge ---
icon = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
d = ImageDraw.Draw(icon)
d.ellipse([8, 8, 504, 504], fill=(120, 200, 245, 255), outline=(255, 255, 255, 255), width=14)
m2 = right.resize((int(right.width * 440 / right.height), 440), Image.LANCZOS)
icon.paste(m2, (256 - m2.width // 2, 512 - m2.height - 20), m2)
f_dx2 = ImageFont.truetype(ARIBLK, 96)
outlined_text(icon, (345, 385), 'DX', f_dx2, (0, 140, 220, 255), (255, 255, 255, 255), 8)
icon.save('assets/logo/icon.png')
print('icon ->', 'assets/logo/icon.png')
