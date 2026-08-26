---
id: B11
title: 機械試驗計數器 · 不讓呼叫端自己填 N
author_ai: Claude (Opus 5, Anthropic)
track: block
status: verified
depends_on: [B13]
inputs: [experiment_log_files]
outputs: [n_trials, trial_sharpe_distribution, selection_bar]
verified_by: evidence/honest_top5/robustness.json
updated: 2026-08-26
notebooklm_tags: [dsr, trial-count, selection-bias, overfitting, audit]
---

# B11 · 機械試驗計數器

## 它解決什麼

去膨脹夏普的門檻由**試驗次數**決定。而試驗次數在大多數實作裡是**呼叫端自己填的參數** —— 填小一點，門檻就低，你的策略就「通過」了。

這不需要惡意，只需要健忘：沒有人記得三週前那個沒存檔的參數掃描也算試驗。

**實測**：某專案的紀錄檔寫 `n_trials: 134`，另一份文件寫 253。機械掃描實驗紀錄得到 **624**。

| 宣告的 N | 選擇偏差門檻（年化 Sharpe） |
|---|---|
| 134 | 1.401 |
| 253 | 1.512 |
| **624（機械計數）** | **1.660** |

差 0.26 個 Sharpe。對一個 Sharpe 2.1 的策略，這決定了 DSR 是 0.92 還是 0.96 —— 通過或不通過。

## 契約

```python
def mechanical_trial_count(log_glob="evidence/kiln/exp*.json", field="sharpe_local"):
    """從實驗紀錄檔數出試驗次數與 Sharpe 分布。呼叫端不能覆寫。"""
    sharpes = []
    for f in sorted(glob.glob(log_glob)):
        try:
            rows = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue                      # 壞掉的檔案不能讓計數靜默變小
        if not isinstance(rows, list):
            continue
        for row in rows:
            v = row.get(field)
            if isinstance(v, (int, float)) and np.isfinite(v):
                sharpes.append(float(v))
    return len(sharpes), np.array(sharpes)
```

搭配使用時，**不接受任何手動 `n_trials`**：

```python
n_trials, trial_sharpes = mechanical_trial_count()
bar = expected_max_sharpe(n_trials, trial_sharpes.var(ddof=1))
```

## 三個設計決定

**1. 搜尋程式在跑的時候就要寫紀錄，不是事後補。**
每一次 `sim` 都要落一列到紀錄檔，包含它的 Sharpe。事後回憶一定會少算。

**2. 全部試驗都要進分布，包含爛的。**
門檻由試驗結果的**離散度**決定。只餵存活者會低估離散度，門檻跟著低估。

**3. 壞掉的紀錄檔要跳過但不能靜默。**
上面的 `except: continue` 在生產版本應該記一行 warning。一個讀不到的檔案 = 一批沒被計入的試驗 = 偏低的門檻。

## 這個數字仍然是下界

機械計數只涵蓋**有留紀錄**的試驗。以下都不在裡面，而且都是真實的搜尋成本：

| 來源 | 為什麼算試驗 |
|---|---|
| 手動試的參數 | 你看過結果才決定不存 |
| 從公開文章移植的策略 | **發表者自己的搜尋成本未知且不是零** —— 一個被發表的策略，按定義就是「看起來夠好所以被發表」的那一個 |
| 從前一個專案繼承的 | 前一個專案的試驗數可能沒交接過來 |
| 組合／集成 | 從已知通過的積木裡挑組合，是一次新的後選擇 |

所以報告要寫「門檻 ≥ 1.660」而不是「門檻 = 1.660」。

## 兩種讀法都要報

```python
# 讀法一：這次 campaign 宣告的搜尋
n1, s1 = mechanical_trial_count("evidence/kiln/exp*.json")

# 讀法二：整個 catalog 當成一次搜尋（跨家族離散度大得多）
s2 = [r["sharpe"] for r in all_registered_strategies]
n2 = len(s2)
```

實測差距：

| 讀法 | N | 門檻（年化） | 12 檔候選通過數 |
|---|---|---|---|
| 已宣告的 campaign | 624 | 1.660 | 1 |
| 整個 catalog | 127 | **2.713** | **0** |

兩個都對，在回答不同問題。**誠實的報告要並列。**

## 陷阱

**陷阱：把重複註冊的策略當成不同試驗。**
實測發現三個編號指向同一支策略（日報酬相關係數 = 1.000）。用「策略數」當分母時，重複會讓 N 虛胖、離散度失真。先用 [B13 相關係數去重](B13-correlation-dedup.md)。

## 相關

- 為什麼要有這個：[C52 試驗計數](../52-trial-counting.md)
- 怎麼用這個數字：[C61 去膨脹夏普](../61-deflated-sharpe.md)
- Gemini 對 DSR 門檻的要求（N ≥ 400、DSR ≥ 0.95）：[G06](../../gemini/06-validation-dsr-and-forward-sim.md)。本塊是那條要求的**執行機制** —— G06 說「必須誠實包含所有被淘汰的試驗」，這裡是讓它無法不誠實的作法。
