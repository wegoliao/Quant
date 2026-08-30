# lesson/codex · 完整合輯

作者 AI：**OpenAI Codex**　·　檔案 16 份　·　產生於 2026-08-31

這份檔案把整個目錄串成一份，給只能吃一個 URL 的 AI 用。
每一節開頭的 `## [id] title` 對應一個獨立檔案，可以單獨抽走使用。

---

## [CDX00] OpenAI Codex 全景脈絡 · 從綠地實驗室到雙主線量化系統

*track: context · status: verified · verified_by: D:/Quant_Grill_Lab/README.md + AGENTS.md + .planning/GRILL_DECISIONS.md + current source tree · source: lesson/codex/00-context.md*

# OpenAI Codex 在 Quant Grill Lab 做了什麼

## 一句話

Codex 把一個「想找到高 Sharpe 策略」的模糊願望，逐步變成一套會拒絕自欺的量化研發系統：研究與 broker 執行分離、每個數字要有證據、每個跨線輸出要有契約、任何不確定都用具名 `HOLD` 或 `WAITING_*` 停下來。

## 系統演化脈絡

| 階段 | 真正解決的問題 | 產出形態 |
|---|---|---|
| 綠地隔離 | 不再依賴舊 repo 的髒工作樹與隱性選擇 | 獨立 Git、獨立 `.venv`、獨立治理決策 |
| 研究骨架 | 策略不能只有一張漂亮回測圖 | deterministic runner、成本、容量、IS/OOS、receipt |
| 研究治理 | 大量搜尋會把雜訊誤認成 alpha | 預註冊、trial count、DSR/PBO、PWF、plateau、HOLD/KILL |
| 雙主線 | 研究目標與真實部位不能混成一個物件 | Mainline 1 / Mainline 2 + `TargetPortfolioSnapshot` seam |
| Owner 執行 | AI 可以準備，但不能授權真實送單 | `OrderProposal -> HumanApproval -> requote -> callbacks -> reconciliation` |
| 可觀察性 | 舊 receipt、舊 HTML、局部測試不能冒充現況 | code/hash/data_asof/run_at/status 的證據階層 |

## 兩條主線不是兩套重複系統

```text
Mainline 1：資料 -> 假說 -> position -> backtest -> 驗證 -> Champion/目標快照
                                            |
                                            v
                              TargetPortfolioSnapshot
                                            |
                                            v
Mainline 2：intake -> 真實部位差額 -> sizing -> OrderProposal -> owner gate -> 對帳
```

Mainline 1 不知道帳戶、股數、五檔或 broker；Mainline 2 不可以偷偷重選策略。兩邊只透過一個去 broker 化、可雜湊、可檢查 freshness 的快照交接。

## Codex 的主要角色

1. **治理翻譯器**：把 owner 的自然語言目標轉成可驗收決策與具名失敗狀態。
2. **實作工程師**：建立研究 runner、策略生命週期、SIM、notebook、owner console 與執行安全模組。
3. **對抗性稽核者**：不信「測試全綠」或 AI 自報完成，回到 source、fixture、receipt 與重跑結果。
4. **系統整合者**：把資料、研究、組合、執行、觀察與對帳接成單向證據鏈。
5. **止損守門員**：證據不足時輸出 `HOLD`、`NO-GO`、`WAITING_*`、`UNVALIDATED`，不拿真錢填補未知。

## 怎麼讀這個目錄

- 想理解「為什麼不能信一張回測圖」：讀 `01-evidence-hierarchy` 與 `03-validation-gates`。
- 想理解「研究如何接到執行」：讀 `02-research-mainline`、`04-target-snapshot-handoff`。
- 想理解「AI 為什麼不能送單」：讀 `05-execution-safety-chain`。
- 想把黑盒子變成積木：直接讀 `blocks/`，每篇都有 interface、輸入、輸出、不變量與失敗狀態。

## 目前誠實狀態

這套系統有大量可用模組，但不等於有可真錢運行的完整系統。最後一次完整盤點仍是：研究 Champion 證據口徑衝突，主線一 `HOLD_RESEARCH_ONLY_NO_PROMOTION`；主線二部分能力存在，但整合仍 `NO-GO REAL`。任何新報告都必須重新以當前 source、tests、hash 與 receipt 驗證，不能沿用這句話當永久現況。

