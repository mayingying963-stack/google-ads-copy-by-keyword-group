#!/usr/bin/env python3
"""
validate_gads_copy.py — Google Ads 文案字符数与合规校验器

用途：
  校验按关键词分组生成的广告文案，逐条检查字符上限、数量要求、重复项、
  政策红线（违禁词/全大写/连续标点/电话邮箱），并报告每个字段距离上限的余量。

用法：
  python validate_gads_copy.py copy.json
  python validate_gads_copy.py copy.json --json     # 机器可读输出
  python validate_gads_copy.py --selftest           # 自检

输入 JSON 结构（每个关键词分组一个对象）：
{
  "brand": "HIITIO",
  "target_url_pattern": "https://www.hiitio.com/...",
  "groups": [
    {
      "group_name": "HVDC Contactor",
      "keywords": ["hvdc contactor", "high voltage dc contactor"],
      "headlines": ["...", "...", ...],
      "descriptions": ["...", ...],
      "paths": ["hvdc", "contactor"],
      "sitelinks": [
        {"text": "...", "line1": "...", "line2": "...", "final_url": "..."}
      ],
      "callouts": ["...", ...],
      "snippets": [
        {"header": "Types", "values": ["...", "...", "..."]}
      ]
    }
  ]
}

退出码：0 = 全部通过；1 = 有错误；2 = 有警告但无错误
"""

import json
import re
import sys
import argparse
from typing import Any

# ============================================================
# 字符上限（来源：Google for Developers Ads API 文档 + 后台校验）
# ============================================================
LIM = {
    "headline": 30,
    "description": 90,
    "path": 15,
    "sitelink_text": 25,
    "sitelink_line1": 35,
    "sitelink_line2": 35,
    "callout": 25,
    "snippet_value": 25,
}

# ============================================================
# 数量要求
# Google 后台硬限制：headline 最多 15，description 最多 4
# 用户常要 18 条标题 = 15 条上稿 + 3 条备用，本校验器支持 "target" 与 "uploadable" 双口径
# ============================================================
COUNT = {
    "headline_upload_max": 15,      # 后台硬上限
    "headline_upload_min": 3,       # 后台硬下限
    "headline_target": 18,          # 建议产出总数（15 上稿 + 3 备用）
    "description_upload_max": 4,
    "description_upload_min": 2,
    "description_target": 5,        # 4 上稿 + 1 备用
    "sitelink_target": 6,
    "callout_min": 4,               # Google 要求至少 4 条才会展示
    "callout_target": 5,
    "snippet_target": 2,
    "snippet_values_min": 3,        # 少于此值不渲染
    "snippet_values_max": 10,
}

# ============================================================
# 结构化摘要的可选标题（Google 固定清单，不可自创）
# 标注 * 的是适合工业/电池/电子器件类目的
# ============================================================
SNIPPET_HEADERS = {
    # 通用
    "Amenities", "Brands", "Courses", "Degree programs", "Destinations",
    "Featured hotels", "Insurance coverage", "Models", "Neighborhoods",
    "Service catalog", "Shows", "Styles", "Types",
    # 工业/电池/电子常用 *
    "Voltage", "Capacity", "Compatible With", "Features", "Service",
    "Types of homes", "Appliances", "Programs", "Health insurance",
    "Specialties", "Styles",
}

# 适合 B2B 新能源/电子器件的推荐标题
SNIPPET_HEADERS_B2B = [
    "Types", "Brands", "Models", "Features", "Compatible With",
    "Service catalog", "Voltage", "Capacity",
]

# ============================================================
# 政策红线词表
# ============================================================
# 1) 批发/零售口径冲突：B2B 批发投放禁提免邮（批发价已含运费）
FORBIDDEN_WHOLESALE = [
    r"free\s+shipping", r"free\s+freight", r"free\s+delivery",
    r"\bfree\s+postage\b", r"shipping\s+included",
    r"\b48\s+states?\b", r"contiguous\s+(us|united\s+states)",
]

