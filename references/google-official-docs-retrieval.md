# 获取 Google 官方文档原文（受限网络下的取证顺序）

写 Google Ads 文案规格时，字符数、字段上限、报错码都必须能指出出处。
但 `support.google.com` / `ads.google.com` / `google.com` 在部分网络环境
整个域名不可达。下面是**按成功率排序**的取证路径。

## 先探测，再决定路线

```bash
for h in support.google.com developers.google.cn ads.google.cn \
         www.gstatic.com www.searchenginejournal.com www.semrush.com; do
  echo "$(curl -sL -m 12 -o /dev/null -w '%{http_code}' https://$h) $h"
done
```

`000` = 连不上（不是 404，是 TCP/TLS 就断了）。

## 路线 1（首选）：`developers.google.cn` — Google for Developers 中国镜像

**这个域名通常可达，且内容是官方原文**，只是中文翻译版。Google Ads API 文档里的
字段规格、数量限制、错误码写得非常完整，比产品页有用得多。

```
https://developers.google.cn/google-ads/api/docs/ads/create-ads?hl=zh-Hant
https://developers.google.cn/google-ads/api/docs/ads/create-ads?hl=zh-CN
https://developers.google.cn/google-ads/api/docs/policy-exemption/overview
https://developers.google.cn/google-ads/api/reference/rpc/latest/<Resource>?hl=en
```

抓下来是 JS 渲染的，用正则去标签后按关键词 grep：

```python
import re, html
s = open(path, encoding='utf-8', errors='ignore').read()
s = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', s)
s = re.sub(r'(?is)<br\s*/?>|</p>|</div>|</li>|</h[1-6]>|</tr>', '\n', s)
s = re.sub(r'<[^>]+>', ' ', s)
txt = re.sub(r'[ \t\xa0]+', ' ', html.unescape(s))
```

**实测有效的一句话原文**（RSA 字段规格）：

> 「广告标题（必填）：`responsive_search_ad.headlines` 中至少 3 个、最多 15 个
> 不重复的 `AdTextAsset` 对象（每个最多 30 个半形字元）。」

这条同时给出了**数量上限**和**字符上限**，是可引用的硬证据。

## 路线 2：`ads.google.cn` — Google Ads 中文产品站

可访问，但只有产品介绍和入口链接，**没有具体规则数字**。适合确认导航路径，
不适合查字符限制。它的 footer 里有 `support.google.com/google-ads/` 的链接，
但那个域名本身仍然不通。

## 路线 3：搜狗 / 360 搜索（Bing 不可信）

```bash
curl -sL -m 25 --compressed -A "<浏览器 UA>" \
  "https://www.sogou.com/web?query=<关键词>" -o out.html
```

**⚠️ 不要用 Bing。** 实测 Bing（含 `cn.bing.com`、`ensearch=1`、完整 query 回显）
返回的结果与查询词**完全无关**（查 Google Ads 字符限制，返回一堆 LLVM 下载页）。
回显完整 query 但按首 token 检索，不可当 Google 用。

搜狗 / 360 能返回真实中文解读文章，可作为**二手佐证**，但要在报告里标明可信度。

## 路线 4：第三方行业站点（只作交叉验证）

| 站点 | 状态 | 用途 |
|---|---|---|
| `www.searchenginejournal.com` | 首页 200，内页 000 | 不稳，别依赖 |
| `www.semrush.com` | 200 | 有 blog，但具体文章 URL 要现查 |
| `ppc.land` | 403 | 有反爬 |

**这些不是权威出处**，只能用来确认"行业普遍认为是这个数"。

## 报告里怎么标注可信度

必须区分两类，否则用户会以为全是官方原文：

| 内容 | 来源 | 标注 |
|---|---|---|
| RSA 30/90/15、3–15 / 2–4、报错码 | `developers.google.cn` 官方原文 | **高 · 逐字可溯源** |
| 站内链接 25/35/35、宣传信息 25、摘要值 25 | 后台校验行为 + 行业通行 | **中 · 需后台确认** |
| 政策红线分类 | 按官方政策结构整理，非逐字原文 | **中 · 非逐字** |

## 已验证不可达时怎么说

不要说"查不到所以不确定"就完了。正确表述：

> 本机 `support.google.com` 全域名不可达，因此政策帮助页部分按通行分类整理，
> 已在可信度表中逐项标出。硬性字符数来自 `developers.google.cn` 官方原文。
> 若要 100% 逐字政策原文，需要能访问 `support.google.com` 的网络环境。

用户接受这种诚实标注（他会追问数量和误差），不接受把二手中文博客说成官方原文。

## 顺带确认过的时效性事实

- **加大型文字广告 ETA 已于 2022-06 全量停用**。`developers.google.cn` 的
  create-ads 文档里**已完全没有 ETA 格式**，只有 RSA。这是判断资料是否过期的
  一个好信号：还在教"ETA 3 标题 + 2 描述"的教程一律是旧文。
