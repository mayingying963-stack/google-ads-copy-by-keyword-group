---
name: google-ads-copy-by-keyword-group
description: "Generate Google Ads search-ad copy organised by keyword group: 18 headlines (≤30 chars, 5 supply-strength + 5 CTA), 5 descriptions (≤90), 6 sitelinks (25/35/35), 5 callouts (≤25), 2 structured snippets, all hard-validated against Google's character limits and policy red lines before delivery. Use when the user says 广告文案 / 生成广告文案 / Google Ads copy / RSA copy / 搜索广告文案 / ad copy for these keywords, or supplies keywords plus a target audience and wants ready-to-upload ad copy. Outputs CSV for Google Ads Editor, an Excel workbook and a bright HTML review page. Handles B2B vs retail voice, Chinese-brand English copy, and the 18-headlines-but-15-upload-slot split."
tags:
  - advertising
  - google-ads
  - ad-copy
  - rsa
  - b2b
  - keyword-groups
  - character-limits
---

# Google Ads 文案生成（按关键词分组）

把一个关键词清单 + 目标人群，变成可直接上稿的 Google Ads 搜索广告文案。
**所有字符数在交付前必须由脚本硬校验，不靠肉眼。**

## 何时使用

触发词：`广告文案`、`生成广告文案`、`Google Ads copy`、`RSA copy`、`搜索广告文案`、
`ad copy for these keywords`、`write ad copy`，或用户给了关键词 + 目标人群要文案。

不适用：只要关键词研究（用 keyword 类 skill）、只要落地页（用 landing-page 类 skill）、
Performance Max 素材组（资产类型不同）。

## 硬性规格（本 skill 的产出标准）

| 资产 | 数量 | 字符上限 | 特殊要求 |
|---|---|---|---|
| 标题 Headline | **18 条** | **≤30** | 其中 **5 条讲供应实力**、**5 条是 CTA** |
| 说明 Description | **5 条** | **≤90** | 每条独立成立，不依赖顺序 |
| 站内链接 Sitelink | **6 条** | 标题 ≤25 / 说明行1 ≤35 / 说明行2 ≤35 | 三行都要填 |
| 宣传信息 Callout | **5 条** | **≤25** | — |
| 结构化摘要 Snippet | **2 组** | 每个值 **≤25** | 标题必须用 Google 固定清单内的词，每组 ≥3 个值 |

**字符计数**：按英文字符（含空格、标点）直接数。中文按全角算 2。我们产英文文案，`len()` 即结果。

### ⚠️ 18 条标题与 Google 后台上限的冲突（必须理解）

Google 后台 RSA **最多只接受 15 条标题、4 条说明**。所以 18 条标题的标准拆法是：

```
标题 1–15  → 上稿（填进 Google Ads 后台）
标题 16–18 → 备用（A/B 轮换池：跑 2–3 周后按 CTR 替换表现差的）
说明 1–4   → 上稿
说明 5     → 备用
```

**不要把 18 条全部塞进导入文件**——第 16–18 条会被后台拒绝。导出脚本已自动只取前 15/前 4，
并在审阅页把 16–18 标成 `备用` 标签。交付时明确告诉用户这个拆分。

## 工作流程

### 第 1 步：确认输入（缺什么问什么，别猜）

必需：
1. **关键词清单**（按语义分好组，或让本 skill 分组）
2. **目标人群**（B2B 采购 / 工程师 / 经销商 / 终端消费者 —— 决定语气）
3. **产品/服务**和**站点 URL**（用于 paths、sitelink 落地页、最终 URL）
4. **品牌名**（至少 1 条标题放品牌名，建议钉在 HEADLINE_1）

可选但强烈建议：现有认证（UL/CE/UN38.3 等）、起订量、交期、自有优势（工厂直供/OEM/美国制造）。
**只写用户确认过的事实**——没给的认证、客户数、年限一律不许编。

### 第 2 步：关键词分组

按**搜索意图 + 落地页可承接内容**分组，不是按字面相似：

- 一个分组 = 一个广告组 = 一个落地页能完整兑现的承诺
- 每组 3–10 个关键词
- 不同意图不混组（"buy 48v battery" 和 "lifepo4 vs lead acid" 不是一组）
- 大词和长尾词分开，否则大词吃光预算

### 第 3 步：18 条标题的槽位分配（这是本 skill 的核心）

**不要写 18 个形容词变体。18 条 = 18 个不同的购买理由。**

