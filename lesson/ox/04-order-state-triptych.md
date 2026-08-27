---
id: X4
title: 積木 · 訂單狀態三聯畫——一個 enum 裝不下「成交＋取消失敗＋還活著」
author_ai: ox-alpha (Hermes Agent / Nous Research)
track: execution
status: verified
updated: 2026-08-26
source_repo: src/quant_grill_lab/execution/order_events.py + proposal_submit.py + REVIEW-005 S2/S3/E1–E3
web_url: https://wegoliao.github.io/Quant/lesson/ox/04-order-state-triptych.html
notebooklm_tags: [state-machine, order-lifecycle, dedup, journal, shioaji, deal-matching]
---

# 訂單狀態三聯畫：把三種狀態壓成一個 enum 的代價

## 一句話

「送單嘗試」「訂單生命週期」「命令結果」是三個正交維度；
把它們塞進同一個 `status` enum 會同時產生兩個方向相反、都會賠錢的錯誤——
沒送出的單顯示已送出（漏單），取消失敗的活單顯示已拒絕（雙倍曝險）。

## 痛點：兩個真實重現的錯

```
錯誤 1 (S2): 批次第 2 筆 timeout, 第 3 筆根本沒嘗試
             → 卻停留在 SENT, 無 order id / sent_at
             → owner 怕重複單而不補 → 漏單

錯誤 2 (E2): 原單已 ACK 活著, Cancel 回報 op_code=88 失敗
             → 狀態被改成 REJECTED
             → owner 以為結束了再下一張 → 原單還在市場上 = 雙倍部位
```

## 黑盒子解構：三聯畫模型

```
┌─────────────────────────┬──────────────────────────────┬──────────────────────┐
│ submission_state        │ lifecycle_state              │ last_command         │
│ (我的嘗試)              │ (券商那邊的單)                │ (我發出的指令)        │
├─────────────────────────┼──────────────────────────────┼──────────────────────┤
│ NOT_ATTEMPTED           │ PENDING_ACK                  │ {type: NEW|CANCEL|   │
│ ATTEMPTING              │ LIVE                         │  UPDATE,             │
│ SENT                    │ PARTIAL                      │  outcome: OK|FAILED, │
│ UNKNOWN                 │ FILLED                       │  op_code, message}   │
│ (初始值=NOT_ATTEMPTED!) │ CANCELLED                    │                      │
│                         │ NEW_REJECTED                 │                      │
└─────────────────────────┴──────────────────────────────┴──────────────────────┘
規則: New 失敗才可令 order NEW_REJECTED;
      Cancel/Update 失敗只記 last_command.FAILED, lifecycle 保持 LIVE/PARTIAL。
真實終態範例: SENT + PARTIAL(2000股) + {CANCEL, FAILED} —— 單一 enum 表達不了這個。
```

## 成交回報對帳（Finding E1：所有真實成交可能都 unmatched）

Shioaji 官方回報形狀：

```
下單 ack:    order.id = "892f730b"
成交 Deal:   trade_id = "9c6ae2eb"   ← 是另一個值!
             另帶 seqno / ordno       ← 這才是關聯原單的正確鍵
             exchange_seq              ← 成交事件的冪等 id
```

原實作把 `trade_id` 當 `broker_order_id` 對帳 → 官方示例重現：
成交 2 張仍停在 `SENT, filled=0`。修法：

```python
# ack 時保存三鍵
ack_keys = {"id": order.id, "seqno": s.seqno, "ordno": s.ordno}
# deal 用 seqno/ordno 找原單; exchange_seq 只做事件冪等
line = book.find_by(seqno=deal.seqno, ordno=deal.ordno)
if not book.seen(deal.exchange_seq):
    apply(line, deal); book.commit_id(deal.exchange_seq)   # 先驗後記
```

## 冪等與 journal（E3/S3）

- **先驗後記**：deal id 在 `_apply_deal()` 成功 commit 後才原子記入 set。
  順序反了，第一份同 seq 的壞事件 raise 後，修正重播會被當 duplicate 丟掉
  （Codex 實測：錯誤 6 張 raise 後，正確 5 張被忽略，filled=0）
- **durable journal**：broker call 前寫 `ATTEMPT`，返回後寫 `RETURNED/SENT`，
  例外寫 `UNKNOWN`。斷電恢復時先 reconcile，禁止整批重送
  （最危險窗口：`place_order()` 已到券商但尚未 `mark_sent()`）

## 契約不變量

1. 未嘗試的 line 初始即為 `NOT_ATTEMPTED`，只有 broker call 返回後才可 `mark_sent`
2. 三個維度各自獨立轉移，互不覆寫
3. 弱鍵（無 exchange_seq 時）只能標 ambiguity 觸發人工對帳，不能宣稱唯一
4. 失敗事件進 quarantine journal，不污染 applied-id set

## AI 對話提問範本

1. 「解釋訂單系統中 submission/lifecycle/command 三個狀態維度為何必須正交，並舉一個單 enum 無法表達的終態。」
2. 「設計一個 broker 成交回報的去重機制：exchange_seq、seqno/ordno、弱鍵各扮演什麼角色？」
3. 「我的批次下單在中途 crash 後如何安全恢復？請給出 journal 的欄位設計與 reconcile 流程。」

---
上一顆：[X3 驗證鏈偽造](03-auth-chain-forgery.md)。下一顆：[X5 多 AI 審查工作流](05-agent-review-workflow.md)。
