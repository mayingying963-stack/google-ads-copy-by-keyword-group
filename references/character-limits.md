# 字符上限与官方出处

## 硬上限（Google 会拒绝或截断）

| 资产 | 字段 | 上限 | 数量要求 |
|---|---|---|---|
| RSA | Headline 标题 | **30** | 最少 3，**最多 15** |
| RSA | Description 说明 | **90** | 最少 2，**最多 4** |
| RSA | Path 1 / Path 2 | **15** each | 可选；有 path2 必须同时有 path1 |
| Sitelink | Link text 标题 | **25** | — |
| Sitelink | Description line 1 | **35** | — |
| Sitelink | Description line 2 | **35** | — |
| Callout | Text | **25** | 最少 4 条才展示 |
| Structured snippet | Value | **25** | 每个 header ≥3 值才渲染 |

## 出处

数字来自 **Google for Developers · Google Ads API 文档**（`developers.google.cn`，可访问）：

> 「广告标题（必填）：`responsive_search_ad.headlines` 中至少 3 个、最多 15 个不重复的
> `AdTextAsset` 对象（每个最多 30 个半形字元）。」
>
> 「说明（必要）：`responsive_search_ad.descriptions` 中至少 2 个、最多 4 个不重复的
> `AdTextAsset` 对象（每个最多 90 个半形字元）。」
>
> 「显示网址路径（`path1` 和 `path2`）（选用）：每个栏位最多 15 个半形字元。
> 只有在设定 `path1` 时，才能设定 `path2`。」

Sitelink / Callout / Snippet 的 25 / 35 来自 Google Ads 后台实时校验；官方政策帮助页
（`support.google.com`）在部分网络环境不可达，这些数字按后台行为确认。

## 平台报错码（写进校验器）

| 情况 | 报错 |
|---|---|
| 标题或说明重复 | `AssetError.DUPLICATE_ASSET` |
| 填了 path2 但没填 path1 | `AdError.CANNOT_SET_PATH2_WITHOUT_PATH1` |

## 字符计数口径

- 官方按「半形字元」（half-width characters）计
- 英文 / 数字 / 半角标点 / 空格 = 1 字符
- 中文全角字 = 2 字符
- 我们产英文文案，Python `len(text)` 即结果

## 18 条标题的拆分规则

Google 后台上限 15 条。用户要求 18 条时：

```
标题 1–15  → 上稿（导入 Google Ads）
标题 16–18 → 备用（A/B 轮换池）
说明 1–4   → 上稿
说明 5     → 备用
```

**导出文件只含前 15 条标题、前 4 条说明。**第 16–18 条写进审阅页和 md 供轮换用。

## 已淘汰、不要再用

- **加大型文字广告 (ETA / Expanded Text Ads)** —— 2022 年 6 月全量停用。
  任何"3 个标题 30 字符 + 2 个描述 90 字符的 ETA"教程都是过期资料。现在搜索广告只有 RSA。

## 余量目标

用户要求「尽可能逼近上限而不超过」时：

| 字段 | 目标区间 | 说明 |
|---|---|---|
| 标题 | 26–30 | 0 余量合法，但不要靠截断词尾 |
| 说明 | 85–90 | 太长可读性下降，85 左右最佳 |
| 站内链接标题 | 20–25 | — |
| 站内链接说明行 | 28–35 | — |
| 宣传信息 | 18–25 | — |
