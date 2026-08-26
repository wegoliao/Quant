# Quant Lesson · 模組化量化系統課程與黑盒子積木庫

[![Status](https://img.shields.io/badge/status-verified-brightgreen.svg)]()
[![Multi-AI](https://img.shields.io/badge/Multi--AI-Gemini%20%7C%20Claude%20%7C%20Codex-blue.svg)]()
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-orange.svg)](https://wegoliao.github.io/Quant/lesson/)

本倉庫收錄 Quant Grill Lab 中由各 AI（**Gemini**、**Claude**、**Codex** 等）共同沉澱之台股工程級量化系統知識、設計哲學與**可獨立拆裝的黑盒子積木庫（Building Blocks）**。

線上文件入口：[https://wegoliao.github.io/Quant/lesson/](https://wegoliao.github.io/Quant/lesson/)

---

## 目錄結構導引

- [`INDEX.md`](INDEX.md)：全站完整目錄與導引。
- [`_shared/`](_shared/)：跨 AI 通用規範、全域系統地圖與術語字典。
  - [`_shared/CROSS_AI_PROTOCOL.md`](_shared/CROSS_AI_PROTOCOL.md)：跨 AI 交互學習標準。
  - [`_shared/SYSTEM_MAP.md`](_shared/SYSTEM_MAP.md)：全系統五層架構地圖。
  - [`_shared/GLOSSARY.md`](_shared/GLOSSARY.md)：量化名詞與指標定義。
- [`gemini/`](gemini/)：**Gemini (Google DeepMind / Antigravity)** 貢獻之全套課程（G00~G06）與 10 大已驗證黑盒子積木（GB01~GB10）。
- [`claude/`](claude/)：**Claude (Anthropic)** 貢獻之實績觀察與成交簿對帳課程。

---

## 為什麼本教材適合 NotebookLM 與 AI 對話？

所有 Markdown 文件均遵循以下原則：
1. **結構化 Frontmatter**：包含清晰的 `author_ai`、`track` 與 `notebooklm_tags`。
2. **TL;DR 與數學嚴謹性**：每個模組開頭均有一句話摘要與精確公式。
3. **無黑盒子**：所有演算法均提供無外部黑箱依賴的最小可運行純 Python 代碼與單元測試。
4. **內建 AI Prompt**：每份文件末尾均提供現成提示詞，複製即可在對話中秒級總結。
