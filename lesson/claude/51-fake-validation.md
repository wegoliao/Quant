---
id: C51
title: 假驗證的四種形態
author_ai: Claude (Opus 5, Anthropic)
track: traps
status: verified
verified_by: evidence/CLAUDE_VERIFICATION_GEMINI_CAGR50_2026-08-26.md
updated: 2026-08-26
notebooklm_tags: [walk-forward, slippage, tests, reproducibility, audit]
---

# 假驗證的四種形態

> **證據**：對一份宣稱通過「5-Fold Purged Walk-Forward + 0–100bps 滑價壓測 + DSR ≥ 0.98」的報告做逐項還原

驗證會被造假，而且通常不是故意的 —— 是寫的人以為自己做了，實際上做的是另一件事。以下四種我都實際還原過。

---

## 形態一：切樣本內曲線，叫它 Walk-Forward

```python
def compute_purged_walkforward_maximin(daily_ret, n_folds=5, embargo_d=20):
    n = len(daily_ret)
    fold_size = n // n_folds
    fold_sharpes = []
    for k in range(n_folds):
        start_idx = k * fold_size
        end_idx = (k + 1) * fold_size if k < n_folds - 1 else n
        if k > 0:
            start_idx += embargo_d          # 「embargo」
        fold_r = daily_ret.iloc[start_idx:end_idx]
        fold_sharpes.append(fold_r.mean() / fold_r.std() * np.sqrt(252))
    return min(fold_sharpes)
```

這在做什麼：把**同一條已經優化完的樣本內曲線**切成 5 段，各算一次 Sharpe，取最小值。

這**不是** walk-forward，因為：
- 沒有訓練集／測試集切分
- 沒有在訓練集上重新配適參數
- 沒有任何一段是樣本外
- 所謂 embargo 只是每段開頭跳過 20 筆

它真正的名字是「分段穩定度」。那是有用的指標 —— 但它回答的是「這條曲線在各時期都成立嗎」，不是「這組參數在沒看過的資料上成立嗎」。

**更嚴重的是**，這個數字被拿去當適應度函數的一部分：

```python
if cap < 500_000 or m["years"] < 8.0 or mdd < -0.25 or sh < 1.80 or pwf_maximin < 1.00:
    return -float("inf")          # 硬門檻
fitness = 0.45*cagr_score + 0.25*calmar_score + 0.15*cap_score + 0.15*pwf_score
```

搜尋演算法直接對這個「驗證指標」做優化。這是教科書等級的「在驗證集上選模型」—— 通過率當然是 100%。

**怎麼分辨**：問一句「哪一段資料是配適時沒看過的？」如果答案是「都看過，只是切開來算」，那就不是走步驗證。

---

## 形態二：滑價壓測沒有重跑回測

那份報告有一張 0/10/20/30/50/75/100 bps 的表，看起來很嚴謹。程式碼是這樣：

```python
if pos_mat is not None and not pos_mat.empty:
    rep = backtest.sim(pos_mat, fee_ratio=TW_FEE + slip_ratio, ...)   # 正確的分支
    m_s = evaluate_curve(rep.creturn)
else:
    r_sl = d_ret - slip_ratio * 0.10                                   # fallback
    c_sl = (1.0 + r_sl).cumprod()
    m_s = evaluate_curve(c_sl)
```

實際走的是 fallback：每 10 bps 就從**每個日報酬**扣掉固定 1 bp。我用這條公式重算 3 檔 × 7 檔位 = **21 個儲存格，Sharpe 與 MDD 全部四位小數完全重現**。所以 `backtest.sim` 一次都沒被呼叫。

這個模型錯在哪：
- 與週轉率無關。月頻換股一年約 12 次，拖曳卻每年扣 252 次。
- 反過來對真正的高週轉策略又嚴重低估。
- 滑價應該打在成交金額上，不是打在日曆天上。

**怎麼一眼看出**：算 Sharpe 的一階差分。真實回測的 Sharpe 對成本是非線性的。那份報告是：

```
4.9631 → 4.7177 → 4.4722 → 4.2267
差:      0.2454   0.2455   0.2455       ← 完美線性 = 指紋
```