# 2) 虚假陈述风险：无佐证的绝对化/排名/稀缺声明
FORBIDDEN_MISREP = [
    r"#\s*1\b", r"\bnumber\s+one\b", r"\bno\.\s*1\b",
    r"\bbest\s+in\s+the\s+world\b", r"\bworld'?s\s+best\b",
    r"\bcheapest\b", r"\bguaranteed\s+lowest\b",
    r"\bonly\s+\d+\s+left\b", r"\bhurry\b", r"\bact\s+now\b",
    r"\b100\s*%\s*guaranteed?\b",
    r"\binstant(ly)?\s+approv", r"\bno\s+credit\s+check\b",
]

# 3) 危险品红线：锂电池类目须避开危险品运输表述
FORBIDDEN_DANGER = [
    r"\bhazardous\b", r"\bexplosive\b", r"\bflammable\s+shipping\b",
    r"\bun\s*38\.?3\s*exempt\b",
]

# 4) 纯 CTA 占满（无实质信息）
FORBIDDEN_BARE_CTA = [
    r"^click\s+here$", r"^buy\s+now$", r"^learn\s+more$",
    r"^shop\s+now$", r"^sign\s+up$", r"^get\s+started$",
]

# 技术性拒绝
RE_MULTI_PUNCT = re.compile(r"[!?.,;:]{2,}|\.{3,}|-{2,}")
RE_PHONE = re.compile(r"(\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4})")
RE_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
# 装饰符号：只抓纯装饰性字符。& + , . ' / ( ) : - % ° $ 等正常商业标点必须放行
RE_DECOR = re.compile(r"[★☆✦✧❖➤►◆■●※~|\\<>^{}\[\]]")


def _err(group, field, msg, value=None):
    return {
        "level": "error",
        "group": group,
        "field": field,
        "message": msg,
        "value": value,
    }


def _warn(group, field, msg, value=None):
    return {
        "level": "warning",
        "group": group,
        "field": field,
        "message": msg,
        "value": value,
    }


def check_text_policies(group, field, text, *, wholesale_mode=True):
    """对所有文案字段做通用政策检查。"""
    issues = []
    low = text.lower()

    # 全大写（允许单个词如 USA、UL、CE、OEM、BMS 等缩略语）
    words = [w for w in re.findall(r"[A-Za-z]{3,}", text)]
    if words and all(w.isupper() for w in words) and len(words) > 1:
        issues.append(_err(group, field, "整条全大写（Google 会拒绝）", text))

    # 连续标点
    if RE_MULTI_PUNCT.search(text):
        issues.append(_err(group, field, "连续/重复标点", text))

    # 感叹号 >1
    if text.count("!") > 1:
        issues.append(_err(group, field, f"感叹号 {text.count('!')} 个（最多 1）", text))

    # 电话号码 / 邮箱（不能出现在广告文案里）
    if RE_PHONE.search(text):
        issues.append(_err(group, field, "含电话号码（应用 call 资产或落地页）", text))
    if RE_EMAIL.search(text):
        issues.append(_err(group, field, "含邮箱地址", text))

    # 装饰符号
    if RE_DECOR.search(text):
        issues.append(_err(group, field, "含装饰符号（★ @# 等）", text))

    # 首尾空格 / 双空格
    if text != text.strip() or "  " in text:
        issues.append(_warn(group, field, "首尾或连续空格", text))

    # 政策词表
    if wholesale_mode:
        for p in FORBIDDEN_WHOLESALE:
            if re.search(p, low):
                issues.append(
                    _err(group, field, "B2B 批发文案禁提免邮/免运费（改 'Freight quoted with your quote'）", text)
                )
                break
    for p in FORBIDDEN_MISREP:
        if re.search(p, low):
            issues.append(_err(group, field, "疑似虚假陈述/无佐证绝对化声明", text))
            break
    for p in FORBIDDEN_DANGER:
        if re.search(p, low):
            issues.append(_err(group, field, "疑似危险品表述（锂电类目红线）", text))
            break
    for p in FORBIDDEN_BARE_CTA:
        if re.search(p, low):
            issues.append(_err(group, field, "纯 CTA 无实质信息", text))
            break

    return issues


