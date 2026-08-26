---
id: G02
title: 資料防偷看防禦 · FinLab 資料管線與 PIT 財報公告日對齊
author_ai: Gemini (Google DeepMind / Antigravity)
track: data
status: verified
updated: 2026-08-26
source_repo: https://github.com/wegoliao/Quant/tree/main/67.quant_lesson/lesson/gemini/
web_url: https://wegoliao.github.io/Quant/lesson/gemini/02-data-pit-and-leakage-defense.html
notebooklm_tags: [data, pit, point-in-time, lookahead-bias, finlab, leakage-defense]
---

# 資料防偷看防禦 · FinLab 資料管線與 PIT 財報公告日對齊

## 一句話總結 (TL;DR)

台股量化回測中最常見的「假聖杯」，90% 來自於**把未公開的資料當成已公開（Lookahead Bias）**。本章深度剖析月營收與季報的法定公告日延遲（Lag）、FinLab 中 `set_universe` 的全域進程污染陷阱，以及如何建構精確的 Point-in-Time (PIT) 防禦機制。

---

## 1. 致命陷阱一：月營收與季報的「時間標籤」陷阱

### 災難場景：
某策略在 5 月 1 日計算「4 月月營收成長率」並買進飆股。
- **回測結果**：年化報酬率 80%，Sharpe 3.5！
- **實盤死因**：台灣證交所規定，4 月份月營收是在 **5 月 10 日** 之前公佈。在 5 月 1 日~ 5 月 9 日這段時間，市場根本沒有人知道 4 月營收。回測程序利用了「未來營收」偷看答案！

```
【時間軸上的 Lookahead Bias 揭露】
4/30 (營收結算日) ──────── 5/01 (回測偷看買進❌) ──────── 5/10 (法定公告日⭕) ───> 5/11 (實盤最早可下單日)
```

### 季報公告延遲更嚴重：
- **Q1 財報**：法定截止日為 **5 月 15 日**（而非 3 月 31 日）。
- **Q2 財報**：法定截止日為 **8 月 14 日**（而非 6 月 30 日）。
- **Q3 財報**：法定截止日為 **11 月 14 日**（而非 9 月 30 日）。
- **Q4 財報（年報）**：法定截止日為 **次年 3 月 31 日**（而非 12 月 31 日）。

**鐵律**：任何以「財報涵蓋期截止日」作為索引的回測，都是徹底無效的垃圾回測。

---

## 2. 致命陷阱二：FinLab `data.set_universe()` 的全域進程污染

在大型多策略回測或多 Agent 協同環境中，曾發現一個極具隱蔽性的 Bug：
- 策略 A 為了研究中型股，呼叫了 `data.set_universe(["2330", "2317", ...])`。
- 這個呼叫直接修改了 Python 進程內部的全域 Universe 快取！
- 導致隨後執行的策略 B（原本應該在全市場 2,700 檔股票中選股）被強制縮限在策略 A 的子集裡，大盤標的（如 0050）與其他強勢股直接蒸發，導致回測數據完全失真。

### 解決方案：Scoped Context Manager（作用域還原）

在執行任何自訂 Universe 前，必須儲存舊狀態並在退出時自動還原：

```python
from contextlib import contextmanager
from finlab import data

@contextmanager
def scoped_universe(custom_universe: list[str]):
    """安全設定 Universe，退出 context 時自動還原全域快取。"""
    previous_universe = data.get_universe()
    try:
        data.set_universe(custom_universe)
        yield
    finally:
        data.set_universe(previous_universe)
```

---

## 3. PIT 對齊器積木實作

完整的 PIT 防偷看對齊模組請參閱 [`GB02 PIT 財報與營收防偷看對齊器`](blocks/GB02-pit-lag-aligner.md)。

核心原則：
1. **月營收**：一律對齊至次月 11 日的次一開盤日（Next Open）。
2. **季報**：一律依據實際申報公告日對齊，或強制加入 45 天 / 90 天的安全 Lag 緩衝區。
3. **宏觀指標 (PMI / CPI)**：嚴格依據國發會 / 主計總處的實際發布時間戳對齊，禁止以月份標籤對齊。

---

## 4. NotebookLM & AI 提問範本

- **提問範本 1**：「請解釋什麼是 Point-in-Time (PIT) 資料？如果量化系統沒有做好 PIT 對齊，會產生什麼樣的偽勝率？」
- **提問範本 2**：「為什麼 FinLab 的 `set_universe` 會造成全域污染？Gemini 是如何透過 contextmanager 解決這個問題的？」
