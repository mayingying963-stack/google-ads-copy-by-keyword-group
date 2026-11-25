# 结构化摘要固定标题清单

Google 只接受下列标题，**自创标题会直接报错**。每组至少 3 个值才渲染，每个值 ≤25 字符。

## 通用行业

`Amenities` · `Brands` · `Courses` · `Degree programs` · `Destinations` ·
`Featured hotels` · `Insurance coverage` · `Models` · `Neighborhoods` ·
`Service catalog` · `Shows` · `Styles` · `Types`

## 工业 / 电池 / 电子器件（★ 最常用）

| 标题 | 适合场景 | 值示例（≤25） |
|---|---|---|
| ★ `Types` | 产品线有多种形态 | `HVDC Contactor` · `DC Relay` · `Fuse Holder` |
| ★ `Features` | 技术特征罗列 | `Sealed Arc Chamber` · `IP67 Rated` · `1000V DC` |
| ★ `Brands` | 代理/兼容多品牌 | `Siemens Compatible` · `Schneider Fit` |
| ★ `Models` | 型号清单 | `HVC-1000` · `HVC-750` · `HVC-500` |
| ★ `Compatible With` | 配件、兼容性 | `Solar Strings` · `Battery Storage` · `EV Chargers` |
| ★ `Service catalog` | 服务类型 | `OEM Design` · `Testing` · `Repair` |
| `Voltage` | 电源/电池电压档 | `48V` · `72V` · `96V` · `110V` |
| `Capacity` | 容量档 | `105Ah` · `200Ah` · `280Ah` |

## 其他（按需）

`Appliances` · `Types of homes` · `Programs` · `Health insurance` · `Specialties`

## 推荐组合

### 组合 A：产品线清晰（最通用）
```json
{"header": "Types",    "values": ["HVDC Contactor", "DC Relay", "Fuse Holder"]}
{"header": "Features", "values": ["Sealed Arc Chamber", "1000V DC Rating", "Low Resistance"]}
```

### 组合 B：配件/兼容类
```json
{"header": "Compatible With", "values": ["Solar Strings", "Battery Storage", "EV Chargers"]}
{"header": "Types",           "values": ["DC Fuse", "Fuse Holder", "Battery Fuse"]}
```

### 组合 C：电池规格类
```json
{"header": "Voltage",   "values": ["48V", "72V", "96V"]}
{"header": "Capacity",  "values": ["105Ah", "200Ah", "280Ah"]}
```

## 常见错误

| 错误 | 结果 |
|---|---|
| 标题自创 `Our Products` / `Why Choose Us` | 报错，无法保存 |
| 值只有 2 个 | 不渲染（浪费位置） |
| 值超过 25 字符 | 被截断或拒绝 |
| 值里放句子 | 应放名词短语，不是完整句 |
| 同一 header 用两次 | 报错 |
| 大小写不一致 | 建议 Title Case |

> 值里不要写完整句子。结构化摘要显示为一行带 · 分隔的短语列表，
> 写句子会被截断成看不懂的碎片。
