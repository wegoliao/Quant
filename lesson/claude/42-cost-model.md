---
id: C42
title: 成本模型：不打折、次日開盤、重跑而非扣減
author_ai: Claude (Opus 5, Anthropic)
track: context
status: verified
verified_by: evidence/honest_top5/robustness.json
updated: 2026-08-26
notebooklm_tags: [cost, fee, tax, slippage, stress-test]
---

# 成本模型：不打折、次日開盤、重跑而非扣減

> **證據**：12 檔策略在 0 / +10bps / +30bps 三個成本檔位各重跑一次 `backtest.sim`

## 台股的成本組成

| 項目 | 費率 | 說明 |
|---|---|---|
| 券商手續費 | **0.1425%**（未折扣） | 買賣各一次 |
| 證券交易稅 | **0.3%** | 只在賣出時 |
| 滑價 | 視流動性 | 回測預設不含，要另外壓測 |

## 為什麼用未折扣費率

多數券商會給折扣（3 折、2.8 折很常見）。用折扣後的費率回測，數字會好看很多。

但這裡有一個判斷準則：

> **一個只有在 3 折才活得下去的策略，它的 edge 是退佣，不是 alpha。**

用未折扣的 0.1425% 回測，是在問「這個策略本身有沒有東西」。如果它在未折扣下就過關，折扣是純粹的加分；如果它需要折扣才過關，你要知道自己在賭什麼。

這個 repo 的預設值把這個判斷寫進註解裡：

```python
# 0.1425% is the UNDISCOUNTED broker fee. Most brokers discount it, but a
# strategy that only survives at a 3-something discount rate is a strategy whose
# edge is a rebate, and the owner should see that before capital is committed.
TW_FULL_FEE_RATIO = 0.001425
TW_TAX_RATIO = 0.003
```

## 為什麼成交價是次日開盤

訊號在收盤後才算得出來，所以最早只能在次日開盤成交。用當日收盤價成交等於同棒前視。

強度做法是在契約層直接禁止：

```python
def __post_init__(self):
    if self.trade_at_price == "close":
        raise StrategyContractError(
            "trade_at_price='close' fills at the same bar that produced the "
            "signal. Use 'open' (next bar) or supply an explicit price frame."
        )
```

讓錯誤在建構物件時就爆掉，而不是等到你在解讀一份漂亮的報告時。

## 成本壓測：一定要重跑

**錯的做法**（從報酬序列扣一個常數）：

```python
r_slipped = daily_returns - slippage_ratio * 0.10      # 不要這樣
```

這與週轉率完全脫鉤。月頻換股一年成交 12 次，但這條公式每年扣 252 次。

**對的做法**（每個檔位重新模擬）：

```python
def sim_returns(spec, params, fee_add=0.0):
    pos = spec.build_position(**params)
    kw = spec.backtest.as_sim_kwargs()
    if fee_add:
        kw["fee_ratio"] = kw["fee_ratio"] + fee_add
        kw["tax_ratio"] = kw["tax_ratio"] + fee_add
    return active_returns(backtest.sim(pos, **kw).creturn)

for add, tag in [(0.0, "declared"), (0.001, "+10bps"), (0.003, "+30bps")]:
    r = sim_returns(spec, params, fee_add=add)
```

## 實測：真實的成本反應長什麼樣

| S### | 宣告成本 | +10bps/邊 | +30bps/邊 | Sharpe 衰減 |
|---|---|---|---|---|
| S127 | 2.107 | 1.988 | **1.746** | **-17%** |
| S126 | 1.499 | 1.411 | 1.232 | -18% |
| S124 | 2.027 | 1.886 | 1.596 | -21% |
| S148 | 1.545 | 1.437 | 1.219 | -21% |
| S123 | 2.097 | 1.947 | 1.640 | -22% |
| S022 | 1.756 | 1.631 | 1.377 | -22% |
| S048 | 1.542 | 1.420 | 1.171 | -24% |
| S125 | 1.816 | 1.664 | 1.354 | -25% |
| S122 | **2.211** | 2.019 | 1.625 | **-26%** |
| S004 | 1.993 | 1.823 | 1.477 | -26% |
| S144 | 2.110 | 1.922 | 1.540 | -27% |
| S138 | 2.148 | 1.947 | 1.538 | -28% |

**衰減率從 -17% 到 -28% 不等** —— 因為週轉率不同。這個離散度本身就是「有真的重跑」的證明。

如果你看到一張表裡所有策略的 Sharpe 衰減率一模一樣，或者單一策略的 Sharpe 對成本呈完美線性，那就是算術扣減，不是回測。

## 排名會因為成本假設而改變

上表最重要的一行：**Sharpe 最高的 S122（2.211）在 +30bps 之後掉到 1.625，被 S127（1.746）和 S123（1.640）超車。**

S122 每年 287 次交易，S127 每年較少且持股更集中。宣告成本下 S122 贏，高成本下輸。

所以「哪個策略最好」這個問題，在你說清楚成本假設之前是沒有答案的。

## 加 30bps 之後誰還站著

實測 12 檔候選，加 30bps/邊之後：

- 沒有任何一檔還在 Sharpe 1.8 以上
- 過 1.6 的只剩 3 檔（S127 1.746、S123 1.640、S122 1.625）
- 其餘 9 檔全部掉到 1.6 以下

如果你的部署門檻是 Sharpe 1.6，那麼「在什麼成本下的 1.6」必須寫在門檻定義裡。

## 檢查清單

1. 用的是未折扣費率嗎？
2. 成交價是次日開盤（或更保守）嗎？
3. 滑價壓測有重跑 `sim` 嗎？（算 Sharpe 一階差分驗證）
4. 各策略的衰減率有差異嗎？（全部一樣 = 造假）
5. 我的 Sharpe 門檻是在哪個成本檔位下說的？

相關：[假驗證的四種形態](51-fake-validation.md)、[資料的真相](40-research-data-truth.md)
