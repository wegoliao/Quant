---
id: B13
title: 相關係數去重 · 你的前五名可能是同一支策略
author_ai: Claude (Opus 5, Anthropic)
track: block
status: verified
depends_on: []
inputs: [daily_return_series_per_strategy]
outputs: [deduped_shortlist, dropped_map, correlation_matrix]
verified_by: evidence/honest_top5/robustness.json
updated: 2026-08-26
notebooklm_tags: [correlation, deduplication, diversification, portfolio, selection]
---

# B13 · 相關係數去重

## 它解決什麼

兩個問題，同一個工具：

**問題一：同一支策略註冊了很多次。**
實測發現三個永久編號指向同一支策略，日報酬相關係數 **1.000**，績效數字完全相同。另一組三檔 ρ 0.95–0.99。靠檔名或家族欄位抓不出來 —— 它們的名字和家族都不一樣。

**問題二：你的「前五名」是同一個賭注的五種寫法。**
按 Sharpe 排出來的前五名，彼此相關係數 0.78–0.90。各配 20% 資金，你買到的是同一個因子，不是分散。

## 契約

```python
def dedup(rows, limit, rho=0.95, min_overlap=252):
    """按 Sharpe 由高到低取，相關係數 >= rho 的視為同一支，只留最好的那個。"""
    ranked = sorted(rows, key=lambda r: -(r["sharpe"] or 0))
    kept, kept_ret, dropped = [], {}, {}

    for r in ranked:
        n = r["strategy_number"]
        ret = load_returns(n)
        dup_of = None
        for k, kr in kept_ret.items():
            i = ret.index.intersection(kr.index)
            if len(i) > min_overlap and ret.loc[i].corr(kr.loc[i]) >= rho:
                dup_of = k
                break
        if dup_of is not None:
            dropped.setdefault(dup_of, []).append(n)
            continue
        kept.append(r)
        kept_ret[n] = ret
        if len(kept) >= limit:
            break

    return kept, dropped
```

**`min_overlap` 不能省。** 兩條只重疊 30 天的曲線可以輕易得到 0.97 的相關係數，那毫無意義。

## 去重之後一定要出相關係數矩陣

去重門檻 0.95 只擋掉「幾乎完全一樣」的。**0.90 不會被擋掉，但 0.90 也不是分散。**

實測矩陣（前七名）：

| | S122 | S138 | S123 | S124 | S125 | S022 | S148 |
|---|---|---|---|---|---|---|---|
| S122 | 1.00 | 0.89 | 0.87 | 0.83 | 0.78 | 0.62 | 0.52 |
| S138 | | 1.00 | 0.90 | 0.82 | 0.79 | 0.61 | 0.52 |
| S123 | | | 1.00 | **0.90** | 0.85 | 0.71 | 0.59 |
| S124 | | | | 1.00 | 0.82 | 0.72 | 0.59 |
| S125 | | | | | 1.00 | 0.70 | 0.57 |
| S022 | | | | | | 1.00 | 0.50 |

讀法：前五名（S122/S138/S123/S124/S125）是**一群**。真正不同的是第 1、第 6、第 7 名 —— S122 + S022 + S148，兩兩 0.50–0.62。

## 分群比排名有用

```python
def cluster(corr, threshold=0.75):
    """單連結分群：把相關係數高於 threshold 的視為同一個賭注。"""
    groups, seen = [], set()
    for a in corr.index:
        if a in seen:
            continue
        g = [b for b in corr.index if corr.loc[a, b] >= threshold]
        seen |= set(g)
        groups.append(g)
    return groups
```

實測 12 檔可部署候選，分成三群：

| 群 | 成員 | 群內最佳 Sharpe | 對其他群的相關 |
|---|---|---|---|
| 品質低波 | S122 / S138 / S123 / S124 / S125 | 2.211 | — |
| 多因子價值 | S022 / S048 / S126 | 1.756 | 0.61–0.72 |
| 凸性動能 | S148 | 1.545 | 0.50–0.59 |

**127 檔已註冊策略，真正不同的賭注只有三個。** 這是分群才看得出來的事。

## 陷阱

**陷阱 1：以為家族欄位可以代替相關係數。**
被判為完全重複的那三檔，家族欄位不完全一樣。名字騙人，報酬序列不騙人。

**陷阱 2：只在最後選投組時才去重。**
去重要在**計算 DSR 之前**做。重複註冊會讓試驗數虛胖、離散度失真。見 [B11 機械試驗計數器](B11-mechanical-trial-counter.md)。

**陷阱 3：把低相關當成「可以各配 20%」。**
相關係數低只代表它們不是同一個東西，不代表它們各自都經得起考驗。實測那三群裡，只有第一群的代表通過去膨脹檢定；另外兩群的代表沒過。**分散是為了降低單一因子依賴，不是為了讓沒通過的東西混進來。**

## 相關

- 完整清單與矩陣：[C70 已驗證積木清單](../70-verified-strategy-inventory.md)
- 為什麼要在 DSR 之前做：[C52 試驗計數](../52-trial-counting.md)
- 整條驗證流水線：[C60 驗證流水線](../60-verification-harness.md)
