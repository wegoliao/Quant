---
id: B12
title: 本地胃納模型 · 最緊的那一檔決定整本帳
author_ai: Claude (Opus 5, Anthropic)
track: block
status: verified
depends_on: []
inputs: [position_frame, close, volume]
outputs: [capacity_ntd]
verified_by: evidence/honest_top5/all_metrics.json
updated: 2026-08-26
notebooklm_tags: [capacity, adv20, liquidity, participation, deployability]
---

# B12 · 本地胃納模型

## 它解決什麼

FinLab 的 `liquidity.capacity` 是伺服器端計算，離線取不到。但**胃納量是台股量化最重要的單一數字** —— 實測全庫 CAGR 最高（53.69%）、Calmar 最高（2.16）的那檔策略，胃納量是 **NT$70,802**。

沒有本地模型，你會在報告裡看到一堆漂亮的 CAGR，卻不知道哪些放得進錢。

## 契約

```python
def capacity_ntd(position, close, volume, participation=0.05, adv_window=20, q=0.5):
    """帳本 NAV 上限：持股中最緊的一檔碰到 ADV20 的 participation 時的規模。

    對應執行層規則「單一標的下單量 > ADV20 的 5% 即 BLOCK」。
    回傳全期中位數。等權假設。
    """
    adv = (close * volume).average(adv_window)

    held = position.astype(bool)
    n = held.sum(axis=1)
    held, n = held[n > 0], n[n > 0]
    if held.empty:
        return 0.0

    adv_al = adv.reindex(index=held.index, columns=held.columns, method="ffill")
    # 等權下每檔權重 = 1/n，該檔容得下的 NAV = participation * ADV / (1/n)
    per_name = adv_al.where(held) * participation
    tightest = per_name.min(axis=1) * n

    s = tightest.dropna()
    return float(s.quantile(q)) if len(s) else 0.0
```

非等權時把最後兩行換成：

```python
weights = position.div(position.sum(axis=1), axis=0)
per_name = (adv_al * participation) / weights.where(weights > 0)
tightest = per_name.min(axis=1)
```

## 三個設計決定（都要在報告裡講明）

**1. 取最緊的那一檔（`min`），不是平均。**
帳本的胃納由最難買的那檔綁死。取平均會讓一檔流動性極差的股票被 39 檔好股票稀釋掉，得到一個你實際上做不到的數字。

**2. 取中位數（`quantile(0.5)`），不是最小值也不是平均。**
最小值會被單一異常日綁架（某天某檔停牌、某天成交量枯竭）。平均會被高流動性期間拉高。中位數回答「一般日子你能放多少」。

**3. participation 是常數，不是參數。**
它必須等於執行層真正會 BLOCK 的那個閾值。如果執行層是 5%，這裡就是 5%。兩邊不一致，你的研究會核准執行層拒絕的東西。

## 這個模型不能宣稱的事

要在報告裡寫清楚，否則會被過度信任：

- **沒有模擬市場衝擊。** 它只回答「不超過 ADV 的 5%」，不回答「買下去會推價多少」。
- **沒有考慮進出不對稱。** 賣出的流動性通常比買入差，尤其在你想賣的時候。
- **和 FinLab 伺服器端的數字不會一樣。** 要標明是哪一個口徑。
- **月頻換股的假設。** 如果你的策略會在幾天內大幅換手，單日參與率會遠高於這個模型的隱含值。

## 混合帳本：胃納由最緊的那一腳綁死

想用「70% 大容量 + 30% 小型股爆發」兩全其美？這是恆等式，不是可以設計繞過的東西：

```
小型股腳的原生胃納 = C_small
配置權重           = w
總帳本 NAV 上限    = C_small / w
```

`C_small = 70,000`、`w = 0.30` → 總帳本上限 **NT$233,333**。

配得越少總胃納越大，但你稀釋掉的正是你想要的爆發力。

**反面教材**：我驗過一份報告用 `cap = 常數 / w_smallcap` 宣稱混合後胃納「提升 11 倍」。那個公式確實會隨權重下降而變大，但它不是胃納模型，只是一個倒數 —— 而且代入該報告自己的權重後得到 NT$883,062，它卻寫 NT$630,759。

## 實測：胃納量如何改變排名

| S### | Sharpe | CAGR | Calmar | 胃納量 | 可部署 |
|---|---|---|---|---|---|
| S122 | 2.211 | 21.78% | 1.84 | NT$1,077,368 | 是 |
| S144 | 2.110 | 32.26% | 1.39 | NT$192,132 | **否** |
| S127 | 2.107 | **53.69%** | **2.16** | **NT$70,802** | **否** |
| S123 | 2.097 | 26.62% | 1.58 | NT$2,278,084 | 是 |
| S004 | 1.993 | 35.17% | 1.17 | **NT$79,251** | **否** |

按 Sharpe 排的前五名，三名放不進錢。

**所以排序邏輯是：先過胃納門檻 → 在通過的裡面排 Sharpe → 沒通過的另立一張表但仍然列出。** 第三步不能省 —— 那些策略告訴你 alpha 在哪裡，只是你拿不到。

## 相關

- 為什麼這是真正的約束：[C41 胃納量](../41-capacity-is-the-constraint.md)
- 造假的三種寫法：[C53 胃納量造假](../53-capacity-fiction.md)
- Gemini 的執行端版本：[GB04 ADV20 容量守門員](../../gemini/blocks/GB04-adv-capacity-guard.md)。那一塊守的是**下單當下**（這張單會不會超過 ADV），本塊算的是**研究階段**（這個策略整體能放多少錢）。兩者的 participation 常數必須一致，否則研究會核准執行端拒絕的東西。
