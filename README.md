# Google Ads Copy Generator — 按关键词分组生成广告文案

一个 **Hermes Agent / Claude Skill**，把关键词清单 + 目标人群变成可直接上稿的
Google Ads 搜索广告文案，**所有字符数由脚本硬校验，不靠肉眼**。

## 为什么需要它

写 Google Ads 文案的痛点不是"想不出词"，而是：

- 18 条标题写完全部 31 字符，一条都过不了
- 站内链接说明行按 90 字符写，实际上限是 **35**
- 结构化摘要自创标题，后台直接报错
- 文案写得漂亮，但一句没对准关键词，质量得分上不去
- 批发业务写了 `Free Shipping`，采购开始质疑单价

这个 skill 把这些全部变成**可执行的检查**。

## 产出规格

| 资产 | 数量 | 字符上限 |
|---|---|---|
| 标题 Headline | **18 条**（15 上稿 + 3 备用） | ≤30 |
| 说明 Description | **5 条**（4 上稿 + 1 备用） | ≤90 |
| 站内链接 Sitelink | **6 条** | 标题 ≤25 / 说明行 ≤35 / ≤35 |
| 宣传信息 Callout | **5 条** | ≤25 |
| 结构化摘要 Snippet | **2 组** | 每值 ≤25 |

其中 **5 条标题讲供应实力、5 条是 CTA**，其余为产品规格与备用。

> ⚠️ Google 后台 RSA 最多接受 **15 条标题、4 条说明**。18 条标题的标准拆法是
> 前 15 条上稿、后 3 条进 A/B 轮换池。导出脚本已自动处理，不会让你撞上限。

## 快速开始

```bash
# 1. 校验文案（字符数 + 政策红线）
python scripts/validate_gads_copy.py examples/hiitio-example.json

# 2. 导出可导入的文件
python scripts/export_gads_copy.py examples/hiitio-example.json --xlsx
```

产出：
- `HIITIO_rsa.csv` — Google Ads Editor 直接导入（**默认 Paused**）
- `HIITIO_assets.csv` — 站内链接 / 宣传信息 / 结构化摘要
- `HIITIO_review.html` — 明亮配色审阅页，逐条标字符数（绿=合规 / 红=超限）
- `HIITIO_copy.md` — 纯文本版
- `HIITIO_copy.xlsx` — 需 `pip install openpyxl`

## 校验器实测覆盖

`python scripts/test_coverage.py` → **24/24 通过**

```
[PASS] 合规基线        [PASS] 标题超30        [PASS] 说明超90
[PASS] 标题重复        [PASS] 全大写拒绝       [PASS] 全大写品牌不误判
[PASS] 型号不误判      [PASS] 短语含全大写词不误判 [PASS] 免邮违禁
[PASS] 虚假陈述#1      [PASS] 危险品词        [PASS] 电话号
[PASS] 邮箱           [PASS] 装饰符号        [PASS] 连续标点
[PASS] 纯CTA          [PASS] 站内链接行超35    [PASS] 宣传信息<4条
[PASS] 摘要标题非法     [PASS] 摘要值<3        [PASS] 路径超15
[PASS] 路径含空格       [PASS] 通用性:虚构品牌异行业 [PASS] 零售模式放行免邮
```

其中两项最能说明设计取舍：

- **`通用性:虚构品牌异行业`** — 换一个完全虚构的品牌（`ACME-ESPRESSO`）和完全不同的行业（咖啡设备）
  跑同一套校验，必须照样通过。证明本 skill 不绑定任何具体站点或行业。
- **`全大写品牌不误判`** — `ACME-ESPRESSO`、`HVC-1000` 这类带连字符的全大写品牌/型号必须放行；
  但 `FACTORY DIRECT SUPPLIER` 这种多词全大写仍要拒绝。

## 文件结构

```
SKILL.md                          技能主体（工作流 + 槽位分配 + 验证清单）
references/
  character-limits.md             字符上限与官方出处
  copy-formulas.md                各槽位文案公式与句式库
  b2b-vs-retail-voice.md          B2B 与零售语气差异
  policy-red-lines.md             政策红线完整清单
  snippet-headers.md              结构化摘要固定标题清单
  google-official-docs-retrieval.md   受限网络下取官方原文的取证顺序
  html-responsive-verification.md     HTML 多断点验证（含 Edge headless 视口陷阱）
scripts/
  validate_gads_copy.py           字符数 + 政策校验器（--selftest 自检）
  export_gads_copy.py             导出 CSV / HTML / MD / XLSX
  check_render.py                 HTML 多断点渲染检查（1440/768/390）
  test_coverage.py                校验器能力回归测试
examples/
  hiitio-example.json             完整双分组示例，可直接跑
```

## 数据来源

字符上限取自 **Google for Developers · Google Ads API 官方文档**：

> 「广告标题：至少 3 个、最多 15 个不重复对象（每个最多 30 个半形字元）」
> 「说明：至少 2 个、最多 4 个不重复对象（每个最多 90 个半形字元）」
> 「路径：`path1` / `path2` 每个最多 15 个半形字元」

站内链接 25/35/35、宣传信息 25、结构化摘要值 25 来自 Google Ads 后台实时校验
（政策帮助页在部分网络环境不可达）。

**已淘汰**：加大型文字广告 ETA 已于 2022 年 6 月全量停用，现在搜索广告只有 RSA。
任何"ETA 3 标题 + 2 描述"的教程都是过期资料。

## 作为 Skill 安装

**Hermes Agent**：把整个目录放进 `~/.hermes/skills/advertising/google-ads-copy-by-keyword-group/`

**Claude Code / 其他支持 SKILL.md 的框架**：放进对应的 skills 目录即可，
frontmatter 已是标准 `name` + `description` 格式。

## 依赖

- Python 3.8+（脚本仅用标准库）
- 可选：`openpyxl`（导出 Excel）、`playwright`（多断点渲染检查）

## License

MIT
