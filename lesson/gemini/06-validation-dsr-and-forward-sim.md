---
id: G06
title: 防過擬合鐵律 · Deflated Sharpe Ratio (DSR)、PBO 與前瞻 SIM 證據鏈
author_ai: Gemini (Google DeepMind / Antigravity)
track: validation
status: verified
updated: 2026-08-26
source_repo: https://github.com/wegoliao/Quant/tree/main/67.quant_lesson/lesson/gemini/
web_url: https://wegoliao.github.io/Quant/lesson/gemini/06-validation-dsr-and-forward-sim.html
notebooklm_tags: [validation, dsr, deflated-sharpe, pbo, overfitting, forward-sim]
---

# 防過擬合鐵律 · Deflated Sharpe Ratio (DSR)、PBO 與前瞻 SIM 證據鏈

## 一句話總結 (TL;DR)

量化研究中最昂貴的自欺欺人，是「在電腦上跑了 1,000 次試驗，把 Sharpe 最高的那次當成真實實力」。本章詳解 Marcos López de Prado 提出的 **Deflated Sharpe Ratio (DSR)** 與 **PBO** 數學檢驗，並說明本系統如何透過「不可回填的前瞻 SIM（Forward SIM）」建立真實抗過擬合證據鏈。

---

## 1. 為什麼常規 Sharpe Ratio 是嚴重欺騙？

當你測試了 $N$ 個獨立策略（或同一策略的 $N$ 組參數），即使所有策略的真實期望值都為 0（純噪聲），從中選出的「最佳 Sharpe」之期望值約為：

$$E[\max_N \{ \widehat{\text{SR}} \}] \approx \sqrt{2 \ln N} \cdot \sigma_{\text{SR}}$$

例如：若測試了 $N = 400$ 次試驗，就算全部是隨機拋硬幣，挑出來的最佳 Sharpe 也會輕易達到 **1.5 ~ 2.0**！如果直接拿去實盤，必然面臨災難性虧損。

```
【試驗次數 vs 虛假 Sharpe 膨脹關係】
試驗次數 N = 1    ──> 期望虛假 Sharpe ≈ 0.0
試驗次數 N = 50   ──> 期望虛假 Sharpe ≈ 1.2
試驗次數 N = 400  ──> 期望虛假 Sharpe ≈ 2.1  <── (傳統回測在這裡誤以為發現聖杯)
試驗次數 N = 4000 ──> 期望虛假 Sharpe ≈ 2.8
```

---

## 2. Deflated Sharpe Ratio (DSR) 數學公式與校正

DSR 計算的是：**「在考慮了總試驗次數 $N$、樣本偏態（Skewness $\gamma_3$）、峰態（Kurtosis $\gamma_4$）與回測長度 $T$ 後，該策略真正超越虛假隨機期望值的機率」**：

$$\text{DSR} = \Phi\left( \frac{(\widehat{\text{SR}} - \text{SR}^*) \sqrt{T - 1}}{\sqrt{1 - \gamma_3 \widehat{\text{SR}} + \frac{\gamma_4 - 1}{4} \widehat{\text{SR}}^2}} \right)$$

其中門檻 $\text{SR}^*$ 為 $N$ 次試驗下的期望最大隨機 Sharpe：

$$\text{SR}^* = \sqrt{V[\{\widehat{\text{SR}}_n\}]} \left( (1 - \gamma) \Phi^{-1}\left(1 - \frac{1}{N}\right) + \gamma \Phi^{-1}\left(1 - \frac{1}{N \cdot e}\right) \right)$$

（$\gamma \approx 0.5772$ 為尤拉常數）。

### 本系統門檻：
- 策略宣告的試驗次數必須誠實包含所有被淘汰的試驗（如 $N \ge 400$）。
- 核心候選策略的 **DSR 必須 $\ge 0.95$（95% 信心水準）**，否則一律標記為未通過過擬合檢定。

---

## 3. 參數高原穩定性檢定 (Plateau Test)

```
        【孤峰過擬合 vs 參數高原】
   孤峰 (Overfitted Spike)       高原 (Robust Plateau)
         ▲                           ┌─────────┐
        ╱ ╲                          │ 冠軍參數 │
       ╱ ★ ╲                         │    ★    │
   ───┴─────┴───                 ────┴─────────┴────
   (參數微調即崩塌)              (鄰域變動依然穩健)
```

- **檢驗方法**：將策略的視窗期、持股檔數、進出場門檻在 $\pm 1$ 檔調整（共 $3^k$ 個鄰近網格）。
- **要求**：至少 **$\ge 80\%$** 的鄰近參數組合，其 Sharpe 與 CAGR 必須維持在最佳參數的 $85\%$ 以上。

---

## 4. 前瞻 SIM（Forward SIM）證據鏈

本系統的最高狀態標註為：
```text
HOLD_RESEARCH_ONLY_NO_PRISTINE_OOS
```
這代表：任何切分歷史資料的 Walk-Forward 都只是回溯診斷（Historical Diagnostic）。
真正的 Pristine OOS 只有一種：
1. **策略代碼與參數 SHA-256 凍結**（寫入不可篡改的封存檔）。
2. 從凍結日的**次一交易日**開始，每日自動產生訊號快照。
3. 嚴禁任何回填（Backfill），在真實時間推進下累積至少 **126 個交易日** 的實盤觀察。

---

## 5. 相關積木模組索引

- [`GB10 DSR / PBO 過擬合檢驗器`](blocks/GB10-dsr-pbo-validator.md)

---

## 6. NotebookLM & AI 提問範本

- **提問範本 1**：「請向非量化背景的投資人解釋，為什麼 Deflated Sharpe Ratio (DSR) 要把『做過多少次回測試驗』納入計算公式？」
- **提問範本 2**：「為什麼本系統認為歷史資料切分的 Walk-Forward 依然可能存在選擇偏誤，堅持必須做 Forward SIM？」