def check_length(group, field, text, limit):
    """长度检查，返回 (issues, usage_info)"""
    n = len(text)
    issues = []
    if n > limit:
        issues.append(_err(group, field, f"{n} 字符 > 上限 {limit}（超 {n - limit}）", text))
    return issues, {"field": field, "len": n, "limit": limit, "slack": limit - n}


def validate_group(g: dict, idx: int, wholesale_mode=True):
    """校验单个关键词分组。返回 (issues, stats)"""
    issues = []
    stats = {"usage": [], "group": g.get("group_name", f"group{idx}")}
    name = g.get("group_name") or f"group{idx}"

    # ---------- 关键词 ----------
    kws = g.get("keywords") or []
    if not kws:
        issues.append(_err(name, "keywords", "分组没有关键词"))

    # ---------- 标题 ----------
    hl = g.get("headlines") or []
    n_hl = len(hl)
    # 设计上的 18 条 = 15 上稿 + 3 备用。超过 15 不是错误，只要标明拆分方式即可。
    if n_hl > COUNT["headline_upload_max"]:
        stats["headline_split"] = (
            f"{COUNT['headline_upload_max']} 上稿 + {n_hl - COUNT['headline_upload_max']} 备用"
        )
    if n_hl < COUNT["headline_upload_min"]:
        issues.append(_err(name, "headlines", f"{n_hl} 条 < 最少 {COUNT['headline_upload_min']} 条"))
    if n_hl != COUNT["headline_target"]:
        issues.append(
            _warn(name, "headlines", f"标题 {n_hl} 条，建议 {COUNT['headline_target']} 条（15 上稿 + 3 备用）")
        )
    # 重复
    seen = {}
    for h in hl:
        k = h.strip().lower()
        if k in seen:
            issues.append(_err(name, "headlines", "标题重复（后台报 AssetError.DUPLICATE_ASSET）", h))
        seen[k] = 1
    for h in hl:
        i, u = check_length(name, "headline", h, LIM["headline"])
        issues += i
        stats["usage"].append(u)
        issues += check_text_policies(name, "headline", h, wholesale_mode=wholesale_mode)

    # ---------- 说明 ----------
    ds = g.get("descriptions") or []
    n_d = len(ds)
    # 设计上的 5 条 = 4 上稿 + 1 备用。超过 4 不是错误。
    if n_d > COUNT["description_upload_max"]:
        stats["description_split"] = (
            f"{COUNT['description_upload_max']} 上稿 + {n_d - COUNT['description_upload_max']} 备用"
        )
    if n_d < COUNT["description_upload_min"]:
        issues.append(_err(name, "descriptions", f"{n_d} 条 < 最少 {COUNT['description_upload_min']} 条"))
    seen_d = {}
    for d in ds:
        k = d.strip().lower()
        if k in seen_d:
            issues.append(_err(name, "descriptions", "说明重复", d))
        seen_d[k] = 1
    for d in ds:
        i, u = check_length(name, "description", d, LIM["description"])
        issues += i
        stats["usage"].append(u)
        issues += check_text_policies(name, "description", d, wholesale_mode=wholesale_mode)

    # ---------- 路径 ----------
    paths = g.get("paths") or []
    if len(paths) > 2:
        issues.append(_err(name, "paths", f"{len(paths)} 段路径 > 2 段"))
    if len(paths) == 1:
        issues.append(_warn(name, "paths", "只填了 path1（path2 可留空，但有 path2 必须同时有 path1）"))
    for i_p, p in enumerate(paths):
        i, u = check_length(name, f"path{i_p+1}", p, LIM["path"])
        issues += i
        stats["usage"].append(u)
        if re.search(r"\s", p):
            issues.append(_err(name, f"path{i_p+1}", "路径含空格（应用连字符）", p))
        if re.search(r"[^\w\-]", p):
            issues.append(_warn(name, f"path{i_p+1}", "路径含特殊字符，建议仅字母数字与连字符", p))

    # ---------- 站内链接 ----------
    sls = g.get("sitelinks") or []
    if len(sls) != COUNT["sitelink_target"]:
        issues.append(_warn(name, "sitelinks", f"站内链接 {len(sls)} 条，建议 {COUNT['sitelink_target']} 条"))
    seen_sl = {}
    for s in sls:
        t = s.get("text", "")
        d1 = s.get("line1", "")
        d2 = s.get("line2", "")
        i, u = check_length(name, "sitelink_text", t, LIM["sitelink_text"])
        issues += i
        stats["usage"].append(u)
        i, u = check_length(name, "sitelink_line1", d1, LIM["sitelink_line1"])
        issues += i
        stats["usage"].append(u)
        i, u = check_length(name, "sitelink_line2", d2, LIM["sitelink_line2"])
        issues += i
        stats["usage"].append(u)
        for lbl, v in (("sitelink_text", t), ("sitelink_line1", d1), ("sitelink_line2", d2)):
            issues += check_text_policies(name, lbl, v, wholesale_mode=wholesale_mode)
        k = t.strip().lower()
        if k in seen_sl:
            issues.append(_err(name, "sitelinks", "站内链接标题重复", t))
        seen_sl[k] = 1
        if not s.get("final_url"):
            issues.append(_warn(name, "sitelinks", "站内链接缺 final_url（导入前补齐）", t))

    # ---------- 宣传信息 ----------
    cos = g.get("callouts") or []
    if len(cos) < COUNT["callout_min"]:
        issues.append(
            _err(name, "callouts", f"{len(cos)} 条 < Google 最低展示要求 {COUNT['callout_min']} 条")
        )
    if len(cos) != COUNT["callout_target"]:
        issues.append(_warn(name, "callouts", f"宣传信息 {len(cos)} 条，建议 {COUNT['callout_target']} 条"))
    seen_co = {}
    for c in cos:
        i, u = check_length(name, "callout", c, LIM["callout"])
        issues += i
        stats["usage"].append(u)
        issues += check_text_policies(name, "callout", c, wholesale_mode=wholesale_mode)
        k = c.strip().lower()
        if k in seen_co:
            issues.append(_err(name, "callouts", "宣传信息重复", c))
        seen_co[k] = 1

    # ---------- 结构化摘要 ----------
    sns = g.get("snippets") or []
    if len(sns) != COUNT["snippet_target"]:
        issues.append(_warn(name, "snippets", f"结构化摘要 {len(sns)} 组，建议 {COUNT['snippet_target']} 组"))
    for sn in sns:
        header = sn.get("header", "")
        values = sn.get("values") or []
        if header not in SNIPPET_HEADERS:
            issues.append(
                _err(name, "snippets", f"结构化摘要标题 '{header}' 不在 Google 固定清单内（不可自创）", header)
            )
        if not (COUNT["snippet_values_min"] <= len(values) <= COUNT["snippet_values_max"]):
            issues.append(
                _err(
                    name, "snippets",
                    f"'{header}' 有 {len(values)} 个值，需 {COUNT['snippet_values_min']}–{COUNT['snippet_values_max']} 个（<3 不渲染）",
                )
            )
        for v in values:
            i, u = check_length(name, f"snippet:{header}", v, LIM["snippet_value"])
            issues += i
            stats["usage"].append(u)
            issues += check_text_policies(name, f"snippet:{header}", v, wholesale_mode=wholesale_mode)

    return issues, stats


