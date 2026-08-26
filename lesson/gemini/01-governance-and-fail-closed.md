---
id: G01
title: 治理邊界、排他研究鎖與 Fail-Closed 防禦架構
author_ai: Gemini (Google DeepMind / Antigravity)
track: governance
status: verified
updated: 2026-08-26
source_repo: https://github.com/wegoliao/Quant/tree/main/67.quant_lesson/lesson/gemini/
web_url: https://wegoliao.github.io/Quant/lesson/gemini/01-governance-and-fail-closed.html
notebooklm_tags: [governance, research-lock, fail-closed, security, permissions]
---

# 治理邊界、排他研究鎖與 Fail-Closed 防禦架構

## 一句話總結 (TL;DR)

在多 Agent、多腳本並發的量化環境中，任何未加鎖的寫入都會導致回測數據污染或網站生成崩潰；而在交易執行路徑上，任何不確定的狀態都必須**防禦性關閉（Fail-Closed）**。本章闡述全域排他鎖 `RESEARCH_LOCK.json` 的設計與三層物理隔離治理鐵律。

---

## 1. 為什麼需要全域排他研究鎖？

在過去的探索中（如 Codex G070~G075 階段），曾發生過數次重大事故：
- **並發寫入衝突**：一個 Agent 正在執行 81 支策略的全量回測，另一個 Agent 同時向 `registry` 寫入新策略，導致正在產出的指標快照與策略清單不一致，整站重建被 fail-closed 終止，浪費數十分鐘運算。
- **孤兒鎖死鎖**：某些回測腳本因例外崩潰退出，留下了未釋放的鎖，導致後續所有研究流程全部卡死。

### 解決方案：OS 級全域研究鎖 (`RESEARCH_LOCK.json`)

```
                          【全域研究鎖運作狀態機】
                              ┌─────────────┐
                              │    IDLE     │
                              └──────┬──────┘
                   acquire_lock()    │  檢查心跳 < 15 分鐘
                                     ▼
        ┌────────────────────────────────────────────────────────┐
        │  鎖定狀態 (OFFICIAL_SIM / REGISTRY_WRITE / SITE_BUILD) │
        │  記錄: pid, holder, acquired_at, heartbeat_at, scope   │
        └────────────────────────────┬───────────────────────────┘
                 release_lock()      │  崩潰或逾時 > 15 分鐘
                                     ▼
                              ┌─────────────┐
                              │ 釋放 / 回收  │
                              └─────────────┘
```

鎖包含三種互斥類型：
1. `OFFICIAL_SIM`：執行官方基準回測時鎖定，防止策略代碼被篡改。
2. `REGISTRY_WRITE`：註冊新策略或修改參數時鎖定，防止回測讀到半成品。
3. `SITE_BUILD`：編譯生成首頁與報表時鎖定，確保讀取一致的快照。

---

## 2. 治理邊界三大鐵律 (Three Hard Boundaries)

### 鐵律一：Research / SIM / Execution 嚴格隔離
- **研究層 (Research Lane)**：`upload=False`，使用本機 `finlab_db`，不載入券商 SDK，無權限讀取帳戶與憑證。
- **券商模組隔離**：`shioaji` **只能在 `src/quant_grill_lab/execution/` 中被引用**，任何在策略、研究或筆記本中引用券商 SDK 的行為均被 CI 自動阻擋。

### 鐵律二：AI 絕對無權下單 (No Autonomous Real Orders)
- 自然語言輸出的 AI 永遠不具備傳送真實訂單的授權。
- 下單腳本必須具備 **Owner 雙重手動確認（Two-Key Verification）**，包含指紋校驗（Fingerprint）與短效一次性授權（Single-Use Auth）。AI 只能產出訂單意圖（Order Proposal），按下發送按鈕永遠是人類的事。

### 鐵律三：防禦性關閉 (Fail-Closed)
- 當遇見 `UNKNOWN`、`PENDING`、`PARTIAL_FILL` 或資料缺失時，系統**絕對不自動猜測或重試**，而是立即停止操作並通知人類，避免在異常盤口中重複送單導致巨額虧損。

---

## 3. 核心積木與代碼實作

完整獨立可運行的研究鎖實作請參閱 [`GB01 全域排他研究鎖`](blocks/GB01-research-lock.md)。

### 常用命令列操作：
```powershell
# 1. 查詢當前研究鎖狀態
.\.venv\Scripts\python.exe scripts\research_lock.py status

# 2. 在鎖保護下安全執行官方回測
.\.venv\Scripts\python.exe scripts\research_lock.py run `
  --kind OFFICIAL_SIM --holder "Gemini" --scope "S138-S141 Verification" -- `
  pytest tests/test_strategy_signals_gate.py
```

---

## 4. NotebookLM & AI 提問範本

- **提問範本 1**：「請總結為什麼本系統堅持禁止 AI 自主向券商 API 送單？背後的風險模型是什麼？」
- **提問範本 2**：「如果一個回測腳本在持有 `OFFICIAL_SIM` 鎖時意外被中斷，系統是如何透過心跳機制（Heartbeat）避免死鎖的？」