| 槽位 | 数量 | 作用 | 必须包含 |
|---|---|---|---|
| 1–5 | **5 条** | **供应实力** | 工厂直供 / OEM·ODM / 认证 / 起订量 / 年限或产能 |
| 6–10 | **5 条** | **CTA** | 带动作动词的明确指令 |
| 11–15 | 5 条 | 产品与规格 | 型号、参数、应用场景、兼容性、技术差异 |
| 16–18 | 3 条 | **备用** | 补充角度或备选措辞，供 A/B 轮换 |

**5 条供应实力的写法**（B2B 的核心，采购看的第一个东西）：
```
Factory Direct, No Middleman        OEM & ODM Available
UL & CE Certified                   Samples Before You Order
15 Years of Supply                  Low MOQ for Distributors
Bulk Pricing for Wholesalers        Custom Specs Accepted
```

**5 条 CTA 的写法**（要有动作，不能只写 "Click Here"）：
```
Request a Quote Today               Get Datasheets Instantly
Talk to Our Engineers               Send Your Spec for Pricing
Compare Models and Ratings          Download the Spec Sheet
```
> ❌ `Click Here` / `Buy Now` / `Learn More` 单独成条会被判"无实质信息"，必须带宾语。

**产品与规格 5 条**：型号、电压电流、认证标准号、应用场景、技术差异化。
最好是**关键词原词嵌入 2–3 条**，直接抬升 Ad Strength。

### 第 4 步：说明 5 条

每条必须**独立成立**（Google 会随机组合，不能有"接上条"的逻辑）。建议结构：

| # | 结构 | 例子 |
|---|---|---|
| 1 | 产品 + 规格 + 应用场景 | `1000V DC contactors built for EV chargers and solar storage.` |
| 2 | 供应优势 + 行动承诺 | `Factory-direct supply with OEM options. Quote in 1 business day.` |
| 3 | 质量/技术证据 | `Sealed arc chamber, tested contact resistance. Datasheets on request.` |
| 4 | 信任背书 | `Supplying switchgear buyers for 15 years. Samples before volume.` |
| 5 | 服务/定制（备用） | `Custom coil voltage and mounting. Engineers help you match models.` |

### 第 5 步：站内链接 6 条

每条三行都要填满（空行会降低展示机会）。**落地页必须真实存在**，否则会被拒。

| 类型 | 标题示例 | 说明行示例 |
|---|---|---|
| 产品型号页 | `HVDC Contactor Models` | `Compare ratings and form factors` |
| 资料下载 | `Request Datasheets` | `Full electrical specifications` |
| 定制/OEM | `OEM & Custom Orders` | `Coil voltage and mounting options` |
| 认证合规 | `Certifications` | `UL, CE and RoHS documentation` |
| 关于我们 | `About {Brand}` | `15 years in switchgear supply` |
| 联系销售 | `Contact Sales` | `Send your specification` |

### 第 6 步：宣传信息 5 条（≤25）

短、硬、可验证。B2B 优选：`Factory Direct Pricing` / `UL & CE Certified` /
`Samples Available` / `OEM & ODM Support` / `15 Years Experience` / `Low MOQ`

> ⚠️ Google 要求**至少 4 条**才会展示，5 条正合适。

### 第 7 步：结构化摘要 2 组

**标题必须从 Google 固定清单选，不可自创**（自创会直接报错）。适合工业/电池/电子类目：

`Types` · `Brands` · `Models` · `Features` · `Compatible With` ·
`Service catalog` · `Voltage` · `Capacity`

每组 **≥3 个值**（少于 3 个不渲染），每个值 ≤25 字符。

```json
{"header": "Types",    "values": ["HVDC Contactor", "DC Relay", "Fuse Holder"]}
{"header": "Features", "values": ["Sealed Arc Chamber", "1000V DC Rating"]}
```

### 第 8 步：硬校验（不可跳过）

把产出写成 JSON，跑校验器：

```bash
python scripts/validate_gads_copy.py copy.json
```

校验器检查：所有字符上限、数量、重复项、全大写、连续标点、电话邮箱、
免运费违禁、虚假陈述、危险品表述、结构化摘要标题合法性。

退出码 `0` = 通过；`1` = 有错误必须修；`2` = 有警告。

### 第 9 步：导出交付

```bash
python scripts/export_gads_copy.py copy.json --xlsx
```

产出：
- `*_rsa.csv` — Google Ads Editor 直接导入（**默认 Paused**）
- `*_assets.csv` — 站内链接 / 宣传信息 / 结构化摘要
- `*_review.html` — 明亮配色审阅页，逐条标字符数（绿=合规/红=超限）
- `*_copy.md` — 纯文本，便于贴工单
- `*_copy.xlsx` — 需 `pip install openpyxl`