def validate(payload: dict, wholesale_mode=True):
    all_issues = []
    all_stats = []
    groups = payload.get("groups") or []
    if not groups:
        all_issues.append(_err("-", "groups", "没有任何关键词分组"))
        return all_issues, all_stats

    for i, g in enumerate(groups):
        iss, st = validate_group(g, i, wholesale_mode=wholesale_mode)
        all_issues += iss
        all_stats.append(st)

    # 跨分组重复标题（不同分组用完全相同标题会稀释相关性）
    all_hl = {}
    for g in groups:
        for h in g.get("headlines") or []:
            all_hl.setdefault(h.strip().lower(), []).append(g.get("group_name"))
    for h, gs in all_hl.items():
        if len(gs) > 2:
            all_issues.append(
                _warn("-", "headlines", f"标题被 {len(gs)} 个分组重复使用（建议每组独立对准关键词）", h)
            )

    return all_issues, all_stats


def print_report(issues, stats, payload):
    brands = payload.get("brand", "-")
    print("=" * 70)
    print(f"Google Ads 文案校验报告 — {brands}")
    print("=" * 70)

    errors = [i for i in issues if i["level"] == "error"]
    warnings = [i for i in issues if i["level"] == "warning"]

    # 按分组打印
    for st in stats:
        name = st["group"]
        giss = [i for i in issues if i["group"] == name]
        ge = [i for i in giss if i["level"] == "error"]
        gw = [i for i in giss if i["level"] == "warning"]
        mark = "FAIL" if ge else ("WARN" if gw else "PASS")
        print(f"\n[{mark}] {name}")
        for i in ge:
            print(f"   ERROR  {i['field']:22} {i['message']}")
            if i.get("value"):
                print(f"          → {i['value']!r}")
        for i in gw:
            print(f"   WARN   {i['field']:22} {i['message']}")

        # 余量统计：显示最接近上限的字段
        usage = st["usage"]
        if usage:
            tight = sorted(usage, key=lambda u: u["slack"])[:3]
            print("   最贴上限的字段（余量越小越危险）：")
            for u in tight:
                flag = " !" if u["slack"] == 0 else ""
                print(f"     {u['field']:22} {u['len']:>3}/{u['limit']}  余 {u['slack']:>2}{flag}")
        if st.get("headline_split"):
            print(f"   标题拆分：{st['headline_split']}")
        if st.get("description_split"):
            print(f"   说明拆分：{st['description_split']}")

    # 全局问题
    glob = [i for i in issues if i["group"] == "-"]
    if glob:
        print("\n[全局]")
        for i in glob:
            print(f"   {i['level'].upper():6} {i['field']:22} {i['message']}")

    print("\n" + "=" * 70)
    print(f"总计：{len(errors)} 个错误，{len(warnings)} 个警告，{len(stats)} 个分组")
    if errors:
        print("结论：不通过 — 修完错误项再上稿")
    elif warnings:
        print("结论：通过（有警告，建议处理）")
    else:
        print("结论：全部通过")
    print("=" * 70)