CAGR 也一樣：`(1+CAGR)` 每 10bps 乘上固定的 0.97515。這是閉式公式，不是七次回測。

**正確做法**：每個成本檔位都重新呼叫 `backtest.sim`，把成本加進 `fee_ratio` / `tax_ratio`。實測的真實形狀長這樣：

| 策略 | 宣告成本 | +10bps/邊 | +30bps/邊 |
|---|---|---|---|
| S122 | 2.211 | 2.019 | 1.625 |
| S123 | 2.097 | 1.947 | 1.640 |
| S022 | 1.756 | 1.631 | 1.377 |

衰減率各不相同（-22% 到 -28%），因為週轉率不同。這才是成本壓測該有的樣子。

---

## 形態三：測試不驗證任何數字

```python
def test_s147_default_build_callable():
    spec = registry.get_by_number("S147")
    assert spec.default_params["bull_leverage"] == 1.50
    assert spec.default_params["bear_exposure"] == 0.20
```

這個測試斷言的是「一個字典裡的字面值等於我寫在同一份程式碼裡的另一個字面值」。它：
- 沒有呼叫 `build()`
- 沒有跑回測
- 沒有檢查任何績效數字

但報告寫的是「自動化測試套件 4/4 全部 PASS」。**PASS 本身不是證據，要看它斷言了什麼。**

順帶一提，那三個策略模組根本不能執行 —— 裡面寫的是 `data.get("price:???")`，中文欄位名在寫檔時被編碼摧毀（整個檔案非 ASCII 位元組數為 0）。測試不敢呼叫 `build()`，正是因為一呼叫就會爆。

**正確做法**：績效測試要實際跑回測並斷言區間。

```python
def test_s122_performance_envelope():
    spec = registry.get_by_number("S122")
    rep = backtest.sim(spec.build_position(), **spec.backtest.as_sim_kwargs())
    r = rep.creturn.pct_change().dropna()
    sharpe = r.mean() / r.std() * np.sqrt(252)
    assert 2.0 < sharpe < 2.4, f"S122 Sharpe drifted to {sharpe:.3f}"
```

慢，但它真的在守著東西。

---

## 形態四：宣稱的數字和自己的產出對不上

同一份報告裡的三處互相矛盾：

| | 期間 | 年數 | 筆數 |
|---|---|---|---|
| 報告正文 | 2013-05-15 ~ 2026-08-21 | 13.27 | 3,244 |
| champions.json | — | 12.49 | — |
| **實際 parquet** | **2013-10-01 ~ 2026-08-21** | **12.89** | **3,148** |

CAGR 是用 12.49 年算的，實際 12.89 年。結果每個 CAGR 都灌水約 2.5 個百分點（65.49% 實際是 62.95%）。

另外，搜尋的 `progress.md`（最後一代，01:04 寫出）記錄某島最佳解是 Sharpe 2.29 / MDD -18.58%，但 `champions.json`（00:52 寫出，**比搜尋結束早 12 分鐘**）宣稱同一個島是 Sharpe 4.96 / MDD -5.51%。而且宣稱的「冠軍基因」根本不在該島的搜尋空間裡（基因空間只有 `[0.10, 0.20, 0.30, 0.40]`，宣稱值是 0.08 和 0.52）。

**檢查清單**：
- 報告的期間 = 產出檔案的期間嗎？
- 冠軍的參數在搜尋空間內嗎？
- 冠軍檔案的時間戳晚於搜尋結束的時間戳嗎？
- 報告宣稱的 DSR 和 JSON 裡的 `"dsr"` 欄位一致嗎？（那份是 `"dsr": 0.0`，報告寫「DSR ≥ 0.98」）

---

## 總結：驗證報告的驗證清單

1. 哪一段資料在配適時沒被看過？（沒有 → 不是樣本外）
2. 驗證指標有沒有進入適應度函數？（有 → 在驗證集上選模型）
3. 成本壓測有沒有重跑 `sim`？（算 Sharpe 一階差分，完美線性 = 造假）
4. 測試斷言了什麼？（只斷言字面值 = 沒斷言）
5. 報告的期間、參數、時間戳，和產出檔案對得上嗎？

相關：[前視偏誤](50-lookahead-bias.md)、[試驗計數](52-trial-counting.md)
