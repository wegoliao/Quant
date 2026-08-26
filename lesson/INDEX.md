---
id: ROOT-INDEX
title: Quant Lesson 跨 AI 模組化量化系統全課程索引
author_ai: Multi-AI System (Gemini & Claude & Codex)
track: shared
status: verified
updated: 2026-08-26
web_url: https://wegoliao.github.io/Quant/lesson/
notebooklm_tags: [index, catalog, quant-lessons, building-blocks, ai-navigation]
---

# Quant Lesson · 跨 AI 模組化量化系統全課程索引

歡迎來到 **Quant Grill Lab 模組化量化課程庫**。本站點專為 **人類學習、NotebookLM 知識庫匯入與跨 AI 交互對話** 所設計。

- **線上瀏覽網址**：[`https://wegoliao.github.io/Quant/lesson/`](https://wegoliao.github.io/Quant/lesson/)
- **GitHub 原始碼倉庫**：[`https://github.com/wegoliao/Quant/tree/main/lesson`](https://github.com/wegoliao/Quant/tree/main/lesson)

---

## 快速導航地圖

```
Quant Lesson (https://wegoliao.github.io/Quant/lesson/)
├── 🌐 _shared/ (跨 AI 共同協議與架構)
│   ├── CROSS_AI_PROTOCOL.md  ── 跨 AI 交互學習標準協議與積木設計規範
│   ├── SYSTEM_MAP.md         ── 全系統架構地圖與五層隔離資料流
│   └── GLOSSARY.md           ── 量化工程名詞、S編號與風控口徑對照表
│
├── 🧠 gemini/ (Gemini / Google DeepMind 貢獻軌道)
│   ├── 00-gemini-master-context.md        ── [G00] 總體脈絡：拆解黑盒子與工程級量化哲學
│   ├── 01-governance-and-fail-closed.md   ── [G01] 治理邊界、OS 排他鎖與三層隔離
│   ├── 02-data-pit-and-leakage-defense.md ── [G02] FinLab 資料管線、PIT 財報與營收 Lag 防偷看
│   ├── 03-tactics-and-integer-sizing.md   ── [G03] 進出場戰術、凸性整數規劃部位分配與勝率區間
│   ├── 04-microstructure-and-execution.md ── [G04] 委託簿微結構、ADV20 容量守門員與智慧追價
│   ├── 05-alpha-strategies-and-ga.md      ── [G05] 核心策略演化 (S138-S141) 與 50% CAGR GA 藍圖
│   ├── 06-validation-dsr-and-forward-sim.md ── [G06] 防過擬合鐵律：DSR 去膨脹與 Forward SIM 證據鏈
│   │
│   └── 🧱 blocks/ (Gemini 10 大獨立驗證黑盒子積木)
│       ├── GB01-research-lock.md          ── [GB01] 全域排他研究鎖 (OS-backed Lock)
│       ├── GB02-pit-lag-aligner.md        ── [GB02] PIT 財報營收防偷看對齊器
│       ├── GB03-integer-basket-allocator.md ── [GB03] 凸性整數規劃投組權重分配器
│       ├── GB04-adv-capacity-guard.md     ── [GB04] ADV20 流動性與容量守門員
│       ├── GB05-fee-floor-calculator.md   ── [GB05] 券商手續費低消與損益平衡計算器
│       ├── GB06-microstructure-matcher.md ── [GB06] 五檔微結構與衝擊成本評級器
│       ├── GB07-smart-requote-engine.md   ── [GB07] 限價智慧追價與重報價狀態機
│       ├── GB08-volatility-target-sizer.md── [GB08] 動態波動度目標部位調節器
│       ├── GB09-fcf-momentum-core.md      ── [GB09] 現金流營收動能因子選股核心
│       └── GB10-dsr-pbo-validator.md      ── [GB10] DSR / PBO 過擬合統計檢驗器
│
└── 🦅 claude/ (Claude / Anthropic 貢獻軌道)
    ├── 00-context.md                      ── [C00] 實績觀察、三種數字與主線一/二差集
    └── blocks/                            ── Claude 獨立積木庫 (FIFO對帳等)
```

---

## 如何在 NotebookLM 中匯入學習？

1. **一鍵建立筆記本**：在 Google NotebookLM 中建立名為「Quant Grill Lab 量化工程知識庫」的筆記本。
2. **加入來源**：
   - 方式 A：直接貼上本站網址（如 `https://wegoliao.github.io/Quant/lesson/gemini/00-gemini-master-context.html`）。
   - 方式 B：將本倉庫中的 `.md` 檔案直接批次上傳。
3. **對話提問建議**：
   - 「請為我整理 Gemini 提出的 10 大積木，並說明如何用它們組裝成一個完整的下單風控流。」
   - 「請比對 Claude 的主線二差集名單與 Gemini 的整數規劃部位分配，兩者在工程上如何協作？」
