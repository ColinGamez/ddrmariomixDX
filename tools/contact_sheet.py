import os, math
from PIL import Image, ImageDraw

roots = ['assets/boot_tex', 'assets/arrow_tex', 'assets/selmenu_tex']
items = []
for root in roots:
    for dirpath, _, files in os.walk(root):
        for f in sorted(files):
            if f.endswith('.png'):
                items.append(os.path.join(dirpath, f))

cell = 116
cols = 12
rows = math.ceil(len(items) / cols)
sheet = Image.new('RGBA', (cols * cell, rows * cell), (24, 28, 40, 255))
draw = ImageDraw.Draw(sheet)
for i, p in enumerate(items):
    img = Image.open(p).convert('RGBA')
    img.thumbnail((cell - 20, cell - 20))
    x = (i % cols) * cell
    y = (i // cols) * cell
    # checkerboard for alpha
    for cy in range(0, cell - 20, 8):
        for cx in range(0, cell - 20, 8):
            if (cx + cy) // 8 % 2:
                draw.rectangle([x + cx, y + cy, x + cx + 7, y + cy + 7], fill=(40, 46, 60, 255))
    sheet.paste(img, (x + 10 - img.width // 2 + (cell - 20) // 2, y + 10 - img.height // 2 + (cell - 20) // 2), img)
    name = os.path.basename(os.path.dirname(p)) + '/' + os.path.basename(p)[:12]
    draw.text((x + 2, y + cell - 12), name, fill=(180, 220, 255, 255))
sheet.convert('RGB').save('assets/contact_sheet.png')
print(len(items), 'textures -> assets/contact_sheet.png', sheet.size)
