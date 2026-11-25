#!/usr/bin/env python3
"""
export_gads_copy.py — 把校验通过的文案 JSON 导出为 Google Ads Editor 可导入的 CSV + 审阅用 Excel/HTML

用法：
  python export_gads_copy.py copy.json                 # 导出 CSV + HTML 审阅页
  python export_gads_copy.py copy.json --xlsx          # 额外导出 Excel（需 openpyxl）
  python export_gads_copy.py copy.json --outdir dist

产出：
  <brand>_rsa.csv        RSA 广告（标题/说明/路径），可直接 Editor 导入
  <brand>_assets.csv     站内链接 / 宣传信息 / 结构化摘要
  <brand>_review.html    明亮配色审阅页，逐组对照关键词与文案，标注字符数
  <brand>_copy.md        纯文本版，便于贴进工单或邮件

注意：CSV 默认 Status=Paused，导入后人工审核再启用，避免头部词一周内吃掉预算。
"""

import csv
import json
import os
import sys
import argparse
from html import escape

LIM = {"headline": 30, "description": 90, "sitelink_text": 25,
       "sitelink_line1": 35, "sitelink_line2": 35, "callout": 25, "snippet_value": 25}
UPLOAD_MAX_HL = 15
UPLOAD_MAX_DESC = 4


def rsa_rows(payload):
    """RSA 广告行：每个分组一行，Headline 1..15 + Description 1..4（只用上稿部分）"""
    rows = []
    for g in payload["groups"]:
        hl = (g.get("headlines") or [])[:UPLOAD_MAX_HL]
        ds = (g.get("descriptions") or [])[:UPLOAD_MAX_DESC]
        paths = g.get("paths") or []
        row = {
            "Campaign": payload.get("campaign", payload.get("brand", "Campaign")),
            "Ad Group": g["group_name"],
            "Ad Type": "Responsive search ad",
            "Final URL": g.get("final_url", payload.get("site", "")),
            "Path 1": paths[0] if len(paths) > 0 else "",
            "Path 2": paths[1] if len(paths) > 1 else "",
            "Status": "Paused",
        }
        for i in range(UPLOAD_MAX_HL):
            row[f"Headline {i+1}"] = hl[i] if i < len(hl) else ""
        for i in range(UPLOAD_MAX_DESC):
            row[f"Description {i+1}"] = ds[i] if i < len(ds) else ""
        rows.append(row)
    return rows


def asset_rows(payload):
    """素材资产：站内链接 / 宣传信息 / 结构化摘要，每行一条"""
    rows = []
    for g in payload["groups"]:
        ag = g["group_name"]
        for s in g.get("sitelinks") or []:
            rows.append({
                "Campaign": payload.get("campaign", payload.get("brand", "Campaign")),
                "Ad Group": ag, "Asset Type": "Sitelink",
                "Text": s.get("text", ""),
                "Line 1": s.get("line1", ""),
                "Line 2": s.get("line2", ""),
                "Final URL": s.get("final_url", ""),
                "Status": "Paused",
            })
        for c in g.get("callouts") or []:
            rows.append({
                "Campaign": payload.get("campaign", payload.get("brand", "Campaign")),
                "Ad Group": ag, "Asset Type": "Callout",
                "Text": c, "Line 1": "", "Line 2": "", "Final URL": "", "Status": "Paused",
            })
        for sn in g.get("snippets") or []:
            rows.append({
                "Campaign": payload.get("campaign", payload.get("brand", "Campaign")),
                "Ad Group": ag, "Asset Type": "Structured Snippet",
                "Text": sn.get("header", ""),
                "Line 1": " | ".join(sn.get("values") or []),
                "Line 2": "", "Final URL": "", "Status": "Paused",
            })
    return rows