---

## [CDX01] 證據階層 · 為什麼檔案存在、測試通過與研究結論是三件事

*track: validation · status: verified · verified_by: D:/Quant_Grill_Lab/deliverables/notebooklm_quant_playbook/06_LATEST_DUAL_MAINLINES_AND_FINLAB_CURRICULUM.md section 6 · source: lesson/codex/01-evidence-hierarchy.md*

# 證據階層

## 核心問題

量化專案最常見的假完成，不是程式完全沒寫，而是把不同強度的證據混成一句「完成了」。

```text
強  當前 checkout 的可重跑 code + focused/full tests + hash + 新 receipt
 |  當次原始 evidence（metrics JSON、equity CSV、broker callback ledger）
 |  根據原始 evidence 產生的報告
弱  handoff、prompt、白皮書、舊截圖、AI 自述
```

## 三個容易混淆的命題

| 命題 | 它只證明什麼 | 不能推出什麼 |
|---|---|---|
| 檔案存在 | 有人曾寫過這個 artifact | 程式可跑、數字仍新鮮 |
| focused tests 綠 | 被選中的行為符合斷言 | 全庫整合、資料正確、真實市場可成交 |
| 報告寫 PASS | 報告作者做出該判斷 | 來源、參數、資料、trial count 都一致 |

## 一份可用證據的最小 interface

```yaml
run_at: 產生時間
data_asof: 每個資料源真正涵蓋到何時
code_hash: 執行版本
config_hash: 參數版本
data_hash: 輸入資料版本
command: 可重跑入口
status: SUCCESS | HOLD_* | WAITING_* | FAILED_*
checks: 每一關的具名結果
artifacts: metrics / equity / report / receipt
```

## 關鍵不變量

1. `run_at` 不能冒充 `data_asof`。
2. 舊 receipt 不能證明本次命令成功。
3. HTML 是呈現 adapter，不是數字的 source of truth。
4. 沒有原始 input/hash 的報告只能當線索。
5. 缺資料必須變成狀態，不能默默補 0、前值或理論價。

## 組裝方式

這個積木位於所有模組之上：策略 backtest、Champion、目標快照、OrderProposal、dashboard 都必須附證據包。沒有證據包的輸出，可以看，但不可升格。

---

## [CDX02] 主線一 · 從 FinLab 資料到可否證的策略候選

*track: research · status: verified · verified_by: D:/Quant_Grill_Lab/src/quant_grill_lab/strategy_selection + experiment_lifecycle.py · source: lesson/codex/02-research-mainline.md*

# 主線一：研究不是「找最高 Sharpe」

## Interface

```text
輸入：有時間語意的資料、預註冊假說、參數空間、成本/容量假設、benchmark
輸出：position、官方 SIM evidence bundle、驗證裁決、候選/Champion receipt
權限：只能研究與產生唯讀 target；不能讀帳戶、不能建立委託
```

## 標準流水線

1. **資料可用性**：先確認欄位、歷史長度、公告日與 refresh 狀態。
2. **假說轉 position**：因子只描述為什麼選；position 才是可回測契約。
3. **官方 SIM**：`upload=False`，保存 metrics、equity、HTML、receipt 與 hash。
4. **成本與可成交性**：費率、稅、滑價、換手、流動性、整股/零股、容量。
5. **抗過擬合**：IS/OOS、purged walk-forward、plateau、trial count、DSR/PBO。
6. **組合價值**：和 benchmark、既有策略的相關、邊際 Sharpe、容量一起看。
7. **裁決**：`PROMOTE`、`HOLD` 或 `KILL`；沒有通過者是合法結果。

## 研究模組真正隱藏的複雜度

深 module 的 interface 應該只讓研究者交付「假說 + position + preregistration」。資料對齊、成本、切分、報告、hash、receipt 由 implementation 統一處理，避免每支策略各自偷換口徑。

## 失敗狀態

