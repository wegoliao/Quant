---
id: G03
title: 戰術分配 · 凸性整數規劃與真實帳戶部位定價
author_ai: Gemini (Google DeepMind / Antigravity)
track: tactics
status: verified
updated: 2026-08-26
source_repo: https://github.com/wegoliao/Quant/tree/main/67.quant_lesson/lesson/gemini/
web_url: https://wegoliao.github.io/Quant/lesson/gemini/03-tactics-and-integer-sizing.html
notebooklm_tags: [tactics, integer-programming, sizing, allocation, portfolio-construction]
---

# 戰術分配 · 凸性整數規劃與真實帳戶部位定價

## 一句話總結 (TL;DR)

策略回測給的是「理想浮點數權重」（例如 5%），但真實帳戶只有「有限現金預算」（例如 NT$50 萬），必須買入「整數張數（1,000股）或零股」。簡單的四捨五入會完全摧毀策略結構；本章詳解如何用**凸性 L1 追蹤誤差整數規劃（Integer Programming）**精確求解最佳下單股數。

---

## 1. 為什麼傳統的四捨五入（Rounding）是錯的？

### 典型反例：
假設可用現金預算為 **NT$ 209,000**：
- **股票 A**：每張單價 NT$ 10,000，目標理想金額 NT$ 19,000（期望 1.9 張）
- **股票 B**：每張單價 NT$ 100,000，目標理想金額 NT$ 190,000（期望 1.9 張）

#### 做法一：傳統向下取整 (Floor)
- 股票 A 買 1 張（花 10,000）
- 股票 B 買 1 張（花 100,000）
- 總共花費 NT$ 110,000，剩下 NT$ 99,000 閒置！因為買不起第 2 張 B，便把零錢拿去多買 9 張 A：
  - 最終持股：A 買 10 張（NT$ 100,000），B 買 1 張（NT$ 100,000）
  - **結果**：A 與 B 變成等權重！策略原本強烈看好 B 的意圖被徹底抹煞，L1 追蹤誤差高達 **91**。

#### 做法二：全局凸性整數規劃 (Pareto Optimization)
- 演算法發現：**「如果放棄購買股票 A（買 0 張），省下的錢剛好足夠買第 2 張 B（買 2 張）」**！
- 最終持股：A 買 0 張，B 買 2 張（花費 NT$ 200,000）
- **結果**：L1 追蹤誤差降至 **29**！遠勝傳統做法。

> **核心啟發**：犧牲一檔平庸的小標的，去補足高權重大標的的整數張數，所獲得的組合貼合度遠高於死板的四捨五入。

---

## 2. 數學問題定義 (Mathematical Formulation)

給定策略目標籃子中各標的的理想金額 $I_i = \text{Target Capital} \times w_i$，單張/每股成本 $c_i$，單檔權重上限 $M_i$，以及帳戶可用總現金預算 $C_{\text{budget}}$：

$$\min_{\{n_i\}} \sum_{i=1}^{K} \left| n_i \cdot c_i - I_i \right|$$

受限於以下約束條件：
1. **預算約束**：$\sum_{i=1}^{K} n_i \cdot c_i \cdot (1 + \text{fee\_rate}) \le C_{\text{budget}}$
2. **整數約束**：$n_i \in \mathbb{N}$（整張為 1000 之倍數，或允許零股）
3. **單檔上限**：$n_i \cdot c_i \le M_i$
4. **搜尋上界**：$0 \le n_i \le \left\lceil \frac{I_i}{c_i} \right\rceil$

---

## 3. 帕雷托前緣掃描演算法 (Pareto Frontier Sweep)

由於單檔誤差 $|n_i \cdot c_i - I_i|$ 為凸函數，且超過上限的張數在「花費」與「誤差」兩軸上均被嚴格支配（Strictly Dominated），我們採用逐檔摺疊（Fold-in）的動態規劃前緣維護：

```
State 0: (Cash = 0, Error = sum(Ideal))
  │
  ├── 展開標的 1 之可能張數 (0, 1, 2...) ──> 產生新前緣 (Cash_1, Error_1)
  │     └─ 剪枝：剔除被雙軸同時超越的劣解 (Dominated States)
  │
  ├── 展開標的 2 之可能張數 ──> 產生新前緣 (Cash_2, Error_2)
  │     └─ 剪枝...
  ▼
最終狀態：在前緣中挑選 Error 最小且不超支的最佳整數解
```

---

## 4. 核心積木代碼與使用方式

完整演算法與邊界處理已封裝於 [`GB03 凸性整數規劃分配器`](blocks/GB03-integer-basket-allocator.md)。

### 調用範例：
```python
from quant_grill_lab.tactics.allocation import allocate_basket, BasketTarget

targets = [
    BasketTarget(stock_id="2330", price=1000.0, weight=0.4),
    BasketTarget(stock_id="2317", price=200.0, weight=0.3),
    BasketTarget(stock_id="2454", price=1200.0, weight=0.3),
]

plan = allocate_basket(
    targets=targets,
    available_cash=500_000,
    allow_odd_lot=True,  # 是否允許零股
)

print(f"分配狀態: {plan.status}")
for alloc in plan.allocations:
    print(f"股票: {alloc.stock_id}, 股數: {alloc.shares}, 實際金額: {alloc.notional:,.0f}")
```

---

## 5. NotebookLM & AI 提問範本

- **提問範本 1**：「請用一個具體例子解釋，為什麼量化交易在小資金時不能使用簡單的四捨五入來計算下單股數？」
- **提問範本 2**：「凸性整數規劃分配器是如何透過 Pareto Frontier 剪枝來避免組合爆炸的？」