def write_csv(rows, path):
    if not rows:
        return
    keys = list(rows[0].keys())
    # UTF-8 BOM，Excel 双击不乱码
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def build_review_html(payload):
    brand = payload.get("brand", "Ad Copy")
    aud = payload.get("target_audience", "")

    def chip(n, lim):
        cls = "ok" if n <= lim else "over"
        return f'<span class="chip {cls}">{n}/{lim}</span>'

    parts = []
    for g in payload["groups"]:
        hl = g.get("headlines") or []
        ds = g.get("descriptions") or []
        paths = g.get("paths") or []
        kws = g.get("keywords") or []

        kw_html = "".join(f'<span class="kw">{escape(k)}</span>' for k in kws)

        hl_rows = []
        for i, h in enumerate(hl):
            kinds = []
            if i < 5:
                kinds.append("供应实力")
            elif 5 <= i < 10:
                kinds.append("CTA")
            if i >= UPLOAD_MAX_HL:
                kinds.append("备用")
            tag = "".join(f'<em class="tag">{k}</em>' for k in kinds)
            hl_rows.append(
                f'<tr><td class="idx">{i+1}</td><td><code>{escape(h)}</code></td>'
                f'<td>{chip(len(h), LIM["headline"])}</td><td class="tagcell">{tag}</td></tr>'
            )
        ds_rows = []
        for i, d in enumerate(ds):
            extra = '<em class="tag">备用</em>' if i >= UPLOAD_MAX_DESC else ""
            ds_rows.append(
                f'<tr><td class="idx">{i+1}</td><td>{escape(d)}</td>'
                f'<td>{chip(len(d), LIM["description"])}</td><td class="tagcell">{extra}</td></tr>'
            )
        sl_rows = []
        for s in g.get("sitelinks") or []:
            t, d1, d2 = s.get("text", ""), s.get("line1", ""), s.get("line2", "")
            sl_rows.append(
                f'<tr><td>{escape(t)} {chip(len(t), LIM["sitelink_text"])}</td>'
                f'<td>{escape(d1)} {chip(len(d1), LIM["sitelink_line1"])}</td>'
                f'<td>{escape(d2)} {chip(len(d2), LIM["sitelink_line2"])}</td></tr>'
            )
        co_html = "".join(
            f'<span class="callout">{escape(c)} {chip(len(c), LIM["callout"])}</span>'
            for c in g.get("callouts") or []
        )
        sn_html = ""
        for sn in g.get("snippets") or []:
            vals = "".join(
                f'<span class="snip">{escape(v)} {chip(len(v), LIM["snippet_value"])}</span>'
                for v in sn.get("values") or []
            )
            sn_html += f'<div class="snipgroup"><b>{escape(sn.get("header",""))}</b>{vals}</div>'

        part = f"""
        <section class="group">
          <h2>{escape(g['group_name'])}</h2>
          <div class="kws">{kw_html}</div>
          {f'<p class="path">Path: <code>{escape("/".join(paths))}</code></p>' if paths else ''}

          <h3>标题（{len(hl)} 条 · 上稿 {min(len(hl), UPLOAD_MAX_HL)} · 备用 {max(0, len(hl)-UPLOAD_MAX_HL)}）</h3>
          <table><thead><tr><th>#</th><th>文案</th><th>字符</th><th>类型</th></tr></thead>
          <tbody>{''.join(hl_rows)}</tbody></table>

          <h3>说明（{len(ds)} 条）</h3>
          <table><thead><tr><th>#</th><th>文案</th><th>字符</th><th>类型</th></tr></thead>
          <tbody>{''.join(ds_rows)}</tbody></table>

          <h3>站内链接（{len(g.get('sitelinks') or [])} 条）</h3>
          <table><thead><tr><th>标题 ≤25</th><th>说明行1 ≤35</th><th>说明行2 ≤35</th></tr></thead>
          <tbody>{''.join(sl_rows)}</tbody></table>

          <h3>宣传信息（{len(g.get('callouts') or [])} 条 · ≤25）</h3>
          <div class="wrapchips">{co_html}</div>

          <h3>结构化摘要（{len(g.get('snippets') or [])} 组）</h3>
          {sn_html}
        </section>
        """
        parts.append(part)

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(brand)} · 广告文案审阅</title>
<style>
:root{{--bg:#f7f9fc;--card:#fff;--ink:#101828;--muted:#5b6b84;--line:#e3e9f2;
--blue:#1558d6;--green:#0e7a52;--red:#c02626}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);line-height:1.65;
font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;font-size:15px}}
.wrap{{max-width:1080px;margin:0 auto;padding:36px 22px 70px}}
header{{background:linear-gradient(135deg,#1558d6,#0b3ea8);color:#fff;
border-radius:14px;padding:28px 30px;margin-bottom:22px}}
header h1{{margin:0 0 8px;font-size:24px}}
header .sub{{opacity:.9;font-size:13.5px}}
section.group{{background:var(--card);border:1px solid var(--line);border-radius:13px;
padding:22px 26px;margin-bottom:20px}}
h2{{font-size:19px;margin:0 0 12px;padding-bottom:10px;border-bottom:2px solid var(--line);color:var(--blue)}}
h3{{font-size:14.5px;margin:20px 0 8px;color:#243b63}}
table{{width:100%;border-collapse:collapse;font-size:13.5px;margin:8px 0}}
th{{background:#f2f6fd;text-align:left;padding:8px 10px;border-bottom:2px solid var(--line);font-weight:600}}
td{{padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
td.idx{{color:var(--muted);width:34px}}
code{{background:#f0f4fb;border:1px solid #e0e8f5;border-radius:4px;padding:1px 5px;
font-family:Consolas,monospace;font-size:12.5px}}
.chip{{display:inline-block;font-size:11.5px;font-weight:700;padding:1px 7px;border-radius:99px;white-space:nowrap}}
.chip.ok{{background:#e6f7ef;color:var(--green)}}
.chip.over{{background:#fdeaea;color:var(--red)}}
.kw{{display:inline-block;background:#eaf1ff;color:#12408f;border:1px solid #cddcf8;
border-radius:99px;padding:2px 10px;font-size:12.5px;margin:0 6px 6px 0}}
.callout{{display:inline-block;background:#f3f6fb;border:1px solid var(--line);
border-radius:8px;padding:6px 11px;margin:0 8px 8px 0;font-size:13px}}
.snip{{display:inline-block;background:#f8fafd;border:1px dashed #cddcf8;
border-radius:7px;padding:4px 9px;margin:0 6px 6px 0;font-size:12.5px}}
.snipgroup{{margin-bottom:10px}}
.snipgroup b{{display:block;margin-bottom:6px;color:#243b63;font-size:13.5px}}
.tag{{display:inline-block;background:#fff4e0;color:#a55a00;border-radius:99px;
padding:1px 8px;font-size:11px;font-style:normal;margin-right:4px}}
.path{{color:var(--muted);font-size:13px;margin:4px 0 0}}
.wrapchips{{margin:8px 0}}
@media(max-width:640px){{
 .wrap{{padding:18px 12px 44px}}
 header{{padding:20px 18px}}
 header h1{{font-size:19px}}
 section.group{{padding:16px 14px}}
 table,thead,tbody,tr,td,th{{display:block;width:100%}}
 thead{{display:none}}
 tr{{border:1px solid var(--line);border-radius:9px;margin-bottom:9px;padding:5px 0;background:#fff}}
 td{{border:none;padding:5px 12px;white-space:normal;word-break:break-word}}
 td+td{{border-top:1px dashed #eef2f8}}
 td.idx{{display:inline-block;width:auto;color:var(--muted);font-weight:700}}
}}
</style></head><body><div class="wrap">
<header><h1>{escape(brand)} · Google Ads 文案审阅</h1>
<div class="sub">{escape(aud)}<br>共 {len(payload['groups'])} 个关键词分组 ·
字符数已逐条校验（绿=合规 / 红=超限）</div></header>
{''.join(parts)}
</div></body></html>"""


def build_markdown(payload):
    out = [f"# {payload.get('brand','')} — Google Ads 文案\n"]
    if payload.get("target_audience"):
        out.append(f"**目标人群**：{payload['target_audience']}\n")
    for g in payload["groups"]:
        out.append(f"\n## {g['group_name']}\n")
        out.append("**关键词**：" + ", ".join(g.get("keywords") or []) + "\n")
        out.append("\n### 标题\n")
        for i, h in enumerate(g.get("headlines") or []):
            tag = "（备用）" if i >= UPLOAD_MAX_HL else ""
            out.append(f"{i+1}. [{len(h)}/30] {h}{tag}\n")
        out.append("\n### 说明\n")
        for i, d in enumerate(g.get("descriptions") or []):
            tag = "（备用）" if i >= UPLOAD_MAX_DESC else ""
            out.append(f"{i+1}. [{len(d)}/90] {d}{tag}\n")
        if g.get("paths"):
            out.append(f"\n### 路径\n`/{'/'.join(g['paths'])}`\n")
        out.append("\n### 站内链接\n")
        for s in g.get("sitelinks") or []:
            out.append(
                f"- **{s.get('text','')}** [{len(s.get('text',''))}/25]  \n"
                f"  {s.get('line1','')} [{len(s.get('line1',''))}/35]  \n"
                f"  {s.get('line2','')} [{len(s.get('line2',''))}/35]\n"
            )
        out.append("\n### 宣传信息\n")
        for c in g.get("callouts") or []:
            out.append(f"- {c} [{len(c)}/25]\n")
        out.append("\n### 结构化摘要\n")
        for sn in g.get("snippets") or []:
            out.append(f"- **{sn.get('header','')}**：" + " | ".join(sn.get("values") or []) + "\n")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser(description="导出 Google Ads 文案为 CSV / HTML / MD / XLSX")
    ap.add_argument("input")
    ap.add_argument("--outdir", default="dist")
    ap.add_argument("--xlsx", action="store_true")
    args = ap.parse_args()

    payload = json.load(open(args.input, encoding="utf-8"))
    os.makedirs(args.outdir, exist_ok=True)
    brand = (payload.get("brand") or "brand").replace(" ", "_")

    rp = os.path.join(args.outdir, f"{brand}_rsa.csv")
    ap_ = os.path.join(args.outdir, f"{brand}_assets.csv")
    write_csv(rsa_rows(payload), rp)
    write_csv(asset_rows(payload), ap_)
    print(f"CSV  : {rp}")
    print(f"CSV  : {ap_}")

    hp = os.path.join(args.outdir, f"{brand}_review.html")
    open(hp, "w", encoding="utf-8").write(build_review_html(payload))
    print(f"HTML : {hp}")

    mp = os.path.join(args.outdir, f"{brand}_copy.md")
    open(mp, "w", encoding="utf-8").write(build_markdown(payload))
    print(f"MD   : {mp}")

    if args.xlsx:
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
            wb = Workbook()
            ws = wb.active
            ws.title = "RSA"
            rras = rsa_rows(payload)
            if rras:
                ws.append(list(rras[0].keys()))
                for r in rras:
                    ws.append(list(r.values()))
                for c in ws[1]:
                    c.font = Font(bold=True)
                    c.fill = PatternFill("solid", fgColor="EAF1FF")
                ws.freeze_panes = "A2"
            ws2 = wb.create_sheet("Assets")
            aras = asset_rows(payload)
            if aras:
                ws2.append(list(aras[0].keys()))
                for r in aras:
                    ws2.append(list(r.values()))
                for c in ws2[1]:
                    c.font = Font(bold=True)
                    c.fill = PatternFill("solid", fgColor="EAF1FF")
                ws2.freeze_panes = "A2"
            xp = os.path.join(args.outdir, f"{brand}_copy.xlsx")
            wb.save(xp)
            print(f"XLSX : {xp}")
        except ImportError:
            print("跳过 XLSX：未安装 openpyxl（pip install openpyxl）")


if __name__ == "__main__":
    main()