- `HOLD_DATA_INSUFFICIENT`：歷史、欄位或 PIT 語意不足。
- `HOLD_RESEARCH_ONLY_NO_PROMOTION`：能研究但不能升格。
- `KILL_OVERFIT`：trial/plateau/PWF 顯示不穩健。
- `KILL_CAPACITY`：績效高但資金規模無法實現。
- `UNVALIDATED_CONFLICT`：不同 runner 或報告對同一關得出矛盾。

## 不可跨越的 seam

主線一最多輸出 `TargetPortfolioSnapshot`。`Champion`、`PROMOTE` 或高 Sharpe 都不是訂單授權。

---

## [CDX03] 研究驗證堆疊 · 一支策略要過哪些關才不是漂亮雜訊

*track: validation · status: verified · verified_by: D:/Quant_Grill_Lab/deliverables/notebooklm_quant_playbook/02_RULES_WHAT_WENT_WRONG.md + 03_HOW_TO_DEVELOP.md · source: lesson/codex/03-validation-gates.md*

# 研究驗證堆疊

## Gate 不是分數加總

硬 gate 是 AND，不是平均：任何一關失敗都不能用另一個漂亮指標抵銷。

| Gate | 要回答的問題 | 常見造假方式 |
|---|---|---|
| 資料時點 | 當天真的知道這個值嗎 | 用現在分類套全歷史、先 ffill 再 rank |
| 成交語意 | 訊號後何時、什麼價能成交 | same-bar、close 訊號又用 close 成交 |
| 摩擦 | 報酬扣掉費稅與滑價後還剩多少 | 費用比例有寫但沒進 equity |
| OOS/PWF | 換期間與 regime 還活著嗎 | 只做一次 50/50 切分 |
| 多重嘗試 | 是最好的一次運氣嗎 | 不記 trial count、DSR 參數傳錯 |
| 參數高原 | 鄰近參數也有效嗎 | 只有一個尖峰 |
| 流動性容量 | 真實資金能不能部署 | 只報平均成交量，不報持倉權重與退出天數 |
| 組合邊際 | 新策略真的帶來新風險來源嗎 | 六支高度相關策略當成六條腿 |

## 建議裁決資料結構

```yaml
strategy_id: Sxxx
gates:
  pit: PASS | HOLD | KILL
  costs: PASS | HOLD | KILL
  pwf: PASS | HOLD | KILL
  multiple_testing: PASS | HOLD | KILL
  plateau: PASS | HOLD | KILL
  capacity: PASS | HOLD | KILL
verdict: PROMOTE | HOLD | KILL
reasons: [具名、可重跑]
```

## 關鍵問題寫法

不要問「這支策略好不好？」；要問：

> 在固定資料截止日、已登記 trial count、完整成本與相同 runner 下，這支策略的 full/IS/OOS/PWF、MDD、Calmar、capacity、plateau 與既有策略相關是多少？任何 gate 缺證據時回傳哪個 HOLD？

---

## [CDX04] 雙主線 seam · TargetPortfolioSnapshot 為什麼是唯一合法交接

*track: architecture · status: verified · verified_by: 2026-08-27 focused pytest 95 passed; includes target snapshot, handoff, approval, requote, settlement · source: lesson/codex/04-target-snapshot-handoff.md*

# TargetPortfolioSnapshot：研究與執行的 seam

## 為什麼不能直接傳「買哪些股票」

自然語言清單缺少版本、來源、時點、權重總和與 hash；執行端無法判斷它是新訊號、舊訊號、另一支 Champion，還是被人工改過的檔案。

## Interface

```text
TargetPortfolioSnapshot
├─ snapshot/champion/version/hash
├─ generated_at / data_asof / validity
├─ target positions：symbol + target_weight + attribution
├─ research evidence reference
└─ 明確排除：account、cash、shares、market quote、broker object
```

## Intake Gate

執行端收到快照後先檢查：

1. schema/version 可接受；
2. snapshot hash 與內容一致；
3. Champion/implementation hash 沒漂移；
4. `data_asof` 與有效期限未過；
5. 權重有限、非負、總和符合契約；
6. attribution 完整；
7. 沒有 broker/account 欄位滲入。

全通過只得到 `READY_FOR_DRAFT`，意思是「允許計算差額並產生提案草稿」，不是 `READY_FOR_REAL`。

## 深 module 的價值

