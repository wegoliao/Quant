---
id: SHARED-GLOSSARY-01
title: 量化工程與系統專有名詞對照表 (Quant Glossary & Metric Conventions)
author_ai: Multi-AI Consensus (Gemini & Claude & Codex)
track: shared
status: verified
updated: 2026-08-26
web_url: https://wegoliao.github.io/Quant/lesson/_shared/GLOSSARY.html
notebooklm_tags: [glossary, terminology, metrics, dsr, pbo, pit, conventions]
---

# 量化工程專有名詞與指標口徑對照表 (Glossary)

## 一句話總結 (TL;DR)

本文件統一了 Quant Grill Lab 中所有 AI（Gemini、Claude、Codex 等）所使用的核心術語、策略代號（S-ID）、風控指標口徑與狀態常數，杜絕跨 AI 溝通時的概念漂移。

---

## 1. 核心治理與系統狀態常數

| 術語 / 常數 | 完整英文 | 核心定義與強制規範 |
|---|---|---|
| **HOLD_RESEARCH_ONLY_NO_PRISTINE_OOS** | Hold Research Only - No Pristine Out-Of-Sample | 本系統的最高總體狀態判定：所有歷史回測（即使切分 IS/OOS）均受研究選擇偏誤影響，在未累積足夠真實前瞻交易日前，**嚴禁視為已證明的可部署 Alpha**。 |
| **UNVALIDATED** | Unvalidated Slippage Model | E5 滑價模型的預設狀態。在未取得至少 30 筆 `BROKER_REAL` 真實成交紀錄前，所有預估成交價均必須標記為未驗證。 |
| **Fail-Closed** | Fail-Closed Architecture | 系統在遇到資料缺失、網路中斷、盤口異常或計算超時等未定義狀態時，**一律自動選擇最安全路徑（停止交易 / 取消委託 / 權重歸零）**，絕不冒險猜測。 |
| **PIT** | Point-in-Time Data | 時間點精確資料。嚴格區分「財報涵蓋期（如 2024Q1）」與「真實公告發布日（如 2024-05-14）」，確保回測在 2024-05-10 時絕對看不到 Q1 財報。 |
| **Lag** | Data Release Lag | 月營收在次月 10 日前公佈、季報在次季 45 日內公佈的法定發布延遲。代碼中必須嚴格以發布日作為 index，而非月份標籤。 |

---

## 2. 統計與抗過擬合評估指標

| 指標名稱 | 縮寫 / 代號 | 計算原理與本系統門檻 |
|---|---|---|
| **Deflated Sharpe Ratio** | **DSR** | 由 Marcos López de Prado 提出。在考慮**總試驗次數（Number of Trials）**、策略報酬之偏態（Skewness）與峰態（Kurtosis）以及樣本長度後，校正後的真實 Sharpe 顯著性。本系統要求核心候選 DSR $\ge 0.95$。 |
| **Probability of Backtest Overfitting** | **PBO** | 利用組合對稱交叉驗證（CSCV）切分子樣本，衡量最佳回測策略在樣本外績效排在中位數以下的機率。PBO 需 $\le 0.15$。 |
| **Average Daily Volume (20D)** | **ADV20** | 個股過去 20 個交易日的日均成交金額（元）或日均成交量（張）。本系統硬性規定單筆委託不得超過該股 ADV20 的 5%（超過直接 `BLOCKED`），且超過 2% 需發出 `WARNING`。 |
| **Plateau Pass Rate** | **Plateau** | 參數高原穩定性檢驗。將關鍵參數在 $\pm 1$ 鄰域內網格微調，要求至少 80% 的鄰近組合能維持冠軍表現的 85% 以上，杜絕「孤峰過擬合」。 |
| **Time-Weighted Return** | **TWR** | 時間加權報酬率。排除帳戶資金進出（Deposit/Withdrawal）影響，客觀衡量操盤實績。 |

---

## 3. 策略編號家族速查 (Strategy Registry Index)

| 策略編號 | 策略識別碼 (Strategy ID) | 主導 AI | 核心機制簡述 |
|---|---|---|---|
| **S022** | `multi_factor_40_basket` | Codex / Gemini | 40 檔中大型股六因子等權組合（NT$500萬容量，基準候選） |
| **W0085** | `high_sharpe_micro_basket` | Historical Lab | Sharpe 2.0+ 微型股策略（胃納量僅 NT$8.5萬，研究對照組） |
| **S048** | `three_family_equal_sleeve` | Portfolio Lab | 三大策略家族等權多 Sleeve 組合（NT$960萬容量） |
| **S138** | `gemini_001_weighted_cashflow_momentum` | **Gemini** | **反向波動加權現金流動能**（Top 20，單檔 10% 上限，Sharpe 2.15） |
| **S139** | `gemini_002_hedged_cashflow_momentum` | **Gemini** | **大盤均線宏觀濾網對沖型現金流動能**（牛市做滿、破線減倉） |
| **S140** | `gemini_004_vol_target_cashflow_momentum` | **Gemini** | **動態波動度目標化配置**（控制組合年化波動在 15% 以內） |
| **S141** | `gemini_007_multimethodology_ensemble` | **Gemini** | **價值+動能+籌碼+微結構四維集成**（多方法論抗單一週期失效） |
| **S142** | `radical_001_convexity_pareto` | **Gemini** | **50% CAGR 凸性激進 GA 演化策略**（集中 8~12 檔、雙軌進出場） |
| **S143** | `radical_002_institutional_cluster` | **Gemini** | **法人共振與籌碼集中度突破策略**（投信連買+主力分點鎖碼） |

---

## 4. NotebookLM 快速導引

- **提問範本**：「請查閱 Glossary，解釋為什麼本系統規定 DSR 必須扣除總試驗次數（Trials），這對避免過擬合有什麼作用？」
