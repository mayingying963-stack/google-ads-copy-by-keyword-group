# 政策红线完整清单

Google Ads 拒稿和封户的主因。**比字符数重要得多。**

## 一、虚假陈述 Misrepresentation（B2B 最容易踩）

| 禁止 | 例子 | 为什么 |
|---|---|---|
| 无佐证的排名 | `#1 Battery Supplier`、`No.1 in China` | 需第三方佐证 |
| 无佐证的绝对化 | `Best in the World`、`Cheapest`、`100% Guaranteed` | 无法举证 |
| 编造客户数 | `50,000+ Customers`（实际没有） | 虚假陈述 |
| 虚假稀缺 | `Only 3 Left`、`Last Chance` | 不真实即违规 |
| 虚假紧迫 | `Offer Ends Today`（天天如此） | 不真实即违规 |
| 认证夸大 | 广告写 UL/CE，落地页无证书 | 落地页必须能兑现 |
| 点名比较 | `Cheaper Than Tesla` | 需能举证 |
| 价格不一致 | 广告 `$99`，落地页 `$129` | 严重违规 |

### 安全替代

```
❌ #1 Supplier        ✅ Factory Direct Since 2010
❌ Cheapest Prices    ✅ Volume Pricing Available
❌ 50,000+ Customers  ✅ Serving OEM Buyers Since 2010
❌ Only 3 Left        ✅ Stock Ready to Ship
```

## 二、技术性拒绝（后台硬校验）

| 禁止 | 说明 | 改法 |
|---|---|---|
| 全大写 | `BEST BATTERY SUPPLIER` | Title Case |
| 连续标点 | `!!` `...` `--` | 单个标点 |
| 多个感叹号 | `Buy Now!!!` | ≤1 个，最好 0 |
| 装饰符号 | `★★★` `@#$%` `◆◆◆` | 删除 |
| 电话号码 | 文案里放 555-1234 | 用 call 资产 |
| 邮箱地址 | `sales@x.com` | 放落地页 |
| 纯 CTA | 标题只有 `Click Here` | 加宾语：`Request a Quote` |
| 拼写错误 | `Recieve` | 校对 |
| 无意义大写混排 | `bEsT PrIcE` | 正常书写 |

### `&` 和 `+` 是允许的

```
✅ UL & CE Certified          （& 合法）
✅ 5,000+ Charge Cycles        （+ 合法）
✅ Ships in 5-7 Business Days  （连字符合法）
```

校验器会误判这些吗？不会——`validate_gads_copy.py` 只抓纯装饰符号。

## 三、禁止内容 Prohibited

仿冒品、危险品、武器、成人内容、赌博、未批准药品 —— 常规业务不涉及。

**锂电池类目特别注意**：不要在文案里出现危险品运输表述。

```
❌ Hazardous Materials Certified
❌ Explosive Risk Handled
❌ UN38.3 Exempt Shipping
```

正确做法：`UN38.3 Tested`（陈述已测试，不承诺运输豁免）。

## 四、受限内容 Restricted

需要资质才能投的类目（医疗、金融、政治广告、加密货币等）。常规 B2B 制造不涉及。
若客户涉及，需先提交资质认证。

## 五、落地页要求（账户级风险）

比单条广告被拒更严重：

- [ ] 可公开访问，**无登录墙**
- [ ] 返回 200，**不是 403 / 404**
- [ ] 不是纯 PDF 下载页
- [ ] 标题与广告承诺**一致**
- [ ] 有实际产品/服务内容，不是空壳页
- [ ] 移动端可用
- [ ] 若广告提认证，页面上能找到证书或可查编号

## 六、B2B 批发专属红线

| 规则 | 原因 |
|---|---|
| **禁提免运费** | 批发价含运费，写 Free Shipping 让采购质疑单价 |
| **不写具体价格** | 报价制 + 落地页无价格 = 虚假陈述 |
| **落地页须有询盘入口** | 否则相关性低、烧钱 |

可讲：`No Ocean Freight` / `No Import Tariffs` / `No Container Wait` / `Freight Quoted With Your Quote`

## 七、商标与竞品名

```
✅ Battery for Toyota Forklifts    （兼容性描述，合法）
❌ Toyota Battery                  （暗示原厂，侵权）
✅ Fits Bobcat and CAT Loaders     （兼容，合法）
❌ Genuine CAT Parts               （冒充原厂）
```

规则：**用 "for / fits / compatible with" 描述兼容性，不用所有格暗示原厂。**

## 校验器覆盖范围

`validate_gads_copy.py` 自动检查：

- 免邮 / 免运费词表（B2B 模式）
- 虚假陈述词表（`#1`、`best in the world`、`cheapest`、稀缺词）
- 危险品词表（`hazardous`、`explosive`）
- 全大写、连续标点、多感叹号
- 电话、邮箱、装饰符号
- 纯 CTA
- 结构化摘要标题合法性 + 值数量

**校验器抓不到的**（需人工判断）：
- 认证是否真实（要核对落地页）
- 数字是否编造（要问用户）
- 商标使用是否恰当
- 落地页是否可访问
