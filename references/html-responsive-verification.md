# HTML 多断点渲染验证（含 Edge headless 视口陷阱）

本 skill 会产出 `*_review.html` 审阅页，**必须验证它在真实断点下不横向溢出**，
而不是靠肉眼扫一眼截图。下面是踩过的坑和可复用的探针。

## ⚠️ 头号陷阱：Edge/Chrome headless 的 `--window-size` 有最小宽度

```
msedge --headless=new --screenshot=out.png --window-size=390,900 file:///...
```

实测结果：

| 传入 `--window-size` | 实际 `window.innerWidth` | 截图宽度 |
|---|---|---|
| 1440 | 1408 | 1440 |
| 1280 | 1248 | 1280 |
| 768 | 736 | 768 |
| **390** | **510** `←被强制放大` | **390** `←被裁切` |
| **360** | **510** `←被强制放大` | 360 |

**后果**：页面按 510px 排版，却只截了左边 390px。
看上去像"内容被截断"，实际是**测量方法错了**，页面本身没有毛病。

2026-11 就因此误判过一次：视觉模型说"右侧内容被裁切"，我据此改了 CSS。
后来用 JS 探针实测 `scrollWidth === clientWidth`、零越界元素，才发现是工具限制。
**先量，再改。** 不要根据 headless 截图下"布局坏了"的结论。

## 正确做法：Playwright + msedge，显式 viewport

`channel="msedge"` 是这台机器的必需参数（Chrome 起不来，os error 14001）。

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    for w, h in [(1440, 1000), (1280, 1000), (768, 1100), (390, 844), (360, 800)]:
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
        pg.goto(url, wait_until="load")
        pg.wait_for_timeout(400)
        m = pg.evaluate("""() => {
            const d = document.documentElement;
            const over = [];
            document.querySelectorAll('*').forEach(el => {
                const r = el.getBoundingClientRect();
                if (r.right > d.clientWidth + 1 && r.width > 0)
                    over.push(el.tagName + '.' + String(el.className||'').slice(0,20));
            });
            return {inner: window.innerWidth, client: d.clientWidth, scroll: d.scrollWidth,
                    overflow: d.scrollWidth > d.clientWidth, offenders: over.slice(0,6)};
        }""")
        print(w, m)
        pg.screenshot(path=f"shot_{w}.png")
```

Playwright 的 viewport 是**真实的 CSS 视口**，390 就是 390。

## 判定标准

```python
ok = (m["scroll"] == m["client"]) and not m["offenders"]
```

- `scrollWidth == clientWidth` 且 `offenders` 为空 → 无横向溢出
- 只看截图不算验证；只跑一个断点也不算

**必测断点**：1440 / 1280 / 768 / 390（用户明确要求过这四档）。要覆盖更小的手机可加 360。

## 窄屏表格：用卡片模式，不要横向滚动

`table { display:block; overflow-x:auto; white-space:nowrap }` 是常见做法，
但用户看到的是"内容被切掉"，而 JS 报"没有页面级溢出"（因为溢出发生在表格的
滚动容器内部）。**这两者不矛盾，但体验很差。**

改法：窄屏把表格拆成纵向卡片，并用 `data-label` 还原表头语义。

```css
@media (max-width: 640px) {
  table, thead, tbody, th, td, tr { display: block; width: 100%; }
  thead { display: none; }
  tbody tr { border:1px solid var(--line); border-radius:10px;
             margin-bottom:10px; padding:6px 0; background:#fff; }
  td { border:none; padding:6px 13px; display:flex; gap:10px;
       align-items:flex-start; white-space:normal; word-break:break-word; }
  td + td { border-top:1px dashed #eef2f8; }
  td[data-label]:before {
    content: attr(data-label);
    flex:0 0 auto; min-width:70px;
    font-size:12px; font-weight:700; color:#7a8aa3;
  }
  code { word-break: break-all; font-size:12.5px; }
  .grid { grid-template-columns: 1fr; }   /* 别忘了解除多列网格 */
}
```

`<td>` 需要 `data-label="列名"`，否则卡片里看不出这一行是什么。
可以脚本化补齐：解析 `<thead>` 顺序，按列序给每个 `<td>` 打 label。

## 补 data-label 的合法脚本（正则 + 按行重置列索引）

```python
def process_table(m):
    table = m.group(0)
    th_m = re.search(r'<thead>(.*?)</thead>', table, re.S)
    if not th_m:
        return table
    headers = [strip_tags(x) for x in re.findall(r'<th[^>]*>(.*?)</th>', th_m.group(1), re.S)]
    body_m = re.search(r'<tbody>(.*?)</tbody>', table, re.S)
    if not headers or not body_m:
        return table
    body = body_m.group(1)

    def row_fn(rm):                       # 每行重置列索引
        row = rm.group(0); idx = [0]
        def rep(cm):
            attrs = cm.group(1); i = idx[0]; idx[0] += 1
            if 'data-label' in attrs or i >= len(headers):
                return cm.group(0)
            return f'<td data-label="{headers[i]}"{attrs}>'
        return re.sub(r'<td([^>]*)>', rep, row)

    new_body = re.sub(r'<tr>.*?</tr>', row_fn, body, flags=re.S)
    return table.replace(body, new_body, 1)

html = re.sub(r'<table>.*?</table>', process_table, html, flags=re.S)
```

验证：`data-label` 数量应等于 `<td>` 总数，字段分布里的列名要和 thead 对上。

## 改 CSS 时的结构守卫

用 `patch` 改 `@media` 块很容易吃掉 `}` 或 `</head>`，整段窄屏样式会静默失效。
每次改完必须跑结构检查：

```python
assert s.count("<style>") == 1 and s.count("</style>") == 1
assert s.count("<head>") == 1 and s.count("</head>") == 1
assert s.count("<body>") == 1 and s.count("</body>") == 1
css = re.search(r'<style>(.*?)</style>', s, re.S).group(1)
assert css.count("{") == css.count("}"), "CSS 括号不平衡"
assert s.count("<section>") == s.count("</section>")
assert s.count("<table>") == s.count("</table>")
```

## 视觉模型的判断要打折

截图交给 vision 检查时，它常把"首屏高度截断"（正常）报成"内容被裁切"（异常），
也可能把 510px 渲染报成溢出。**以 JS 探针的数字为准，截图只用来确认美观度。**
两者冲突时，先怀疑截图方法，再怀疑页面。
