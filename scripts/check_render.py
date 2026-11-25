import os
from playwright.sync_api import sync_playwright

SRC = r"D:\Hermes\workspace\2026-11-25-gads-copy-skill\dist\HIITIO_review.html"
OUT = r"D:\Hermes\workspace\2026-11-25-gads-copy-skill\dist\shots"
os.makedirs(OUT, exist_ok=True)
url = "file:///" + SRC.replace('\\', '/')

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    for w, h, name in [(1440, 1000, "1440"), (768, 1100, "768"), (390, 844, "390")]:
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
        pg.goto(url, wait_until="load")
        pg.wait_for_timeout(400)
        m = pg.evaluate("""() => {
            const d = document.documentElement;
            let over = [];
            document.querySelectorAll('*').forEach(el => {
                const r = el.getBoundingClientRect();
                if (r.right > d.clientWidth + 1 && r.width > 0)
                    over.push(el.tagName + '.' + String(el.className||'').slice(0,20));
            });
            return {client: d.clientWidth, scroll: d.scrollWidth,
                    overflow: d.scrollWidth > d.clientWidth,
                    offenders: over.slice(0,5),
                    tables: document.querySelectorAll('table').length,
                    chips: document.querySelectorAll('.chip').length,
                    chipsOver: document.querySelectorAll('.chip.over').length,
                    bodyH: document.body.scrollHeight};
        }""")
        flag = "OVERFLOW" if (m["overflow"] or m["offenders"]) else "OK"
        print(f"[{name}] client={m['client']} scroll={m['scroll']} {flag} "
              f"tables={m['tables']} chips={m['chips']} over={m['chipsOver']} h={m['bodyH']}")
        if m["offenders"]:
            print("   越界:", m["offenders"])
        pg.screenshot(path=os.path.join(OUT, f"review_{name}.png"), full_page=False)
        pg.close()
    b.close()
print("shots saved:", OUT)
