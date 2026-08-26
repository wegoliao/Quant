---
id: C53
title: 胃納量造假：三種寫法，都不是胃納量
author_ai: Claude (Opus 5, Anthropic)
track: traps
status: verified
verified_by: evidence/honest_top5/all_metrics.json
updated: 2026-08-26
notebooklm_tags: [capacity, adv20, fabrication, audit]
---

# 胃納量造假：三種寫法，都不是胃納量

> **證據**：對照某份報告的胃納量公式與其自己宣稱的數字

## 為什麼這件事最重要

在小型市場做量化，**胃納量是真正的約束，不是績效**。

實測：這個 repo 裡 CAGR 最高（53.69%）、Calmar 最高（2.16）、抗成本能力最強的那檔策略，胃納量是 **NT$70,802**。第二高的是 NT$79,251。

也就是說，最漂亮的數字全部集中在你放不進錢的地方。任何不把胃納量和 Sharpe 並列的排名，都在誤導。

## 造假形態一：倒數公式

```python
cap = 70_645.0 / max(0.01, w_s127)
```

「胃納量 = 一個常數除以某個袖袋的權重」。

這在數學上會產生你想要的行為（少配一點小型股 → 胃納量變大），但它不是胃納模型：
- 完全忽略其他袖袋的胃納
- 忽略「混合帳本的胃納受最緊的那一腳綁死」
- `w = 0` 時得到 `70645/0.01 = NT$7,064,500`，一個純粹由 clip 下界決定的數字

而且**連自己的公式都對不上**：`w_s127 = 0.08` 代入得 NT$883,062，但報告寫 NT$630,759。

## 造假形態二：寫死常數除以槓桿

```python
elif basket_type == "S123_BASE":
    d_base = daily_123
    cap = 2_279_291.0          # 寫死
...
eff_cap = cap / max(1.0, bull_leverage)
```

`2,279,291 / 1.5 = 1,519,527` —— 這就是報告裡那檔策略的「胃納量」。

全程沒有對加了槓桿的帳本做任何胃納計算。而且 1.5x 槓桿的胃納量不是「除以 1.5」那麼簡單：加槓桿之後每檔的絕對部位變大，衝擊成本是非線性的。

## 造假形態三：報 0，然後在報告裡寫別的

```json
"capacity": 0.0,
"capacity_local": 928859.0
```

一個欄位是 0（沒算成），另一個是本地估計。報告引用後者，但沒說前者是空的。

---

## 可用的本地模型

FinLab 的 `liquidity.capacity` 是伺服器端計算，離線取不到。所以要在本地重算，而且要對應到你自己宣告的執行規則。

這個 repo 的執行層規則是「單一標的下單量 > ADV20 的 5% 就 BLOCK」。本地重算就照這條：

```python
def capacity_ntd(position, participation=0.05, q=0.5):
    """帳本規模上限：持股中最緊的一檔碰到 ADV20 的 participation 時的 NAV。"""
    adv20 = (close * volume).average(20)

    held = position.astype(bool)
    n = held.sum(axis=1)
    held, n = held[n > 0], n[n > 0]

    adv_al = adv20.reindex(index=held.index, columns=held.columns, method="ffill")
    # 等權假設下，每檔權重 = 1/n，該檔容得下的 NAV = participation * ADV / (1/n)
    per_name = adv_al.where(held) * participation
    tightest = per_name.min(axis=1) * n
    return float(tightest.dropna().quantile(q))
```

三個必須講清楚的設計選擇：

1. **取最緊的那一檔**（`min(axis=1)`），不是平均。帳本的胃納由最難買的那檔綁死。
2. **取中位數**（`quantile(0.5)`），不是最小值也不是平均。最小值會被單一異常日綁架；平均會被高流動性期間拉高。
3. **等權假設**。如果你的策略不是等權，要改成 `per_name / weight`。

## 這個模型不能宣稱的事

- 它**沒有模擬市場衝擊**。它只回答「不超過 ADV 的 5%」，不回答「買下去會推價多少」。
- 它**沒有考慮進出對稱性**。賣出的流動性通常比買入差，尤其在你想賣的時候。
- 它是**本地重算**，和 FinLab 伺服器端的數字不會一樣。要標明是哪一個。

## 實測：胃納量如何改變排名

同一批策略，按 Sharpe 排 vs 加上胃納量門檻（NT$50 萬）：

| S### | Sharpe | CAGR | Calmar | 胃納量 | 可部署 |
|---|---|---|---|---|---|
| S122 | 2.211 | 21.78% | 1.84 | NT$1,077,368 | 是 |
| S144 | 2.110 | 32.26% | 1.39 | NT$192,132 | **否** |
| S127 | 2.107 | **53.69%** | **2.16** | **NT$70,802** | **否** |
| S123 | 2.097 | 26.62% | 1.58 | NT$2,278,084 | 是 |
| S004 | 1.993 | 35.17% | 1.17 | **NT$79,251** | **否** |

按 Sharpe 排的前五名，有三名放不進錢。

## 記住

> 在報告裡，胃納量要和 Sharpe 並列在同一張表，不能放附註。放附註等於沒放 —— 讀的人會先被 CAGR 53.69% 抓走注意力。

相關：[為什麼胃納量是真正的約束](41-capacity-is-the-constraint.md)、[已驗證積木清單](70-verified-strategy-inventory.md)
