"""hibi web design: Instagram carousel renderer (1080x1350 JPEG).

Usage:
  python3 autopost/render_carousel.py spec.json
spec.json:
{
  "id": "2026-10-12-mon",            # file prefix
  "slides": [
    {"type": "cover", "kicker": "保存版", "title": "スマホで見づらい\\nホームページの\\n特徴5つ", "sub": "当てはまったら要注意"},
    {"type": "point", "no": "01", "title": "文字が小さすぎる", "body": "スマホで拡大しないと読めない…\\n本文は16px以上が目安です。",
     "bad": "拡大しないと読めない", "good": "そのまま読める大きさ"},      # bad/good are optional
    {"type": "list", "title": "まとめ", "items": ["文字は16px以上", "ボタンは指で押せる大きさ"]},
    {"type": "cta"}
  ]
}
Writes images/auto/<id>-<n>.jpg (n starts at 1). Use \\n in text for line breaks.
"""
import json, sys, html, asyncio, pathlib
from playwright.async_api import async_playwright

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / 'images' / 'auto'

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;background:#F7F4EE;color:#333;position:relative;overflow:hidden;
 font-family:"Noto Sans CJK JP","Noto Sans JP",sans-serif}
.serif{font-family:"Noto Serif CJK JP","Noto Serif JP",serif}
.c1{position:absolute;left:-220px;top:-220px;width:560px;height:560px;border-radius:50%;background:#EFEBE3}
.c2{position:absolute;right:-240px;bottom:-200px;width:620px;height:620px;border-radius:50%;background:#E9EDE6}
.logo{position:absolute;right:72px;bottom:64px;font:italic 26px "Noto Serif CJK JP",serif;color:#8A8278;letter-spacing:.1em}
.page{position:absolute;left:84px;bottom:66px;font:500 22px "Noto Sans CJK JP",sans-serif;color:#A8A196;letter-spacing:.2em}
.wrap{position:absolute;left:96px;right:96px;top:150px;bottom:180px;display:flex;flex-direction:column}
.kicker{align-self:flex-start;background:#8A9A86;color:#fff;font-size:30px;letter-spacing:.2em;padding:10px 28px;border-radius:999px}
.cover h1{font-size:96px;line-height:1.42;font-weight:600;margin-top:56px;letter-spacing:.02em}
.cover .sub{font-size:38px;color:#6F806B;margin-top:44px;letter-spacing:.08em}
.cover .save{margin-top:auto;font-size:28px;color:#8A8278;letter-spacing:.1em}
.line{height:2px;width:120px;background:#8A9A86;margin:40px 0}
.no{font:500 30px "Noto Sans CJK JP",sans-serif;color:#8A9A86;letter-spacing:.3em}
.point h2{font-size:72px;line-height:1.45;font-weight:600;margin-top:20px}
.body{font-size:38px;line-height:1.9;color:#4A4640;letter-spacing:.04em}
.cmp{display:flex;gap:28px;margin-top:auto}
.box{flex:1;border-radius:24px;padding:34px 34px 38px;background:#fff}
.box b{display:block;font-size:30px;letter-spacing:.15em;margin-bottom:14px}
.box p{font-size:34px;line-height:1.6}
.bad b{color:#B08A7A}.good{background:#E4EAE1}.good b{color:#5F7A5B}
.list h2{font-size:72px;font-weight:600;margin-bottom:56px}
.list ul{list-style:none}
.list li{font-size:42px;line-height:1.5;padding:26px 0 26px 76px;position:relative;border-bottom:2px solid #E4DED3}
.list li:before{content:"";position:absolute;left:4px;top:34px;width:42px;height:42px;border-radius:50%;background:#8A9A86}
.list li:after{content:"";position:absolute;left:17px;top:42px;width:12px;height:22px;border:solid #fff;border-width:0 5px 5px 0;transform:rotate(45deg)}
.cta{align-items:center;justify-content:center;text-align:center}
.cta h2{font-size:82px;line-height:1.5;font-weight:600}
.cta p{font-size:38px;color:#6F6A62;margin:44px 0 64px;line-height:1.8}
.btn{background:#8A9A86;color:#fff;font-size:44px;letter-spacing:.08em;padding:30px 64px;border-radius:999px}
.cta .small{margin-top:44px;font-size:30px;color:#8A8278;line-height:1.8}
"""


def t(s):
    return html.escape(s).replace('\\n', '<br>').replace('\n', '<br>')


def slide_html(s, n, total):
    k = s['type']
    if k == 'cover':
        inner = f"""<div class="wrap cover">{f'<div class="kicker">{t(s["kicker"])}</div>' if s.get('kicker') else ''}
<h1 class="serif">{t(s['title'])}</h1>{f'<div class="sub">{t(s["sub"])}</div>' if s.get('sub') else ''}
<div class="save">保存して、あとで見返してください</div></div>"""
    elif k == 'point':
        cmp = ''
        if s.get('bad') or s.get('good'):
            cmp = f"""<div class="cmp"><div class="box bad"><b>× NG</b><p>{t(s.get('bad',''))}</p></div>
<div class="box good"><b>○ OK</b><p>{t(s.get('good',''))}</p></div></div>"""
        inner = f"""<div class="wrap point"><div class="no">POINT {t(s.get('no',''))}</div>
<h2 class="serif">{t(s['title'])}</h2><div class="line"></div><div class="body">{t(s.get('body',''))}</div>{cmp}</div>"""
    elif k == 'list':
        items = ''.join(f'<li>{t(i)}</li>' for i in s['items'])
        inner = f"""<div class="wrap list"><h2 class="serif">{t(s.get('title','まとめ'))}</h2><ul>{items}</ul></div>"""
    elif k == 'cta':
        inner = f"""<div class="wrap cta"><h2 class="serif">{t(s.get('title','ホームページのこと、\\n気軽にご相談ください'))}</h2>
<p>{t(s.get('body','初期費用0円・月1万円(税別)で\\n制作から更新までおまかせ'))}</p>
<div class="btn">「HP」とDMで無料相談</div><div class="small">プロフィールから制作サンプルも見られます</div></div>"""
    else:
        raise ValueError(k)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="c1"></div><div class="c2"></div>{inner}<div class="page">{n} / {total}</div><div class="logo">hibi web design</div></body></html>"""


async def main(spec_path):
    spec = json.loads(pathlib.Path(spec_path).read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    total = len(spec['slides'])
    paths = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1080, 'height': 1350})
        for i, s in enumerate(spec['slides'], 1):
            await pg.set_content(slide_html(s, i, total))
            await pg.wait_for_timeout(200)
            out = OUT / f"{spec['id']}-{i}.jpg"
            await pg.screenshot(path=str(out), type='jpeg', quality=92)
            paths.append(str(out.relative_to(REPO)))
        await b.close()
    print('\n'.join(paths))

if __name__ == '__main__':
    asyncio.run(main(sys.argv[1]))