這個 seam 讓研究 implementation 可以換 FinLab、其他資料源或不同策略族，而執行端只學一個 interface。反過來，broker、股數、盤別與 approval 的變更也不污染研究。

---

## [CDX05] 主線二 · Owner-gated execution 安全鏈

*track: execution · status: verified · verified_by: 2026-08-27 focused pytest 95 passed; full-repo and REAL remain explicitly unvalidated · source: lesson/codex/05-execution-safety-chain.md*

# 主線二：把目標變成可審查提案，不是讓 AI 下單

## 安全鏈

```text
Target Intake
  -> holdings / unfilled / net gap
  -> integer sizing + lot lane + costs + capacity
  -> OrderProposal (immutable hash)
  -> Owner read-back
  -> hardware-backed approval bound to batch/purpose/mode/expiry
  -> fresh requote and material-change check
  -> single-use consumption
  -> controlled transmit
  -> order/deal callbacks
  -> immutable reconciliation
```

## 每一段的權限

| 段 | 可以做 | 不可以做 |
|---|---|---|
| 計算 | 算 gap、股數、費用、價界 | 建立 broker order |
| 提案 | 顯示每筆與總額、hash、風險 | 當成 owner 同意 |
| 核准 | owner 對明確 batch 做硬體簽核 | 用文字「我同意」代替 |
| requote | 更新行情、檢查 material change | 偷改已核准內容 |
| transmit | owner 最後操作的受控 seam | AI 執行真實送單 |
| callback | 記錄 broker 真正接受/成交 | 用函式回傳值冒充成交 |
| reconciliation | 對 target/proposal/order/deal/position | 猜測缺少的 fill 或 fee |

## 三個必要不變量

1. Natural-language AI output 永遠不能 arm、approve、amend、cancel 或 transmit。
2. 任何價格、股數、總額、筆數或 batch hash 的重大變動都使 approval 失效。
3. 在真實 fills 尚未校準滑價模型前，預測成交價必須顯示 `UNVALIDATED`。

## 目前狀態

主線二有許多已測 module，但完整系統仍需以當前 checkout 重跑整合測試、broker callback fixture 與 reconciliation；局部綠燈不是 REAL readiness。

---

## [CDX06] 日常營運 · 用 receipt 與具名等待狀態取代「應該有跑」

*track: operations · status: verified · verified_by: D:/Quant_Grill_Lab/src/quant_grill_lab/daily + notebook_runtime.py + scripts/verify_finlab_runtime.py · source: lesson/codex/06-operational-receipts.md*

# 日常營運不是按 Run All 就算完成

## 一次正式 run 應該留下什麼

```text
command + interpreter/kernel
run_at + source-specific data_asof
config/code/data hashes
input inventory
named checks
output artifacts
terminal status
```

## 具名狀態的用途

- `WAITING_DATA`：輸入沒有更新到契約要求的時點。
- `WAITING_OWNER_BROKER_EVIDENCE`：需要 owner 提供的只讀 broker artifact。
- `SKIP_BUSY`：環境正被 kernel 使用；這不是更新成功。
- `SKIP_LOCK_HELD`：另一個正式研究流程持有 OS lock。
- `FAILED_WRITE_RECEIPT`：工作可能跑過，但證據沒有原子落地，仍算失敗。
- `NO_UPDATE`：只有本次所有健康檢查為零且新 receipt 寫入才算成功。

## Notebook 安全契約

可交付 notebook 應可重跑、固定 kernel、沒有秘密、沒有 saved outputs；任何 REAL 控制預設 `false`。AI 不填 credentials、不啟用 REAL switch、不執行 owner 最後動作 cell。

## 為什麼這也是量化 alpha 的一部分

如果每日資料、版本、訊號、成交與報告無法重現，你無法判斷績效來自策略、資料漂移、執行落差或人工作業。營運 receipt 是研究可證偽性的延伸。

---

## [CDX07] 問題寫法 · 用 AI 拆黑盒子、驗證積木與組裝系統

*track: prompts · status: verified · verified_by: D:/Quant_Grill_Lab/deliverables/notebooklm_quant_playbook/06_LATEST_DUAL_MAINLINES_AND_FINLAB_CURRICULUM.md sections 7-9 · source: lesson/codex/07-learning-and-prompts.md*

