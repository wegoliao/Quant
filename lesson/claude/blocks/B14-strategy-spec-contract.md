---
id: B14
title: 策略契約：讓作弊在建構物件時就爆掉
author_ai: Claude (Opus 5, Anthropic)
track: block
status: verified
verified_by: src/quant_grill_lab/strategies/base.py
updated: 2026-08-26
notebooklm_tags: [contract, strategy-spec, provenance, selection-bias, fail-fast]
---

# 策略契約：讓作弊在建構物件時就爆掉

> **證據**：本專案 `StrategySpec` 的實際設計與它擋下來的東西

## 問題

多 AI 協作的研究專案裡，最貴的失敗不是「策略不賺錢」，而是**你花了三天讀一份數字很漂亮的報告，最後發現它用當日收盤價成交**。

防守的地方應該在契約層 —— 讓錯誤在**寫策略的時候**就報錯，而不是在**讀報告的時候**才被發現。

## 契約要強制什麼

不是文件建議，是 `__post_init__` 裡的 `raise`。

### 一、禁止同棒成交

```python
def __post_init__(self):
    if self.trade_at_price == "close":
        raise StrategyContractError(
            "trade_at_price='close' fills at the same bar that produced the "
            "signal. AGENTS.md forbids presenting that as an executable "
            "fill. Use 'open' (next bar) or supply an explicit price frame."
        )
```

預設值是次日開盤。要用收盤價成交，你得先刪掉這段程式碼 —— 那是一個明確的、可被 code review 抓到的動作，而不是一個容易漏掉的參數。

### 二、強制申報讀了哪些資料集

```python
if not self.data_keys:
    raise StrategyContractError(
        "data_keys must list every FinLab dataset the strategy reads, "
        "so each source's data_asof can be recorded"
    )
```

為什麼重要：每個資料集有自己的 `data_asof`。申報之後，跑一次就能產生「這次用的每個來源分別更新到哪一天」的收據，而不是只有一個牆上時鐘的時間戳。

副作用同樣有用：`data_keys` 就是這塊積木的**輸入介面**。要拼積木，你需要知道每塊讀什麼。

### 三、強制申報來源與選擇偏差

```python
ORIGINS = ("NEW_IN_LAB", "INHERITED_WEGO", "PORTED_FINLAB_PUBLISHED")

def __post_init__(self):
    if self.origin not in ORIGINS:
        raise StrategyContractError(f"origin must be one of {ORIGINS}")
    if not self.selection_bias_note.strip():
        raise StrategyContractError(
            "selection_bias_note must not be empty; write 'none known' "
            "explicitly rather than leaving inherited bias undeclared"
        )
```

三個來源分類不是分類學潔癖，它們的未知量不同：

| 來源 | 搜尋成本 | 誰承擔 |
|---|---|---|
| `NEW_IN_LAB` | 本專案的試驗，有紀錄可數 | 自己 |
| `INHERITED_WEGO` | 前一個專案的試驗，部分有紀錄 | 繼承 |
| `PORTED_FINLAB_PUBLISHED` | **發表者的搜尋成本，未知且不是零** | 外部，不可數 |

第三類最容易被誤讀成「乾淨的結果」。但**一個被發表的策略，按定義就是「看起來夠好所以被發表」的那一個**。它的選擇偏差存在，只是你數不到。

`selection_bias_note` 不允許空字串，強迫作者要嘛寫出來，要嘛明確寫「none known」。實測這一欄真的有在做事 —— 某檔策略的自述是：

> DOES NOT CLEAR DEFLATION AND IS FILED ANYWAY. DSR 0.9250 against a 0.95 threshold on the declared 253-trial campaign, verdict INDISTINGUISHABLE_FROM_SEARCH.

一個誠實到會寫下自己沒通過的欄位，比任何 dashboard 都有價值。

### 四、強制寫出「為什麼預期它會賺」

```python
if not self.thesis.strip():
    raise StrategyContractError(
        "thesis must say why this is expected to earn a return; a "
        "strategy nobody can state a reason for is a fitted curve"
    )
```

最後半句是整個契約的靈魂：**沒有人能說出理由的策略，就是一條擬合出來的曲線。**

GA 搜出來的東西尤其需要這一關。如果你寫不出「為什麼這四個因子加起來會有超額報酬」，那你找到的可能只是噪音的一個好看切面。

### 五、參數名要對得上

```python
unknown = set(self.default_params) - set(self.build_parameters())
if unknown:
    raise StrategyContractError(
        f"default_params contains names build() does not accept: {sorted(unknown)}"
    )
```

這條擋掉一整類 bug：`default_params` 寫了 `bull_leverage=1.5`，但 `build()` 根本不吃這個參數 —— 於是測試斷言 `default_params["bull_leverage"] == 1.5` 會通過，而實際跑出來的策略完全不是那回事。

我實際看過這個組合出現：一份報告的測試「4/4 PASS」，斷言的全是 `default_params` 字典的字面值，而那些參數對 `build()` 的行為毫無影響。

### 六、成本假設跟著策略走

```python
@dataclass(frozen=True)
class BacktestConfig:
    resample: str | None = "M"
    resample_offset: str | None = None
    fee_ratio: float = TW_FULL_FEE_RATIO      # 未折扣
    tax_ratio: float = TW_TAX_RATIO
    trade_at_price: str = "open"
```

成本假設放在策略裡，不放在 notebook cell 裡。理由寫在 docstring：

> so two strategies are never silently compared under different fee models.

這一條在做全量比較時直接兌現：

```python
rep = backtest.sim(pos, **spec.backtest.as_sim_kwargs())
```

一行就跑完 127 檔，每檔用自己宣告的假設。不用擔心某一檔偷偷用了折扣費率。

### 七、`upload=False` 不可協商

```python
kwargs = {
    ...
    # upload=False is not optional. A research run must never publish to
    # the FinLab cloud as a side effect of pressing Run All.
    "upload": False,
}
```

寫死在 `as_sim_kwargs()` 裡，不給呼叫端選。研究跑批不應該有對外的副作用。

## 契約擋不住什麼

要誠實：**這個契約擋不住疊加層的前視。**

`trade_at_price` 檢查守的是回測引擎的成交價。但如果有人在 `backtest.sim` **之外**對報酬序列做乘法：

```python
r_levered = base_returns * regime_multiplier      # 繞過整個引擎
```

契約完全看不到。這正是那份 CAGR 65% 報告的作法。

**所以契約要配一條規則**：任何不經過 `backtest.sim` 的報酬變換，都要在測試裡單獨做 shift(1) 驗證。契約管得住引擎內，管不住引擎外。

## 拿來拼積木

契約的副產品是每塊積木都自帶介面說明：

```python
spec.data_keys           # 輸入：讀哪些資料集
spec.build_parameters()  # 可調的旋鈕
spec.default_params      # 預設值
spec.backtest            # 成本與換股假設
spec.source              # 來源與選擇偏差
spec.thesis              # 為什麼預期會賺
spec.module_source()     # 完整原始碼，給人讀的
```

`module_source()` 那個是刻意的 —— 設計目標是「策略的 FinLab 程式碼是要被擁有者讀的，不是藏在框架後面」。黑盒子要能被打開，才叫積木。

## 記住

> 契約的價值不在它擋下多少錯，而在它讓錯誤發生在**寫的時候**而不是**讀報告的時候**。前者花五分鐘，後者花三天。

相關：[假驗證的四種形態](../51-fake-validation.md)、[驗證流水線](../60-verification-harness.md)
