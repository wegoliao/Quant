---
id: X2
title: 積木 · TWSE 盤中零股集合競價——決定價 P* 的法定順序
author_ai: ox-alpha (Hermes Agent / Nous Research)
track: execution
status: verified
updated: 2026-08-26
source_repo: src/quant_grill_lab/execution/odd_lot_auction.py + REVIEW-005 Finding O1/O2
web_url: https://wegoliao.github.io/Quant/lesson/ox/02-oddlot-auction-twse-rules.html
notebooklm_tags: [twse, odd-lot, call-auction, tick-grid, matching-rules, fail-unknown]
---

# TWSE 盤中零股集合競價：P* 怎麼選、我方單怎麼配

## 一句話

台股盤中零股是集合競價市場，決定價 P* 由 **TWSE 營業細則 §58-3 的三條件＋一個 tie-break**
法定順序決定，不是「買賣失衡最小」；而公開資訊只有五檔，當你的限價越過第五檔，
唯一誠實的答案是 UNKNOWN，不能宣稱精確成交。

## 痛點

原實作用 `min_surplus = abs(cum_bid − cum_ask)` 最小來選 P*——這是**猜的**。
同一個錯被兩個 AI（Codex 與 DeepSeek Pro）獨立抓到，證明它不是筆誤而是世界觀缺口：
「最大量＋最小失衡」直覺上很合理，但交易所的規則寫的不是這樣。

## 黑盒子解構：法定四步

```
TWSE 營業細則 §58-3 決定價順序（依序套用）:
  1. 滿足最大成交量
  2. 高於 P* 的買單與低於 P* 的賣單須全數滿足
  3. P* 上至少一側全數滿足
  4. 若仍有多個價位 → 取最接近最近成交價
     （無最近成交價則接近開盤競價基準）
同價超額配置: 價格優先 → 同價時間優先
  （第一次撮合前同價才隨機, 之後依輸入時序 —— 不是一律 pro-rata）
```

### 我方單注入的正確位置

下一盤撮合本來就包含我方單 → **注入後才算 P***（原作這點是對的）。
但真正的限制在資料面：

```
你能看到的:   未成交五檔 (best 5 levels)
你看不到的:   完整委託簿
所以:         限價越過第五檔, 或數量 > 可見對手量
              ⇒ 只能回報 bound / UNKNOWN
              ⇒ 禁止把精確數字填進 proposal
```

### tick 階梯（台股升降單位，比照普通交易）

| 價格帶 | tick |
|---|---|
| < 10 | 0.01 |
| 10–50 | 0.05 |
| 50–100 | 0.1 |
| 100–500 | 0.5 |
| 500–1000 | 1 |
| ≥ 1000 | 5 |

Codex 實跑驗證跨界 `9.98→10.10`、`49.90→50.20`、`99.8→100.5`、`499→502`、`998→1010`
皆無漏價；但私有 `_tick_grid()` 在 500 點時**靜默截斷**且接受 off-grid limit
→ 修法：刪掉重複實作，重用 repo 內 canonical `tactics.costs.tick_grid()`，超限必須 raise。

## 契約不變量

- P* 必須落在合法 grid 且滿足 §58-3 全部三條件
- 五檔不足以確定結果時回 `INSUFFICIENT_VISIBLE_BOOK / UNKNOWN`，**fail-close 不猜測**
- 配置時分開「既有同價量」與「我方新增量」，按價格→時間優先計算
- 單邊空書／全零量 → `NO_CROSS`（fail-close 正確）

## AI 對話提問範本

1. 「請用 TWSE §58-3 逐條檢查這段撮合程式碼的決定價邏輯，指出哪一行違反哪一條。」
2. 「為什麼『最小買賣失衡』不是合法的集合競價 tie-break？給一個會產生不同答案的具體訂單簿。」
3. 「我的下單前試算只能看到五檔，哪些情況下任何精確成交預估都是自欺？應該回傳什麼？」

---
上一顆：[X1 對抗性稽核法](01-adversarial-audit-method.md)。下一顆：[X3 驗證鏈偽造](03-auth-chain-forgery.md)。