# 問題寫法：不要問「解釋這個系統」

## 建立全貌

> 請把系統拆成資料、研究、驗證、組合、handoff、執行、對帳七層。每層列出 owner、輸入、輸出、interface、不變量、權限、HOLD 狀態，以及下游如何使用。

## 拆一個黑盒子

> 針對 `TargetPortfolioSnapshot`，列出它隱藏的 implementation、對 caller 暴露的最小 interface、禁止欄位、hash/freshness 規則、所有 fail-closed 狀態與一個最小正反例。

## 驗證一個積木

> 不採信文件的 `verified` 標籤。找出直接 source、測試、fixture、最近 receipt 與 hash；執行最小可重跑驗證。若缺任何一項，輸出 `UNVALIDATED` 並列出缺口。

## 組裝積木

> 我要從研究候選組成 paper-SIM 流程。請只使用已確認積木，畫出資料流與每個 seam，列出 ordering constraints；任何需要 REAL、credentials 或 owner action 的步驟停止並回傳具名等待狀態。

## 反自欺口試

> 扮演對抗性審查者。逐項挑戰 PIT、same-bar、成本、滑價、流動性、capacity、trial count、IS/OOS、PWF、regime、benchmark、correlation 與 forward evidence。每個 finding 必須附可重跑反例或明確缺少的證據。

## 比較不同 AI

> 比較 `lesson/claude`、`lesson/gemini`、`lesson/codex`、`lesson/ox` 對同一主題的 interface、不變量與證據。不要投票；以可重跑證據決定，無法決定時保留具名分歧。

---

## [CDX08] 未解問題地圖 · 下一步不是再堆功能，而是關閉證據缺口

*track: traps · status: verified · verified_by: D:/Quant_Grill_Lab/deliverables/notebooklm_quant_playbook/06_LATEST_DUAL_MAINLINES_AND_FINLAB_CURRICULUM.md · source: lesson/codex/08-open-problems.md*

# 未解問題地圖

## 研究線

1. 不同報告對 PWF 定義與結果有衝突；需固定同一 runner、split、embargo 與 trial ledger 重跑。
2. 高 Sharpe/高 CAGR 候選仍需 pristine OOS 與未來 observation；不能用已看過的資料補回去。
3. 產業分類、財報公告日、停利 OHLC semantics 等仍有 PIT/前視風險。
4. capacity 必須用實際權重、成交量、持有期與退出天數，不是單一平均量門檻。

## 雙主線 seam

1. 正式 `ACTIVE_CHAMPION` 與版本化 `TargetPortfolioSnapshot` 尚需一致證據。
2. intake 綠燈只到 `READY_FOR_DRAFT`；不能用 demo snapshot 冒充正式交接。
3. 研究 attribution 與 execution sleeve attribution 必須能一對一對帳。

## 執行線

1. predicted fill/slippage 尚未用足夠真實 fills 校準，維持 `UNVALIDATED`。
2. callback、cancel/reject/partial fill、普通/零股 lane 的狀態需要完整 reconciliation coverage。
3. Owner approval、requote、single-use consumption 與 transmit 必須整體驗證，不能只看單 module。

## 營運與教材

1. 主 repo 工作樹有大量並行變更；任何現況盤點都要鎖定時間與 commit/hash。
2. 本 lesson 內其他 AI 的 `verified` 標籤若沒有 `verified_by`，建置器會降為 `unvalidated`。
3. OX 與 GLM-5.3 應各自對本課程提出至少一個可證偽分歧，而不是重寫相同摘要。

## 最有價值的往下推

先完成「同一 runner 的研究真相表」與「正式 snapshot 到 reconciliation 的 dry-run evidence chain」，再增加新策略或新 UI。這兩條能把大量文件變成可驗收系統。

---

## [CB01] 積木 · EvidenceBundle 可重跑證據包

*track: block · status: verified · verified_by: D:/Quant_Grill_Lab/src/quant_grill_lab/experiment_lifecycle.py · source: lesson/codex/blocks/CB01-evidence-bundle.md*

# EvidenceBundle

## Interface

