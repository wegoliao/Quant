---
id: SHARED-MAP-01
title: 全系統架構地圖與資料流向導 (Quant Grill Lab System Map)
author_ai: Multi-AI Consensus (Gemini & Claude & Codex)
track: shared
status: verified
updated: 2026-08-26
web_url: https://wegoliao.github.io/Quant/lesson/_shared/SYSTEM_MAP.html
notebooklm_tags: [system-map, architecture, data-flow, quant-lab, pipeline]
---

# 全系統架構地圖與資料流向導 (System Map)

## 一句話總結 (TL;DR)

Quant Grill Lab 是一套貫徹「**研究、模擬、實盤三層物理隔離**」的台股工程級量化工作台。系統從資料端嚴格對齊 PIT，經過戰術整數分配與 ADV20 容量過濾，再交由微結構引擎產生限價訂單，並由獨立的對帳線進行滑價校準。

---

## 1. 全系統三層物理隔離架構圖

```mermaid
flowchart TB
    subgraph DataLayer ["1. 資料與防偷看層 (Data & PIT Engine)"]
        FinLabDB[("FinLab Local Cache<br/>(finlab_db)")]
        PITAligner["PIT Aligner & Lag Guard<br/>(GB02 / 財報公告日對齊)"]
        FinLabDB --> PITAligner
    end

    subgraph ResearchLane ["2. 研究與策略演化層 (Research Lane - Upload=False)"]
        RLock["OS-backed Research Lock<br/>(GB01 / 排他防衝突鎖)"]
        StratPool["策略候選池 (S001~S143)<br/>(FCF動能/反向波動/Radical GA)"]
        DSRVal["DSR / PBO / Plateau 驗證<br/>(GB10 / 防過擬合堡壘)"]
        
        RLock --> StratPool
        PITAligner --> StratPool
        StratPool --> DSRVal
    end

    subgraph TacticsLane ["3. 戰術與部位定價層 (Tactics & Sizing Engine)"]
        ContextFilter["Entry Context<br/>(趨勢與隔夜跳空濾網)"]
        IntAlloc["Integer Basket Allocator<br/>(GB03 / 凸性 L1 整數規劃)"]
        CapGuard["ADV20 Capacity Guard<br/>(GB04 / 2%~5% 流動性守門員)"]
        FeeFloor["Fee Floor Calculator<br/>(GB05 / 低消 NT$20 損益平衡)"]
        
        DSRVal -->|Approved Candidates| ContextFilter
        ContextFilter --> IntAlloc
        IntAlloc --> CapGuard
        CapGuard --> FeeFloor
    end

    subgraph ExecutionLane ["4. 實盤微結構與執行層 (Execution Lane - Gated)"]
        MSMatcher["Microstructure Matcher<br/>(GB06 / 五檔深度與衝擊評級)"]
        RequoteSM["Smart Requote Engine<br/>(GB07 / 追價狀態機)"]
        OwnerKey["Owner Two-Key Verification<br/>(雙重確認 / AI 絕對禁觸)"]
        BrokerAPI["SinoPac Shioaji API<br/>(券商委託管道)"]
        
        FeeFloor --> MSMatcher
        MSMatcher --> RequoteSM
        RequoteSM --> OwnerKey
        OwnerKey -->|Owner Manual Action| BrokerAPI
    end

    subgraph ReconciliationLane ["5. 實績與滑價對帳層 (Reconciliation Lane)"]
        ActualFills["實際成交簿 (actual_fills.csv)"]
        E5Slippage["E5 Slippage Model<br/>(未滿 30 筆前標記 UNVALIDATED)"]
        Mainline2["主線二差集觀察名單"]
        
        BrokerAPI -.-> ActualFills
        ActualFills --> E5Slippage
        ActualFills --> Mainline2
    end
```

---

## 2. 各層核心職責與積木對應表

| 層級 | 核心職責 | 關鍵輸入 | 關鍵輸出 | 對應積木 |
|---|---|---|---|---|
| **1. 資料層** | PIT 財報發布日對齊、營收公佈日遞延、全域資料隔離 | FinLab Raw DB | 防偷看的 Clean Dataframe | `GB02` |
| **2. 研究層** | 候選策略生成、反向波動加權、多因子 GA 搜尋、DSR 去膨脹 | Clean Data | 策略訊號與通過 DSR 門檻之候選池 | `GB01`, `GB08`, `GB09`, `GB10` |
| **3. 戰術層** | 帳戶真實可用現金轉換為整數張數/零股、ADV20 流動性檢查、手續費低消過濾 | 策略權重 + 帳戶現金 | 具體每檔欲買進之整數股數 (Notional) | `GB03`, `GB04`, `GB05` |
| **4. 執行層** | 五檔盤口微結構判定、TWAP/VWAP 拆單、限價智慧追價狀態機 | 即時報價 + 整數委託意圖 | 格式化之券商下單合約（待 Owner 手動確認） | `GB06`, `GB07` |
| **5. 對帳層** | 券商成交回報匯入、先進先出 (FIFO) 實踐損益計算、E5 滑價模型校準 | 券商成交明細 CSV | 實踐報酬率、真實滑價分佈、主線二名單 | `Claude C00`, `B01` |

---

## 3. NotebookLM 快速導引

- **提問範本 1**：「請根據 System Map 說明，一筆策略訊號從產生到最終被送往券商，中間經過了哪五道風控關卡？」
- **提問範本 2**：「為什麼 Quant Grill Lab 堅持在第 4 層加入 Owner Two-Key Verification，而不讓 AI 全自動送單？」
