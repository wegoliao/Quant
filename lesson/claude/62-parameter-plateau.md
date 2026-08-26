---
id: C62
title: 參數高原：你選的是山峰還是平台
author_ai: Claude (Opus 5, Anthropic)
track: validation
status: verified
verified_by: scripts/run_honest_top5_robustness.py
updated: 2026-08-26
notebooklm_tags: [plateau, ablation, robustness, overfitting]
---

# 參數高原：你選的是山峰還是平台

> **證據**：12 檔候選，每個數值參數各擾動兩檔，全部重跑 `backtest.sim`

## 它在回答什麼

> 如果我把參數挪一格，這個策略還在嗎？

一個過擬合的參數是**尖峰**：`top_n=30` 得 Sharpe 2.2，`top_n=24` 或 `36` 掉到 1.0。那代表 30 這個數字是被資料的噪音選出來的。

一個真實的參數是**平台**：周圍一圈都還在 2.0 附近。那代表你抓到的是結構，不是巧合。

這是所有防過擬合檢查裡**最直觀、也最難造假**的一個 —— 因為每個鄰居都要真的重跑一次回測。

## 實作

```python
def neighbours(params):
    """每個數值參數往兩邊各挪一檔。"""
    out = []
    for k, v in params.items():
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            continue
        if isinstance(v, int):
            step = max(1, round(abs(v) * 0.2))       # 整數 ±20%
            cands = [v - step, v + step]
        else:
            cands = [round(v * 0.8, 6), round(v * 1.25, 6)]   # 浮點 ×0.8 / ×1.25
        for s in cands:
            if s != v and s > 0:
                out.append((f"{k}: {v} -> {s}", dict(params, **{k: s})))
    return out


PLATEAU_FLOOR = 0.70        # 鄰居要保住中心值 70% 的 Sharpe

for label, p in neighbours(spec.default_params):
    r = sim_returns(spec, p)                          # 真的重跑 sim
    s = r.mean() / r.std() * np.sqrt(252)
    passed = s >= PLATEAU_FLOOR * centre_sharpe
```

## 實測結果 —— 以及為什麼「100%」可能沒有意義

| S### | 通過率 | **鄰居數** | 最差鄰居 | 證據強度 |
|---|---|---|---|---|
| S022 | 100% | **12** | 1.667 | **強** |
| S144 | 100% | 8 | 2.107 | 中 |
| S127 | 100% | 4 | 1.742 | 中 |
| S004 | 100% | 4 | 1.795 | 中 |
| S148 | 100% | 4 | 1.444 | 中 |
| S122 | 100% | **2** | 2.095 | **弱** |
| S123 | 100% | **2** | 2.033 | **弱** |
| S124 | 100% | **2** | 1.983 | **弱** |
| S126 | 100% | **2** | 1.46 | **弱** |
| **S048** | **0%** | 2 | 兩個鄰居都拋錯 | **紅旗** |

**這張表最重要的一欄是「鄰居數」，不是通過率。**

S122 的通過率 100%，但它只有 2 個鄰居 —— 因為它只暴露 `top_n` 一個數值參數。「100% 通過」在這裡的意思不是「高原很寬」，而是「可以測的東西很少」。

真正被寬鬆測過的是 S022：12 個鄰居全過，最差 1.667。那是有份量的證據。

**所以報告要寫「100% of 2」而不是「100%」。** 只寫百分比會讓 S122 和 S022 看起來一樣強，但它們差很多。

## S048 的 0% 是紅旗，不是「未通過」

兩個鄰居都拋出例外，代表這個策略在參數稍微改變時就無法建構。這比「Sharpe 掉下去」更糟 —— 它連跑都跑不起來。

要把「鄰居失敗」和「鄰居 Sharpe 太低」分開記錄：

```python
except Exception as e:
    nb_res.append({"param": label, "sharpe": None, "pass": False,
                   "error": type(e).__name__})       # ← 記下錯誤類型
```

## 參數擾動 vs 結構擾動

有個重要區分。這個 repo 裡某檔策略的 notes 寫著：

> Plateau test 13/17 neighbours within 0.85x (92% counting parameter neighbours only; the four failures are leg removals, which are structural changes rather than perturbations).

「拿掉一整條因子腳」不是參數擾動，是結構改變。它失敗不代表過擬合，只代表那條腳有貢獻。

**兩者要分開報**：
- **參數擾動**（`top_n` 30→36）→ 測的是過擬合
- **結構消融**（拿掉整條腳）→ 測的是各元件的貢獻度

把兩者混在同一個百分比裡，兩邊的訊號都被稀釋。

## 消融實驗：另一個方向的用法

同一個機制反過來用，可以找出「哪些元件其實在扣分」。實測某檔四因子策略的逐腳消融：

```
移除低波動腳       -0.585 Sharpe    ← 最大貢獻
移除 14D 公布日對齊 -0.358 Sharpe    ← 免費的、純時序對齊
移除 ROE 腳        -0.190 Sharpe
移除營收成長腳     +0.044 Sharpe    ← 負貢獻
移除營收帶篩選     +0.037 Sharpe    ← 負貢獻
```

最後兩行是重點：這檔策略的招牌是「營收動能」，但它的兩個營收元件在 Sharpe 上是**淨負貢獻**。

這個發現直接生出了一檔新策略：保留有效的（低波動、公布日對齊、營收帶當篩選而非評分），把兩個營收元件換掉。新策略的 Sharpe 2.211 是全庫最高。

**但要誠實標註**：這樣選出來的「腳的集合」是被搜尋出來的。權重沒有擬合（四個百分位排名直接相加），但**組合本身是擬合的**。這一點必須寫進選擇偏差註記。

## 高原檢查的成本

12 檔候選、平均 4 個鄰居、每個鄰居約 10–20 秒 → 約 15 分鐘。

比起它能擋掉的東西，這是很便宜的。

## 檢查清單

1. 每個鄰居都真的重跑 `sim` 了嗎？（不能用內插）
2. 報告有寫鄰居數嗎？（「100%」不寫分母等於沒寫）
3. 鄰居失敗和鄰居分數低有分開記嗎？
4. 參數擾動和結構消融有分開報嗎？
5. 如果某策略只有 1–2 個數值參數，有在報告裡註明「證據弱」嗎？

## 記住

> 通過率的分母比分子重要。「100% of 2」和「100% of 12」是完全不同的兩件事。

相關：[去膨脹夏普](61-deflated-sharpe.md)、[驗證流水線](60-verification-harness.md)