```python
EvidenceBundle(
    run_at, data_asof, command, interpreter,
    code_hash, config_hash, data_hash,
    checks, artifacts, terminal_status,
)
```

## 輸入

實際執行環境、資料截止日、設定、所有 gate 結果與輸出檔案索引。

## 輸出

一個可序列化、可雜湊、能回答「誰、何時、用什麼資料與程式得到什麼狀態」的 receipt。

## 不變量

- `run_at` 與 `data_asof` 分開。
- terminal status 非成功時不能只保留最後漂亮 artifact。
- artifact 必須能回到 hash/input；HTML 不能是唯一數字來源。
- 原子寫入失敗即 `FAILED_WRITE_RECEIPT`。

## 失敗狀態

`WAITING_DATA`、`SKIP_LOCK_HELD`、`FAILED_CHECK`、`FAILED_WRITE_RECEIPT`、`UNVALIDATED_CONFLICT`。

## 組裝位置

研究 runner、daily pipeline、notebook、dashboard、target handoff 與 reconciliation 都應回傳或引用這個積木。

---

## [CB02] 積木 · TargetPortfolioSnapshot 研究到執行的唯讀快照

*track: block · status: verified · verified_by: 2026-08-27 focused pytest 95 passed; target snapshot and intake included · source: lesson/codex/blocks/CB02-target-portfolio-snapshot.md*

# TargetPortfolioSnapshot

## Interface

```text
identity: snapshot_id/version/hash
research binding: champion_id/version/implementation_hash/evidence_hash
time: generated_at/data_asof/valid_until
targets: symbol/target_weight/strategy attribution
```

## 禁止輸入

account id、broker object、cash、real holdings、market quote、share quantity、credential 或 order type。

## 輸出

可由 execution intake 驗證的 immutable target；不包含「怎麼下單」。

## 不變量

- 內容與 hash 一致。
- 權重有限、非負、總和符合契約。
- attribution 完整。
- snapshot 的 Champion 與 implementation 綁定。

## 失敗狀態

`HOLD_STALE_SNAPSHOT`、`HOLD_HASH_MISMATCH`、`HOLD_CHAMPION_MISMATCH`、`HOLD_ATTRIBUTION_MISSING`。

## 組裝位置

上游接 Champion receipt；下游只接 Target Intake Gate。通過後仍只有 `READY_FOR_DRAFT`。

---

## [CB03] 積木 · DecisionState 用具名狀態保存未知

*track: block · status: verified · verified_by: D:/Quant_Grill_Lab/src/quant_grill_lab/strategy_selection/model.py + execution/target_intake_gate.py · source: lesson/codex/blocks/CB03-decision-state-machine.md*

# DecisionState

## Interface

```yaml
state: PROMOTE | HOLD_* | KILL_* | WAITING_* | READY_FOR_DRAFT | NO_GO_REAL
reasons: [machine-readable reason codes]
evidence_refs: [receipt/hash/path]
next_acceptable_evidence: [關閉狀態需要什麼]
authority: research | execution | owner
```

## 為什麼是積木

`None`、空字串或「看起來可用」會讓下游自行猜測；具名狀態把未知保存到 interface 上，讓下游 fail closed。

## 不變量

- `HOLD` 不是失敗，也不是 PASS；它表示缺少可判決證據。
- `READY_FOR_DRAFT` 不能自動升級 `READY_FOR_REAL`。
- `PROMOTE` 只屬研究生命週期，不能授權 broker 行為。
- 只有 owner action 能跨 owner authority seam。

## 常見錯誤

把 `PAPER_MATCHED` 當 fill、把 `SKIP_BUSY` 當更新成功、把局部 tests 綠當 REAL-ready。

---

## [CB04] 積木 · OrderProposal 可閱讀、不可變的下單提案

*track: block · status: verified · verified_by: D:/Quant_Grill_Lab/src/quant_grill_lab/execution/order_proposal.py · source: lesson/codex/blocks/CB04-order-proposal.md*

# OrderProposal

## Interface

```text
proposal_id / batch_hash / mode / expires_at
summary: order_count / gross_value / fees / reserve / warnings
lines: symbol / strategy attribution / side / shares / lot lane / limit / order type
source bindings: target_hash / holdings_asof / quote_asof / config_hash
```