**交付时主动打开 HTML 给用户看**，并附一句散文总结（不是罗列）。

## 逼近上限的写法（用户明确要求"尽可能逼近但不超过"）

先写长版本，再用脚本量，然后**只删冗余词不删信息**：

| 手法 | 前 | 后 |
|---|---|---|
| 删冠词 | `The factory direct supplier` | `Factory Direct Supplier` |
| 数字代替文字 | `five thousand cycles` | `5,000 Cycles` |
| 缩写保留原形 | `United States` | `US` |
| 删虚词 | `Send us your spec and we will quote` | `Send your spec for a quote` |
| 符号代词 | `and` → `&` | `UL & CE` |

**目标：标题 26–30 字符、说明 85–90 字符。**留 0 余量是可以的（30/30 合法），
但要确保不是靠截断词尾达成的。

## 政策红线（交付前逐条对照）

### ❌ 绝对不能写

| 类别 | 禁止 | 原因 |
|---|---|---|
| 虚假陈述 | `#1`、`best in the world`、`cheapest`、`100% guaranteed` | 无佐证即违规 |
| 虚假稀缺 | `Only 3 left`、`Hurry`、`Act now` | 不真实即违规 |
| 认证夸大 | 写了 UL/CE 但落地页查不到 | 落地页必须能兑现 |
| 全大写 | `BEST BATTERY SUPPLIER` | 后台直接拒 |
| 连续标点 | `!!`、`...`、`--` | 拒 |
| 装饰符号 | `★★★`、`@#$%` | 拒 |
| 电话/邮箱 | 文案里放联系方式 | 用 call 资产 |
| 纯 CTA | `Click Here` 单条 | 无实质信息 |

### ⚠️ B2B 批发专属

- **禁提免运费**：批发价已含运费，写 `Free Shipping` 会让采购反推单价虚高。
  改为 `Freight quoted with your quote`。
- **可以讲**：`No Ocean Freight` / `No Import Tariffs` / `No Container Wait`（本地制造叙事）。
- **不写具体价格**：报价制业务，写价格但落地页没有会违规。
- 落地页必须能承接批发询盘（有表单/报价入口），否则相关性低、烧钱。

### 落地页硬要求
可公开访问（无登录墙、非 403）、标题与广告承诺一致、不是纯下载页。

## 常见错误

1. **18 条全塞进导入 CSV** → 后台拒第 16–18 条。只导 15 条。
2. **18 条标题是同义改写** → Ad Strength 上不去。要 18 个不同角度。
3. **站内链接说明行写 40–50 字符** → 上限是 35，不是 90。最常见翻车点。
4. **结构化摘要自创标题**（如 `Our Products`）→ 直接报错，必须用固定清单。
5. **结构化摘要只填 2 个值** → 不渲染。
6. **宣传信息只写 3 条** → Google 不展示，最少 4 条。
7. **固定位置钉太多** → Ad Strength 下降。最多钉 1 条（通常是品牌名）。
8. **编造客户数/年限/认证** → 账户级风险，只写用户确认过的事实。

## 验证清单

- [ ] 标题 18 条（15 上稿 + 3 备用），每条 ≤30，零重复
- [ ] 5 条讲供应实力、5 条是 CTA（有动作动词和宾语）
- [ ] 说明 5 条（4 上稿 + 1 备用），每条 ≤90，可独立成立
- [ ] 站内链接 6 条，标题 ≤25、说明行 ≤35/≤35，落地页真实存在
- [ ] 宣传信息 5 条，每条 ≤25
- [ ] 结构化摘要 2 组，标题在固定清单内，每组 ≥3 值，每值 ≤25
- [ ] `validate_gads_copy.py` 退出码 0
- [ ] 无全大写、无连续标点、无电话邮箱、无编造事实
- [ ] B2B 文案未提免运费
- [ ] 每组标题嵌入了该组关键词原词
- [ ] HTML 审阅页已打开给用户看

## 文件

- `scripts/validate_gads_copy.py` — 字符数 + 政策校验器（`--selftest` 自检）
- `scripts/export_gads_copy.py` — 导出 CSV / HTML / MD / XLSX
- `scripts/check_render.py` — HTML 多断点渲染检查（1440/768/390）
- `examples/hiitio-example.json` — 完整双分组示例（可直接跑）
- `references/character-limits.md` — 字符上限与官方出处
- `references/copy-formulas.md` — 各槽位文案公式与句式库
- `references/b2b-vs-retail-voice.md` — B2B 与零售语气差异
- `references/policy-red-lines.md` — 政策红线完整清单
- `references/snippet-headers.md` — 结构化摘要固定标题清单
