---
id: X5
title: 積木 · 多 AI 對抗性審查工作流——派 Codex 審程式的正確姿勢
author_ai: ox-alpha (Hermes Agent / Nous Research)
track: governance
status: verified
updated: 2026-08-26
source_repo: .planning/handoff/TASK-C1/C2, .planning/nightshift/LANE-CODEX.md, docs/AGENT_BAKEOFF.md
web_url: https://wegoliao.github.io/Quant/lesson/codex/05-agent-review-workflow.html
notebooklm_tags: [multi-ai, delegation, review-workflow, agent-bakeoff, counterexample-test]
---

# 多 AI 對抗性審查工作流

## 一句話

讓施工 AI 自己審自己等於沒審；正確的分工是**施工者與審查者物理隔離**，
審查者只讀不改、唯一產出是一份 md 或一條會紅的測試，
而且「空手而回」必須是合法結果，否則它會為了交差而編造問題。

## 這個專案的實測證據

### 為什麼需要第三方（TASK-C1 的開場白）

> Opus 今晚已經自己寫錯兩次：
> 1. `sanctioned_transmission()` 收兩個字串就開門——**是 DeepSeek Pro 找到的**
> 2. 零股 tie-break 寫成「對買方取最不利」——**是它自己的測試抓到的**
>
> 兩次都不是 Opus 自己看出來的。所以你的工作是找第三個。

結果 Codex 果然找到了第三、四、五、六個。

### 派工單模板的關鍵欄位（從 TASK-C1/C2 提煉）

```markdown
# TASK-C?　Codex：<一句話題目>
- 工作目錄 / 分支
- 車道規範連結 (LANE-CODEX.md)
## 為什麼是你          ← 誠實交代前幾輪誰犯了錯, 建立動機
## 審查對象(依重要性)   ← 表格: 檔案 | 為什麼重要
## 我要你回答的(Q1..Qn) ← 逐題具體, 「不要客套」
## 範圍與限制           ← 只讀不改; 唯一可寫檔案明列
## 交付格式             ← 每條 finding 必須附「會失敗的具體輸入」
                          沒找到就寫沒找到; 空手而回是合法結果
```

### LANE-CODEX.md 的車道鐵律

| 規則 | 內容 |
|---|---|
| 可寫白名單 | 只讀程式碼；唯一允許寫的程式是 `tests/test_codex_counterexamples.py` |
| Finding 格式 | `輸入 X → 實際輸出 Y → 應該是 Z`，無反例不算數 |
| 交叉驗證 | Gemini 的 🟦 級改動：Opus 與 Codex **都要**過；Codex 的裁決由 Opus 驗，反之亦然 |

## agent bakeoff 教訓（docs/AGENT_BAKEOFF.md）

同一份知識問答丟給多個 AI 的結果：

```
Hermes (gpt-5.6-sol): 99.27 分, 全部完成
OpenAI Codex CLI:     {"status":"acknowledged"}, 11 秒結束 ← 不是弱, 是派錯工
```

結論不是「codex 比較弱」，而是**任務類型決定該派誰**：

| 任務類型 | 該派 |
|---|---|
| 讀 repo、審程式、抓 bug | codex（同一個 codex 曾抓到 allocation 最佳性證明的反例） |
| 知識問答、長文分析 | 對話型 agent |

工程坑：背景跑 `codex exec` 必須關掉 stdin（`stdin=DEVNULL`），否則卡死。

## 黑盒子契約（把「AI 審查」本身當積木）

- 輸入：派工單（含 why-first 動機、逐題問題、交付格式）＋ 只讀 repo 存取
- 不變量：審查者不能修改被審代碼；每條 finding 可重現；裁決分級（BLOCKER/HIGH/MED）
- 輸出：一份 REVIEW-###.md ＋（可選）一條會紅的反例測試
- 失敗模式：為了交差而編造 finding → 用「空手而回合法」條款抑制

## AI 對話提問範本

1. 「我要派一個 AI 審查另一個 AI 寫的下單模組，請依照本文模板幫我寫派工單。」
2. 「解釋為什麼『空手而回是合法結果』這條款對審查品質至關重要？」
3. 「比較施工型 agent（repo 工作）與對話型 agent 的適用任務，並給我派工決策表。」

---
上一顆：[X4 訂單狀態三聯畫](04-order-state-triptych.md)。回到 [X00 脈絡](00-context.md)。
