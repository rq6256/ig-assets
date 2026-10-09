"""Render sample sites (desktop + mobile) and compose Instagram mockups (1080x1350).

Usage: python3 render.py <site_dir_name> <works_no> <label_ja> <out_jpg>
"""
import sys, base64, pathlib, asyncio
from playwright.async_api import async_playwright

ROOT = pathlib.Path('/home/claude/ig-assets/sites')
WORK = pathlib.Path('/home/claude/work/mock')

TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;background:#F7F4EE;position:relative;overflow:hidden;font-family:"Noto Serif CJK JP",serif;color:#333}
.blob{position:absolute;right:-160px;top:420px;width:760px;height:760px;border-radius:50%;background:#E9EDE6}
.blob2{position:absolute;left:-200px;top:-180px;width:520px;height:520px;border-radius:50%;background:#EFEBE3}
.tag{position:absolute;left:84px;top:92px;border:1.5px solid #8A9A86;color:#6F806B;font:500 22px "Noto Sans CJK JP",sans-serif;letter-spacing:.3em;padding:8px 20px}
.title{position:absolute;left:84px;top:156px;font-size:58px;letter-spacing:.06em;font-weight:500}
.title span{color:#8A9A86;margin:0 18px;font-weight:400}
.sub{position:absolute;left:86px;top:252px;font:400 25px "Noto Sans CJK JP",sans-serif;color:#7A746C;letter-spacing:.12em}
.laptop{position:absolute;left:70px;top:390px;width:860px}
.lid{background:#26282B;border-radius:22px 22px 6px 6px;padding:18px 18px 22px;box-shadow:0 30px 60px rgba(60,55,45,.18)}
.lid img{display:block;width:100%;border-radius:4px}
.base{height:26px;margin:0 -46px;background:linear-gradient(#DCDCDE,#B9BABD);border-radius:2px 2px 18px 18px;position:relative}
.base:after{content:"";position:absolute;left:50%;top:0;width:150px;height:9px;margin-left:-75px;background:#A9AAAD;border-radius:0 0 10px 10px}
.phone{position:absolute;right:62px;top:640px;width:270px;padding:11px;background:#1F2023;border-radius:46px;box-shadow:0 30px 60px rgba(60,55,45,.25)}
.screen{border-radius:36px;overflow:hidden;background:{spbg};padding-top:34px}
.phone img{display:block;width:100%}
.notch{position:absolute;left:50%;top:22px;width:78px;height:22px;margin-left:-39px;background:#1F2023;border-radius:12px}
.foot{position:absolute;left:86px;bottom:78px;font:400 24px "Noto Sans CJK JP",sans-serif;color:#6F806B;letter-spacing:.14em}
.logo{position:absolute;right:70px;bottom:76px;font:italic 24px "Noto Serif CJK JP",serif;color:#8A8278;letter-spacing:.1em}
</style></head><body>
<div class="blob2"></div><div class="blob"></div>
<div class="tag">制作サンプル</div>
<div class="title">WORKS {no}<span>|</span>{label}</div>
<div class="sub">{name}</div>
<div class="laptop"><div class="lid"><img src="data:image/png;base64,{pc}"></div><div class="base"></div></div>
<div class="phone"><div class="screen"><img src="data:image/png;base64,{sp}"></div><div class="notch"></div></div>
<div class="foot">PC・スマホどちらでも見やすく</div>
<div class="logo">hibi web design</div>
</body></html>"""


async def main(site, no, label, name, out):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        url = (ROOT / site / 'index.html').as_uri()
        pc = await b.new_page(viewport={'width': 1440, 'height': 900}, device_scale_factor=1)
        await pc.goto(url); await pc.wait_for_timeout(800)
        pc_png = await pc.screenshot()
        sp = await b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        await sp.goto(url); await sp.wait_for_timeout(800)
        spbg = await sp.evaluate("getComputedStyle(document.querySelector('header')).backgroundColor !== 'rgba(0, 0, 0, 0)' ? getComputedStyle(document.querySelector('header')).backgroundColor : getComputedStyle(document.body).backgroundColor")
        sp_png = await sp.screenshot()
        (WORK / f'{site}-pc.png').write_bytes(pc_png)
        (WORK / f'{site}-sp.png').write_bytes(sp_png)
        html = TEMPLATE.replace('{no}', no).replace('{label}', label).replace('{name}', name).replace('{spbg}', spbg) \
            .replace('{pc}', base64.b64encode(pc_png).decode()).replace('{sp}', base64.b64encode(sp_png).decode())
        m = await b.new_page(viewport={'width': 1080, 'height': 1350}, device_scale_factor=1)
        await m.set_content(html); await m.wait_for_timeout(300)
        await m.screenshot(path=out, type='jpeg', quality=92)
        await b.close()

if __name__ == '__main__':
    asyncio.run(main(*sys.argv[1:6]))