def selftest():
    """自检：确保校验器能正确抓出越界与违禁。"""
    print("运行自检…\n")
    good = {
        "brand": "TEST",
        "groups": [
            {
                "group_name": "GoodGroup",
                "keywords": ["test keyword"],
                "headlines": [
                    "48V 105Ah LiFePO4 Battery", "Golf Cart Battery Packs",
                    "Made in the USA", "Wholesale & Dealer Pricing",
                    "UL1973 & UN38.3 Tested", "No Ocean Freight Required",
                    "No Import Tariffs", "Ships in 5-7 Business Days",
                    "Custom BMS & Enclosures", "Low MOQ for Dealers",
                    "5,000+ Charge Cycles", "US-Based Technical Support",
                    "Forklift & Golf Cart OEM", "BlitzNXT",
                    "Request a Wholesale Quote", "Grade-A LFP Cells",
                    "Own BMS Firmware", "IP67 Sealed Pack",
                ],
                "descriptions": [
                    "48V 105Ah LiFePO4 packs for golf carts, forklifts and floor machines.",
                    "US-manufactured cells. No ocean freight, no tariffs, no container wait.",
                    "Wholesale and dealer pricing for B2B buyers. Custom BMS available.",
                    "UL1973 and UN38.3 tested. US-based support. Request your quote today.",
                    "Grade-A LFP cells with our own BMS firmware. Freight quoted with your quote.",
                ],
                "paths": ["lifepo4", "48v-105ah"],
                "sitelinks": [
                    {"text": "Technical Datasheets", "line1": "Full specs and test reports",
                     "line2": "Download before you buy", "final_url": "/datasheets"},
                    {"text": "Wholesale Pricing", "line1": "Dealer and volume tiers",
                     "line2": "Quote within one business day", "final_url": "/wholesale"},
                    {"text": "BMS Customization", "line1": "Firmware tailored to your pack",
                     "line2": "Engineering support included", "final_url": "/bms"},
                    {"text": "Certifications", "line1": "UL1973 and UN38.3 reports",
                     "line2": "Documents on request", "final_url": "/certs"},
                    {"text": "About BlitzNXT", "line1": "US-based manufacturing",
                     "line2": "Battery packs built in-house", "final_url": "/about"},
                    {"text": "Contact Engineering", "line1": "Talk to a battery engineer",
                     "line2": "Bulk and OEM inquiries", "final_url": "/contact"},
                ],
                "callouts": [
                    "US Manufacturing", "Grade-A LFP Cells",
                    "Custom BMS Firmware", "UL1973 Tested",
                    "Bulk Pricing Available", "Engineering Support",
                ],
                "snippets": [
                    {"header": "Types", "values": ["LiFePO4", "Golf Cart", "Forklift", "Floor Machine"]},
                    {"header": "Features", "values": ["IP67 Rated", "Custom BMS", "5,000 Cycles"]},
                ],
            }
        ],
    }
    iss, st = validate(good)
    errs = [i for i in iss if i["level"] == "error"]
    print(f"良构样本 → 错误 {len(errs)}，警告 {len(iss) - len(errs)}")
    for e in errs:
        print(f"   意外错误: {e['field']} {e['message']} {e.get('value')}")
    ok1 = len(errs) == 0

    # 坏样本：超长、违禁、重复、全大写
    bad = json.loads(json.dumps(good))
    gb = bad["groups"][0]
    gb["headlines"][0] = "This headline is definitely way too long for Google Ads"
    gb["headlines"][1] = "FREE SHIPPING ON ALL ORDERS"
    gb["headlines"][2] = "Request a Wholesale Quote"      # 与 [14] 重复
    gb["descriptions"][0] = "#1 best battery supplier in the world, guaranteed!!"
    gb["callouts"][0] = "Call us at (555) 123-4567"
    gb["sitelinks"][0]["line1"] = "This sitelink line one is far too long to fit"
    gb["snippets"][0]["header"] = "Our Unique Header"     # 不在清单
    gb["snippets"][1]["values"] = ["Only One"]            # <3 值
    gb["headlines"].append("Nineteenth headline")         # 19 条 > 15

    iss2, st2 = validate(bad)
    errs2 = [i for i in iss2 if i["level"] == "error"]
    print(f"\n坏构样本 → 抓到 {len(errs2)} 个错误")
    for e in errs2:
        print(f"   {e['field']:22} {e['message']}")
    # 期望至少抓到: 超长标题 / 免邮 / 全大写 / 重复 / 虚假陈述 / 电话 /
    #              站内链接超长 / 非法摘要标题 / 摘要值不足 / 说明5条超4 等
    ok2 = len(errs2) >= 8

    print("\n" + "=" * 50)
    print(f"良构样本无误报: {'OK' if ok1 else 'FAIL'}")
    print(f"坏构样本全命中: {'OK' if ok2 else 'FAIL'}")
    print("=" * 50)
    return 0 if (ok1 and ok2) else 1


def main():
    ap = argparse.ArgumentParser(description="Google Ads 文案校验器")
    ap.add_argument("input", nargs="?", help="文案 JSON 文件路径")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--selftest", action="store_true", help="运行自检")
    ap.add_argument(
        "--retail", action="store_true",
        help="零售模式：允许 'free shipping' 等表述（默认 B2B 批发模式禁止）",
    )
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())

    if not args.input:
        ap.print_help()
        sys.exit(2)

    with open(args.input, encoding="utf-8") as f:
        payload = json.load(f)

    wholesale_mode = not args.retail
    issues, stats = validate(payload, wholesale_mode=wholesale_mode)

    if args.json:
        print(json.dumps({"issues": issues, "stats": stats}, ensure_ascii=False, indent=2))
    else:
        print_report(issues, stats, payload)

    errors = [i for i in issues if i["level"] == "error"]
    warnings = [i for i in issues if i["level"] == "warning"]
    if errors:
        sys.exit(1)
    if warnings:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
