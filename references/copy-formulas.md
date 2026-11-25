# 各槽位文案公式与句式库

## 标题槽位分配（18 条）

| 槽位 | 类别 | 目标 |
|---|---|---|
| 1–5 | **供应实力** | 采购第一眼判断"你是不是真厂家" |
| 6–10 | **CTA** | 推动下一步动作 |
| 11–15 | 产品与规格 | 关键词原词 + 参数 + 场景 |
| 16–18 | 备用 | 轮换池 |

## 一、供应实力（5 条）

B2B 采购的判断顺序：**是不是厂家 → 能不能定制 → 有没有认证 → 起订量 → 靠不靠谱**。
五条正好覆盖这五个疑问。

| 采购疑问 | 句式 | 例子（≤30） |
|---|---|---|
| 是不是厂家 | `{属性} Direct, No Middleman` | `Factory Direct, No Middleman` (30) |
| 能不能定制 | `OEM & ODM Available` / `{X} Customization` | `Custom Coil Voltage Options` (27) |
| 有没有认证 | `{认证} Certified` / `{标准号} Tested` | `UL & CE Certified Contactors` (28) |
| 起订量 | `Low MOQ for {客户类型}` / `{类型} Pricing` | `Bulk Pricing for Distributors` (29) |
| 靠不靠谱 | `{N} Years of {领域} Supply` | `15 Years of Switchgear Supply` (29) |

补充可用：
```
Sample Before You Order        Samples Available on Request
Supply Partner Since {year}    Custom Specs Accepted
Fast Lead Times from Stock     Volume Discounts Available
Grade-A {材料} Cells           Own {部件} Firmware
```

## 二、CTA（5 条）

**规则：必须带动词 + 宾语。**`Click Here` / `Learn More` 单独成条会被判"无实质信息"。

| 目的 | 句式 | 例子（≤30） |
|---|---|---|
| 要报价 | `Request a Quote {时间状语}` | `Request a Quote Today` (22) |
| 要现货 | `Get {资产} Instantly` | `Get Datasheets Instantly` (25) |
| 要对话 | `Talk to {角色}` | `Talk to Our Engineers` (23) |
| 要参数 | `Send Your Spec for Pricing` | `Send Your Spec for Pricing` (27) |
| 要对比 | `Compare {对象}` | `Compare Models and Ratings` (27) |

补充可用：
```
Download the Spec Sheet        Ask Our Technical Team
Get a Quote in 24 Hours        Request Volume Pricing
Speak to a {角色}               See Stock and Lead Times
```
> 感叹号最多 1 个，最好 0 个。`Get a Quote Today!` 合法，`Act Now!!` 违规。

## 三、产品与规格（5 条）

| 角度 | 句式 | 例子 |
|---|---|---|
| 型号 + 核心词 | `{电压}{电流} {产品词}` | `48V 105Ah LiFePO4 Battery` (25) |
| 应用场景 | `{产品词} for {场景}` | `HVDC Contactor for EV Charging` (29) |
| 标准号 | `Tested to {标准}` | `Tested to IEC 60269` (19) |
| 技术差异 | `{技术特征}` | `Sealed Arc Chamber Design` (25) |
| 兼容性 | `Fits {品牌/型号}` | `Battery for Toyota Forklifts` (28) |

**关键**：至少 2–3 条嵌入该组关键词原词，直接抬升 Ad Strength。

## 四、说明（5 条）

```text
1. 产品 + 规格 + 应用场景     {规格} {产品} built for {场景1} and {场景2}. {认证}
2. 供应优势 + 时间承诺       Factory-direct with OEM options. Quote in {N} business days.
3. 质量 / 技术证据           {技术特征}, {测试项}. Datasheets on request.
4. 信任背书                  Supplying {客户类型} for {N} years. Samples before volume.
5. 服务 / 定制（备用）        Custom {参数}. Our engineers help you match the right {产品}.
```

**每条必须独立成立**（Google 随机组合，不能写"如上所述""此外还有"）。

## 五、站内链接（6 条）

标准六件套（B2B 最稳的组合）：

| # | 标题（≤25） | 说明行1（≤35） | 说明行2（≤35） |
|---|---|---|---|
| 1 | `{产品} Models` | `Compare ratings and specs` | `Filter by voltage and current` |
| 2 | `Request Datasheets` | `Full technical specifications` | `Test reports on request` |
| 3 | `OEM & Custom Orders` | `Custom {参数} options` | `Engineering review included` |
| 4 | `Certifications` | `{认证列表} documentation` | `Download compliance files` |
| 5 | `About {Brand}` | `{N} years in {领域}` | `Factory-direct manufacturing` |
| 6 | `Contact Sales` | `Send your specification` | `Quote within {N} business day` |

> 三行必须都填。空行会显著降低展示机会。

## 六、宣传信息（5 条，≤25）

按"硬卖点优先"排列，不要五条都是形容词：

```
Factory Direct Pricing     UL & CE Certified        Samples Available
OEM & ODM Support          15 Years Experience      Low MOQ
Grade-A {材料}              Custom BMS Firmware      US Manufacturing
Tested & Documented        Volume Discounts         Fast Lead Times
```

## 七、结构化摘要（2 组）

强推 `Types` + `Features` 组合（覆盖面最广）：

```json
{"header": "Types",    "values": ["HVDC Contactor", "DC Relay", "Precharge Contactor", "Fuse Holder"]}
{"header": "Features", "values": ["Sealed Arc Chamber", "1000V DC Rating", "Low Contact Resistance"]}
```

其他组合：`Brands`（代理多品牌时）、`Models`（型号多时）、`Compatible With`（配件类）、
`Voltage` / `Capacity`（电池、电源类）。

## 压缩手法（逼近上限用）

| 手法 | 前 | 后 | 省 |
|---|---|---|---|
| 删冠词 | `The factory direct supplier` | `Factory Direct Supplier` | 4 |
| 数字代替文字 | `five thousand cycles` | `5,000 Cycles` | 8 |
| 缩写 | `United States` | `US` | 10 |
| 删虚词 | `Send us your spec and we will quote` | `Send your spec for a quote` | 11 |
| 符号 | `and` → `&` | `UL & CE` | 2 |
| 删介词 | `Contactors for EV chargers` | `EV Charging Contactors` | 5 |

**按顺序试，每改一版就重新量。不要靠截断词尾凑数。**