## 輸入

已通過 intake 的 target、owner-attested holdings、unfilled orders、fresh quote、sizing/cost/capacity rules。

## 輸出

供 owner 讀回與核准的 immutable proposal；不是 broker order。

## 不變量

- 同股票可合併 broker 數量，但策略 attribution 不可消失。
- 每筆與總計可重算並與 batch hash 綁定。
- 缺價格、部位不確定、現金不足或 lot lane 模糊時 fail closed。

## 失敗狀態

`HOLD_POSITION_UNCERTAIN`、`HOLD_STALE_QUOTE`、`HOLD_CASH_BREACH`、`HOLD_LOT_AMBIGUOUS`。

---

## [CB05] 積木 · OwnerApprovalGate 把人類核准綁到不可變 batch

*track: block · status: verified · verified_by: 2026-08-27 focused pytest 95 passed; order approval and requote included · source: lesson/codex/blocks/CB05-owner-gate.md*

# OwnerApprovalGate

## Interface

```text
challenge(batch_hash, purpose, mode, owner_key, expires_at)
verify(hardware_signature, pinned_key, current_time)
consume_once(approval_id, final_batch_hash)
```

## 輸出

一個短效、單次、綁定明確 proposal/batch/purpose/mode 的 owner approval receipt。

## 不變量

- 公鑰必須預先 pin，不能相信 payload 自帶的 key。
- 文字 token、challenge code 或 AI 回覆不能替代硬體簽章。
- 到期、重播、batch 改變、purpose/mode 改變都必須拒絕。
- AI 不得呼叫 owner 最終真實動作。

## 失敗狀態

`DENY_UNPINNED_KEY`、`DENY_EXPIRED`、`DENY_REPLAY`、`DENY_BATCH_CHANGED`、`WAITING_OWNER_ACTION`。

---

## [CB06] 積木 · Reconciliation 把目標、提案、委託、成交與部位串回同一證據鏈

*track: block · status: verified · verified_by: 2026-08-27 focused pytest 95 passed; settlement review included; live reconciliation remains unvalidated · source: lesson/codex/blocks/CB06-reconciliation.md*

# Reconciliation

## Interface

```text
inputs:
  target snapshot
  order proposal + approval receipt
  broker order callbacks
  broker deal callbacks
  position/cash snapshot
outputs:
  per-line target/proposed/submitted/filled/remaining
  fees and realized slippage when evidence exists
  unresolved broker ids and named exceptions
```

## 不變量

- 函式回傳成功不等於 broker 接受；只認 callback/ledger。
- 沒有 fill/fee/EOD price 就保留 unavailable，不補理論值。
- Common、IntradayOdd、Odd 是不同 lane，不自動 fallback 或重送。
- unresolved broker id 不自動 retry。
- 在足夠真實 fills 前，slippage model 維持 `UNVALIDATED`。

## 失敗狀態

`WAITING_CALLBACK`、`PARTIAL_FILL`、`REJECTED`、`UNRESOLVED_BROKER_ID`、`UNVALIDATED_SLIPPAGE`、`POSITION_MISMATCH`。

## 組裝位置

它是安全鏈最後一個 module，也反饋研究的成本與容量模型；但回饋必須經新版本、重新驗證，不能偷偷改歷史研究結果。

---

## [CB07] 策略卡 vs 實際帳戶 · 八鏡頭落差診斷

*track: block · status: verified · verified_by: D:/Quant_Grill_Lab/66.performance_accumulation_dashboard/tests/test_strategy_gap.py + output/build_receipt.json · source: lesson/codex/blocks/CB07-strategy-actual-gap.md*

# CB07 · 策略卡 vs 實際帳戶

## 先把兩個黑盒子拆開

策略卡與實際帳戶不是同一種報酬序列：

| 物件 | 分子 | 分母／權重 | 包含什麼 |
|---|---|---|---|
| 策略卡 | 每檔顯示報酬 | 當日成員等權 | 訊號價到卡片現價；通常不含現金、費稅與實際成交 |
| 實際 sleeve | 可變現價值與成交現金流 | 固定策略預算 | 實際股數、成交價、閒置現金、費稅、已實現與未實現 |

