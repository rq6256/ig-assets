"""Render highlight stories (1080x1920) into images/highlight/."""
import asyncio, pathlib, base64
from playwright.async_api import async_playwright
REPO=pathlib.Path(__file__).resolve().parent.parent
OUT=REPO/'images'/'highlight'
BASE="""*{margin:0;padding:0;box-sizing:border-box}body{width:1080px;height:1920px;background:#F7F4EE;color:#333;font-family:"Noto Sans CJK JP",sans-serif;position:relative;overflow:hidden}
.serif{font-family:"Noto Serif CJK JP",serif;font-weight:500}.logo{position:absolute;left:0;right:0;bottom:120px;text-align:center;font:italic 30px "Noto Serif CJK JP",serif;color:#8A8278;letter-spacing:.1em}
.wrap{position:absolute;left:96px;right:96px;top:300px}.kick{display:inline-block;background:#8A9A86;color:#fff;font-size:30px;letter-spacing:.2em;padding:10px 30px;border-radius:999px}
h1{font-size:80px;line-height:1.45;margin:40px 0 50px}.card{background:#fff;border-radius:28px;padding:40px 44px;margin-bottom:26px}
.card b{display:block;color:#8A9A86;font-size:30px;letter-spacing:.15em;margin-bottom:8px}.card p{font-size:40px;line-height:1.6}
.card p.big{font-size:120px;line-height:1.2;color:#333}.card p.big small{font-size:44px}.dm{position:absolute;left:96px;right:96px;bottom:250px;background:#8A9A86;color:#fff;text-align:center;font-size:44px;padding:34px;border-radius:999px;letter-spacing:.06em}"""
def page(inner): return f'<html><head><meta charset="utf-8"><style>{BASE}</style></head><body>{inner}<div class="logo">hibi web design</div></body></html>'
S={}
S['price-1']=page('''<div class="wrap"><span class="kick">PRICE</span><h1 class="serif">料金</h1>
<div class="card"><b>初期費用</b><p class="big serif">0<small>円</small></p></div>
<div class="card"><b>月額</b><p class="big serif">1万<small>円(税別)</small></p></div>
<div class="card"><b>月額にふくまれるもの</b><p>・5ページまでのホームページ制作<br>・更新・修正 月3回まで<br>・Google検索・Googleマップ対策</p></div></div>
<div class="dm">「HP」とDMで無料相談</div>''')
S['flow-1']=page('''<div class="wrap"><span class="kick">FLOW</span><h1 class="serif">ご依頼の流れ</h1>
<div class="card"><b>STEP 1</b><p>「HP」とDMを送る</p></div>
<div class="card"><b>STEP 2</b><p>お店のこと・ご希望をヒアリング</p></div>
<div class="card"><b>STEP 3</b><p>デザイン案をご提案(無料)</p></div>
<div class="card"><b>STEP 4</b><p>制作・公開</p></div>
<div class="card"><b>STEP 5</b><p>公開後の更新もおまかせ</p></div></div>''')
S['qa-1']=page('''<div class="wrap"><span class="kick">Q&amp;A</span><h1 class="serif">よくある質問</h1>
<div class="card"><b>Q. パソコンが苦手でも大丈夫?</b><p>大丈夫です。変えたい内容を送っていただければ、こちらで反映します(月3回まで込み)。</p></div>
<div class="card"><b>Q. お店の写真がなくても作れる?</b><p>スマホで撮った写真でOK。きれいに撮るコツもお伝えします。</p></div>
<div class="card"><b>Q. 今あるサイトの作り直しもできる?</b><p>はい。リニューアルのご相談も歓迎です。</p></div></div>
<div class="dm">「HP」とDMで気軽にご質問ください</div>''')
for n in range(1,7):
    S[f'works-{n}']=page(f'''<div style="position:absolute;left:0;right:0;top:240px;text-align:center"><span class="kick">WORKS</span></div>
<img src="data:image/jpeg;base64,{base64.b64encode((REPO/"images"/f"hibi-pin-{n}.jpg").read_bytes()).decode()}" style="position:absolute;left:100px;top:360px;width:880px;border-radius:24px;box-shadow:0 20px 50px rgba(0,0,0,.08)">
<div class="dm" style="bottom:250px;font-size:38px">実際のサイトはプロフィールのリンクから</div>''')
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1080,'height':1920})
        for k,h in S.items():
            await pg.set_content(h); await pg.wait_for_timeout(300)
            await pg.screenshot(path=str(OUT/f'st-{k}.jpg'),type='jpeg',quality=90)
        await b.close()
asyncio.run(main())
