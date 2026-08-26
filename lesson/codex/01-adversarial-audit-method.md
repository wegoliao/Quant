---
id: X1
title: 積木 · 對抗性稽核法——為什麼 129 個測試全綠還是不安全
author_ai: ox-alpha (Hermes Agent / Nous Research)
track: validation
status: verified
updated: 2026-08-26
source_repo: .planning/handoff/REVIEW-005-codex-oddlot-audit.md
web_url: https://wegoliao.github.io/Quant/lesson/codex/01-adversarial-audit-method.html
notebooklm_tags: [adversarial-audit, testing, counterexample, false-confidence, codex]
---

# 對抗性稽核法：為什麼 129 個測試全綠還是不安全

## 一句話

測試只證明「程式行為符合測試的預期」；如果預期本身是猜的，
全綠只是把錯誤固化。對抗性稽核 = 拿真實世界的約束（交易所法條、
券商 API 文件、實際行情）去打程式的輸出，每一條 finding 附一個會失敗的具體輸入。

## 痛點

Opus 寫完零股撮合模組，129 個測試通過，看板寫「已交付」。三個跡象顯示這不夠：
1. 測試是同一個 AI 寫的——它會把自己誤解的世界觀寫進斷言
2. 「5,000 股 @ 484.00 預期成交 0 股」這條斷言聽起來合理（限價沒過？），其實是錯的
3. 沒有人拿 TWSE 法條逐條對過撮合順序

## 黑盒子解構：五步稽核流程

```
1. 讀規格來源   → TWSE 營業細則 §58-3、券商 API 官方 callback 文件
2. 選真實樣本   → 用實際持倉標的的五檔書（2408），不是人造對稱資料
3. 窮舉邊界     → tick 跨界(9.98→10.10, 499→502)、極寬 grid、空書、超大股數
4. 執行反例     → 在記憶體 fixture 裡真的跑，記下程式輸出 vs 規則應有輸出
5. 分級裁決     → BLOCKER(會賠錢) / HIGH(狀態錯亂) / MED(邊界截斷)，附檔案:行號
```

### 反例表（REVIEW-005 實測節錄）

| 輸入 | 程式輸出 | 依規則應該是 |
|---|---|---|
| BUY 347 @ 484.00 | P*=484.00, filled=347 | ✅ 正確 |
| BUY 5,000 @ 484.00 | filled=0 | 可見書中我方是唯一 484.00 買單，應成交 4,105 |
| BUY 10,000 @ 486.50 | filled=10,000 @ 486.00 | 可見賣量僅 8,765，結果不可能成立 |
| 攻擊者自簽 approval | SANCTION_OPEN=True, mode=REAL | 必須驗 pinned credential |

### 契約不變量

- 每條 finding 必須有「具體輸入 → 實際輸出 X → 應該是 Y」，沒有的不算數
- 沒找到問題就明寫「沒找到」＋列出掃過的邊界；**空手而回是合法結果**
- 既有測試要跑但不可信：先跑一遍建立基線，再獨立驗證斷言本身

## 最小可運行程式碼模式

```python
def audit_filling(engine, visible_book, my_order) -> AuditVerdict:
    """用可見五檔書對照交易所規則審查撮合引擎。

    Preconditions:
      - visible_book 是真實(或官方文件描述形狀的)五檔, 不是對稱假資料
      - engine.clear() 已通過既有測試套件 (基線)
    Postconditions:
      - 回傳逐項 verdict; 每個 fail 都帶 reproducible input
    """
    # 依 TWSE §58-3 三條件過濾合法 P* 候選:
    # (a) 最大成交量 (b) 更遠價全滿足 (c) 決定價上至少一側全滿足
    legal_ps = [p for p in tick_grid(low, high)
                if max_volume_at(p) == global_max_volume(p)]
    p_star = tiebreak_nearest_to_last_price(legal_ps)

    program_p, program_filled = engine.clear(visible_book, my_order)
    if (program_p, program_filled) != (p_star, expected_fill):
        return AuditVerdict("BLOCKER", input=my_order,
                            actual=(program_p, program_filled),
                            expected=(p_star, expected_fill))
    return AuditVerdict("PASS")
```

## AI 對話提問範本（貼進 NotebookLM / 任何 AI）

1. 「總結對抗性稽核與一般 unit test 的差別：什麼情況下測試全綠反而增加風險？」
2. 「我想審查一個限價撮合函數，請依照本文五步流程幫我設計 10 個反例輸入。」
3. 「我的測試斷言『超額委託量應回報 0 成交』，請用台股盤中零股規則判斷這條斷言是否合法。」

---
上一顆積木：[X00 脈絡](00-context.md)。下一顆：[X2 零股集合競價規則](02-oddlot-auction-twse-rules.md)。
