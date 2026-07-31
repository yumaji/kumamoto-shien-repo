from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
PAPER = "#f4f7f5"
CARD = "#ffffff"
LINE = "#dde4e0"
INK = "#20272a"
INK_SOFT = "#55605f"
GREEN = "#2e6e4e"

FONT = "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf"

# サイト本文と同じく IPAゴシックにはボールドが無いので、
# わずかにストロークを重ねて太字相当に見せる
def bold(d, xy, text, font, fill, w=1.0):
    d.text(xy, text, font=font, fill=fill, stroke_width=w, stroke_fill=fill)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# 内側のカード（サイトの .card と同じ見た目）
M = 48
d.rounded_rectangle([M, M, W - M, H - M], radius=20, fill=CARD, outline=LINE, width=2)

# 左端の緑のアクセント（サイトの被災者向けカードの帯と同じ発想）
d.rounded_rectangle([M, M, M + 14, H - M], radius=20, fill=GREEN)
d.rectangle([M + 8, M + 2, M + 14, H - M - 2], fill=GREEN)

x = 118
f_eyebrow = ImageFont.truetype(FONT, 44)
f_title = ImageFont.truetype(FONT, 96)
f_lead = ImageFont.truetype(FONT, 34)
f_url = ImageFont.truetype(FONT, 30)
f_note = ImageFont.truetype(FONT, 23)

bold(d, (x, 126), "令和8年熊本地震", f_eyebrow, GREEN, 0.8)
bold(d, (x, 200), "支援情報まとめ", f_title, INK, 1.6)

d.line([x, 356, W - 118, 356], fill=LINE, width=2)

d.text((x, 392), "義援金・ふるさと納税・ネット募金の窓口と、", font=f_lead, fill=INK_SOFT)
d.text((x, 440), "被災された方が使える支援をまとめています。", font=f_lead, fill=INK_SOFT)

bold(d, (x, 516), "kumamoto-shien.net", f_url, GREEN, 0.6)

note = "公式発表をもとに個人が作成した非公式のまとめです"
nw = d.textlength(note, font=f_note)
d.text((W - 118 - nw, 524), note, font=f_note, fill=INK_SOFT)

img.save("ogp.png", optimize=True)
print("saved 1200x630")