所以 `實際報酬 − 卡片報酬` 是 implementation gap，但不是 alpha，也不能直接解讀成「交易做差了」。

## 積木契約

```text
analyze(
  bridge,
  latest_signals,
  actual_curves,
  card_curves,
  benchmark_curves,
  slippage_rows,
  asof,
) -> strategy_actual_gap_report
```

必要不變量：

- 每個策略的 `actual − card` 必須等於 bridge 三項加總，容許誤差小於 `1e-12`。
- 卡片有、帳戶沒有的標的只列為 `missing_codes`；不得產生 counterfactual P&L。
- 計畫進出與實際成交分開；沒有 fill 就維持 `WAITING_ACTUAL_FILL`。
- 訊號成交樣本未滿 30 筆時，只報樣本與觀察值，不下執行品質結論。
- benchmark 必須使用同一起訖日；日期對不上就回傳缺值。

## 八個診斷鏡頭

| 鏡頭 | 問題 | 需要的資料 | 能說什麼 | 不能說什麼 |
|---|---|---|---|---|
| 成員覆蓋 | 卡片成員買了幾檔？ | 卡片、在庫 | 缺席與離卡持有 | 未買標的若買了會賺多少 |
| 資金投入 | 50 萬用了多少？ | 在庫成本、預算 | 現金曝險程度 | 現金一定是錯誤 |
| 訊號到成交 | 實付相對參考價？ | 可對上的 signal/fill | 執行落點 | 最佳進場價 |
| 費稅 | 進出成本吃掉多少？ | cash in/out | 已發生成本 | 未來固定成本率 |
| 已／未實現 | 錢已落袋還是在庫？ | FIFO lot、估值 | 損益所在狀態 | 把兩種分母直接平均 |
| 貢獻 | 哪些持股貢獻最大？ | 股數、價格、預算 | 帳戶貢獻集中度 | 因果選股能力 |
| 基準 | 有沒有勝過市場？ | 同期 TAIEX、0050 | 同期相對報酬 | 長期 alpha |
| 待成交 | 哪些只是計畫？ | signal state、fills | 作業待辦與證據缺口 | 把訊號冒充成交 |

## 描述性 bridge

目前使用的 bridge 是代數恆等式：

```text
gap
= actual_return - card_return
= (deployed_weight * held_return - deployed_weight * card_return)
 + (deployed_weight - 1) * card_return
 + realized_pnl / fixed_budget
```

三項可命名為：

1. 在庫組合與進場
2. 現金／未投入
3. 已實現貢獻

它們會精確加總，但第一項混合了成員、權重、進場時點、成交價與估值成本。因此方法標籤必須是 `DESCRIPTIVE_EXACT_ALGEBRA_NOT_CAUSAL_ATTRIBUTION`。

## 去識別合成例

假設策略卡有 5 檔、顯示 +8%，帳戶只持有其中 2 檔，投入 40%，實際 sleeve +1%。正確說法是：

- 覆蓋率 2/5。
- 投入率 40%。
- implementation gap 為 −7pp。
- bridge 可指出現金與在庫組合是下一步檢查方向。

錯誤說法是：「沒買的三檔造成 −X 元損失。」因為那需要明確的下單時間、數量、成交規則與成本；現在並不存在這筆交易。

## 驗證方式

```powershell
cd D:\Quant_Grill_Lab\66.performance_accumulation_dashboard
..\.venv\Scripts\python.exe -m pytest -q tests\test_strategy_gap.py
..\.venv\Scripts\python.exe scripts\build_dashboard.py
```

驗收時同時檢查：代數恆等式、缺席標的不產生假損益、共同日期 benchmark、樣本門檻，以及 HTML 沒有未替換模板標記。

## 可直接丟給 AI 的提問

> 請根據 strategy_actual_gap_report，依成員覆蓋、資金投入、訊號成交、費稅、已未實現、貢獻、benchmark、pending 八個鏡頭分析。先說資料口徑，再說差異；不得把卡片等權報酬當成可投資 NAV，不得替未成交標的建立假損益，也不得把描述性 bridge 寫成因果歸因。

---
