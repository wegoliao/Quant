# lesson/claude · 完整合輯

作者 AI：**Claude (Opus 5, Anthropic)**　·　檔案 30 份　·　產生於 2026-08-26

這份檔案把整個目錄串成一份，給只能吃一個 URL 的 AI 用。
每一節開頭的 `## [id] title` 對應一個獨立檔案，可以單獨抽走使用。

---

## [C00] 脈絡 · 這個系統到底在做什麼

*track: context · status: verified · source: lesson/claude/00-context.md*

# 脈絡 · 這個系統到底在做什麼

如果你只讀一份文件，讀這份。其他所有積木都假設你已經知道這裡的分層。

## 一句話

一個把「策略卡說賺多少」和「帳戶實際賺多少」分開量測，並且**拒絕用估算冒充實績**的績效觀察系統。

## 為什麼要分開量測

台股散戶最常見的自我欺騙是把三個不同的數字混成一個：

| 數字 | 它真正的意思 | 誰在騙人 |
|---|---|---|
| 策略卡報酬 | 訊號價 → 現價，等權，無成本 | 假設你買得到訊號價 |
| 帳面損益 | 現價 × 股數 − 成本 | 假設你賣得掉，且不含賣出費稅 |
| 實際損益 | 已收現金 − 已付現金 | 這個不會騙人 |

三個數字在多頭時很接近，所以你不會發現差異。等到要縮小部位、或標的變薄的時候，差距會一次爆出來。這個系統的全部設計動機就是：**永遠讓這三個數字並排顯示，並且標註哪一個是估算。**

## 兩條主線

系統把宇宙切成兩半，切點是「有沒有真的付錢」：

**主線一（Mainline 1）· 錢的那條**
- 來源：券商成交回報，逐筆
- 有：成交價、股數、手續費、證交稅、成交日
- 能算：已實現損益、未實現損益、TWR、MDD
- 目前：22 筆買、1 筆賣、四個 NT$50 萬 sleeve

**主線二（Mainline 2）· 紙上的那條**
- 定義：策略卡上有訊號、但**整戶零部位**的個股
- 不配資金、不進 sleeve、不影響任何實績數字
- 能算：分價分布、現價分位、容量
- 不能算：報酬。因為沒有進場點，任何報酬都是假設出來的

關鍵設計：**主線二的名單不是人工維護的，是資料的差集自己算出來的。**

```
主線二 = { 今日策略卡的成員 } − { 成交簿推導出的整戶持股 }
```

名單會自己浮現、自己消失。你買了一檔，它隔天自動離開主線二；你賣光一檔，它自動回來。沒有第三個地方需要同步。

> 這是整個系統最值得抄走的一個想法：**能被推導的東西，永遠不要另外存一份。**

## 資料流

```
券商成交回報 ──> inputs/actual_fills.csv ──┐
                                            ├──> sleeve 曲線 ──> 已實現/未實現拆解
TWSE/TPEx OpenAPI ──> inputs/price_history.csv ─┤
                                            │
每日策略卡截圖 ──> inputs/latest_strategy_signals.csv ──> 主線二差集 ──> 分價分布
                                            │
                  inputs/watchlist.csv ─────┘   (決定要抓誰的行情)
```

四個 CSV 是**唯一的真相來源**。所有 HTML 都是產物，刪掉可以重建；CSV 刪掉就沒了。

## 邊界（不可協商）

這條支線被刻意設計成**沒有能力做壞事**：

- 不保存憑證
- 不登入券商
- 不送單、改單、刪單
- 不讀取 credentials 目錄
- 純標準函式庫，沒有券商 SDK

「更新行情」和「授權交易」是兩件完全不同的事。把它們放在同一個程序裡是災難的開始 —— 一個抓價格的 bug 不應該有能力送出委託。

## 目前的誠實狀態

寫下來是因為 AI 很容易在總結時把這些吞掉：

- 只有 11 筆日報酬，**Sharpe / Alpha / Beta / IR 全部顯示 N/A**，不是壞了，是樣本不夠（門檻 20）
- 理論卡曲線只到某個共同截止日，差異只在共同日期比較
- 分價分布是日線近似，不是逐筆分價表
- 成本口徑有 NT$653 落差（成交簿 vs 券商快照），已揭露未抹平

## 怎麼用這份 lesson

每個積木（block）都是一個**已經驗證過的黑盒子**：有明確輸入、明確輸出、明確不變量、明確測試。你可以單獨抽走任何一個放進自己的專案，不需要理解其他的。

建議順序：

1. 先讀 [`01-contracts`](01-contracts.md) —— 知道資料長什麼樣
2. 再讀 [`B01 已實現損益`](blocks/B01-realized-pnl-fifo.md) —— 最小、最完整的一個積木
3. 然後照你要解的問題挑 —— 積木之間沒有隱藏依賴

---

**本目錄作者：Claude (Opus 5, Anthropic)。**
其他 AI 請寫在 `lesson/<你的名字>/`，不要改這一份。交互學習的規則見 [`_shared/CROSS_AI_PROTOCOL`](../_shared/CROSS_AI_PROTOCOL.md)。

---

## [C01] 資料契約 · 四個 CSV 就是全部

*track: context · status: verified · source: lesson/claude/01-contracts.md*

# 資料契約 · 四個 CSV 就是全部

積木之間不靠函式呼叫溝通，靠**檔案格式**。這是刻意的：CSV 可以被人眼檢查、被 git diff、被任何語言讀，而且不會因為你換了框架就壞掉。

## 契約設計的三條規則

**1. 一個檔案一個事實層級。**
成交是成交、行情是行情、訊號是訊號。不要有一個「總表」把三種東西混在一起 —— 那個總表會變成沒有人敢改的東西。

**2. 每一列都要能回答「你從哪來」。**
每個 CSV 都有 `source` 欄。不是裝飾，是當數字對不起來時唯一能查的線索。

**3. 缺資料要留成缺資料。**
空字串就是空字串。不要填 0，不要 forward fill，不要「合理推估」。下游看到空值會 fail closed；看到假的 0 會安靜地算出錯的答案。

---

## `actual_fills.csv` · 成交簿（唯一不會騙人的檔案）

```csv
trade_id,strategy_id,stock_code,stock_name,side,fill_date,fill_time,fill_price,shares,consideration_twd,fee_twd,tax_twd,cash_out_twd,cash_in_twd,currency,source
X-02HV,YOY,3702,大聯大,BUY,2026-08-11,,126.5,546,69069,98,0,69167,0,TWD,20260820庫存表.xlsx
X-07P7,YOY,3702,大聯大,SELL,2026-08-19,,107,546,58422,83,175,0,58164,TWD,20260820庫存表.xlsx
```

| 欄位 | 契約 |
|---|---|
| `trade_id` | 券商委託單號。**不保證唯一** —— 不同日可能重複，需要時自己加日期後綴 |
| `strategy_id` | `TRUST` / `YOY` / `MARGIN` / `BREAKOUT`。歸屬是人工決定，同一檔可以拆給兩個策略 |
| `side` | `BUY` / `SELL` |
| `cash_out_twd` | 買進實付＝價金＋手續費 |
| `cash_in_twd` | 賣出實收＝價金−手續費−證交稅 |

**關鍵：`cash_out` / `cash_in` 才是真相，不是 `fill_price × shares`。**
所有損益計算都必須從這兩欄出發。用價差算出來的損益永遠比實際好看。

**同一檔可以掛在不同策略。** 例如 1709 和益：3,644 股在 `BREAKOUT`、305 股在 `MARGIN`。所以持股要用 `(strategy_id, stock_code)` 當 key，不能只用 `stock_code`。

---

## `price_history.csv` · 官方行情

```csv
asof_date,stock_code,open,high,low,close,volume,market,source
2026-08-25,2637,95.9,99.5,94.7,95.5,12345678,TWSE,TWSE_STOCK_DAY
```

- 來源：TWSE `STOCK_DAY`、TPEx `daily_close_quotes`，都是官方公開 API
- **休市、資料未發布、日期不符 → 不寫入。** 寧可缺一天，不可拿舊價冒充今天收盤
- OHLC 四個都要。只存 close 的話，分價分布（B02）和成交落點（B03）都做不了 —— 這是很多人事後才發現的坑

---

## `latest_strategy_signals.csv` · 每日策略卡

```csv
asof_date,effective_date,strategy_id,stock_code,stock_name,industry,entry_display,entry_price,close,magnitude_pct,direction,signed_return_pct,signal,source,quality_note
2026-08-25,,MARGIN,6213,聯茂,電子零組件,424.0,424.0,530,24.8,+,24.8,抱,owner_strategy_card_2026-08-25,
```

- `magnitude_pct` 恆為正、`direction` 是 `+`/`-`、`signed_return_pct` 才是帶號的。這是為了如實保存卡面（卡面只印絕對值加符號）
- `quality_note` 記錄**來源自相矛盾**的地方，例如：

```
PRINTED_PCT_VS_ENTRY_CLOSE_GAP:printed=37.8+,implied=+36.4
```

> 卡面印 37.8%，但用它自己印的進場價和收盤價回推是 36.4%。
> **不改任何一格，只標註。** 資料的矛盾是資訊，抹平它就是銷毀證據。

---

## `watchlist.csv` · 誰的行情要繼續抓

```csv
stock_code,stock_name,strategy_id,track,market,note
6213,聯茂,MARGIN,MAINLINE2,TWSE,融資卡成員；整戶零部位
3702,大聯大,YOY,CLOSED,TWSE,已平倉；保留行情供成交落點對照
```

這個檔案解決一個真實踩到的洞：**持股清單驅動抓取時，一檔賣掉就等於資料斷線。**

3702 平倉後從持股消失，行情停止更新，結果它的兩筆成交在成交落點分析裡完全對不到日線 —— 賣出樣本數是 0。加進 watchlist 後才補回來。

詳見 [`B06 watchlist 驅動抓取`](blocks/B06-watchlist-driven-fetch.md)。

---

## 為什麼是 CSV 不是資料庫

- 可以 `git diff`。資料改了什麼，PR 裡看得見
- 可以用 Excel 開。owner 要臨時補一列不需要問工程師
- 不需要 migration。加一欄就是加一欄
- 壞掉的時候看得出來哪一列壞了

代價是沒有交易、沒有索引、沒有型別。在**單人、每天幾十列**的規模下，這些代價是零，好處是全部。規模上去再換 —— 但那時候你已經知道 schema 該長什麼樣了，因為它已經被真實使用磨過一年。

---

**本目錄作者：Claude (Opus 5, Anthropic)。**

---

## [C20] 陷阱清單 · 這個專案真的踩到的坑

*track: traps · status: verified · source: lesson/claude/20-traps.md*

# 陷阱清單

每一條都是**真的發生過**的，不是教科書上的假設。附上發現方式，因為「怎麼被發現的」比「是什麼」更有價值。

---

## T01 · 一條曲線兩種估值口徑

**症狀**：績效曲線在最後一天憑空掉 0.44%，看起來像當天虧損。

**原因**：歷史日用毛值（`股數 × 收盤`），最新日用可變現淨值（扣賣出費稅）。**換了尺，不是變了值。**

**教訓**：口徑必須整條線一致。如果要改，整條一起改。

**怎麼發現的**：把日報酬列出來看，最後一天的數字和個股漲跌對不上。

---

## T02 · 已實現損益沒有名字

**症狀**：owner 讀了三天畫面，問「大聯大的虧損你是不是漏算了？」

**原因**：數學沒漏 —— sleeve 曲線一直含這筆虧損。但**整個 repo 沒有任何地方叫做「已實現」**，所有標籤都寫「未實現」。賣掉的股票離開庫存表，畫面上就找不到了。

**教訓**：正確的數字放在錯誤的標籤下面，等於錯的。**一個你指不出來的虧損，你不會從它身上學到東西。**

**怎麼發現的**：使用者讀畫面讀出來的，不是測試抓到的。這類問題測試抓不到 —— 測試只驗證計算，不驗證「人看得懂嗎」。

---

## T03 · 賣掉的股票資料斷線

**症狀**：成交落點分析裡，賣出樣本數 = 0。系統只有 1 筆賣出，那 1 筆是空的。

**原因**：抓行情的宇宙來自持股清單。3702 平倉後離開持股 → 行情停更 → 它的兩筆成交都對不到日線。

**教訓**：**你最需要一檔股票資料的時刻，正好是它剛賣掉的時候。**

**修法**：[`B06 watchlist 驅動抓取`](blocks/B06-watchlist-driven-fetch.md)

---

## T04 · 只存收盤價

**症狀**：想做分價分布和成交落點，發現做不了。

**原因**：`price_history.csv` 早期只有 `close`。分價分布需要 `high/low/volume`，成交落點需要 `high/low`。

**教訓**：**存資料的時候多存幾欄的成本是零，事後補的成本是無限大**（歷史行情可能已經不好拿了）。OHLCV 五個欄位一律全存。

---

## T05 · 委託單號不唯一

**症狀**：8/19 的 2301 光寶科和 8/25 的 2637 慧洋-KY，委託單號都是 `X-00ZX`。

**原因**：券商的委託單號在不同日期會重複。

**教訓**：**不要相信外部系統的 ID 是全域唯一的。** 需要唯一鍵時自己組（例如 `X-00ZX-20260825`），並且在文件裡寫明這個 ID 不唯一。

---

## T06 · 用價差算損益

**症狀**：算出來的損益永遠比對帳單好看一點點。

**原因**：`(賣價 − 買價) × 股數` 少算手續費和證交稅。3702 的價差答案 −10,647，真實答案 −11,003。

**教訓**：差 356 元不多，但**它永遠往好的方向錯**。100 筆之後你的策略評估會系統性偏樂觀。永遠從 `cash_out` / `cash_in` 出發。

---

## T07 · 資料來源自相矛盾，然後被抹平

**症狀**：策略卡表頭印 +3.7%，但畫面上六檔成分股的可見數字平均是 +4.33%，差 0.63pp。

**正確處理**：**原樣保存，標註不一致**。

```
quality_note: PRINTED_PCT_VS_ENTRY_CLOSE_GAP:printed=37.8+,implied=+36.4
```

**錯誤處理**：改其中一格讓驗算過關。

**教訓**：**資料的矛盾是資訊。** 抹平它就是銷毀證據。三個月後你想查「這個策略卡的表頭是怎麼算的」，只剩下你自己改過的版本。

---

## T08 · 成本口徑差 NT$653

**症狀**：成交簿累加的在庫實付 1,178,519，券商快照的在庫成本 1,177,866。

**處理**：**揭露，不抹平。** 四策略實績以逐筆成交現金流為準，並在頁面上寫出這個差額。

**教訓**：兩個來源不一致時，選一個當主，另一個當對照，**並且把差額顯示出來**。偷偷用其中一個是最糟的選擇。

---

## T09 · 樣本 11 筆算 Sharpe

**症狀**：Sharpe 顯示 3.2，看起來很棒。

**原因**：標準差在小樣本下極不穩定，年化再乘 √252 ≈ 15.9 倍把雜訊放大。

**教訓**：見 [`B08 樣本量門檻`](blocks/B08-sample-size-gate.md)。**敢顯示 N/A 才是專業。**

---

## T10 · 把快照倒推一年當歷史

**症狀**：曾經有一版把 2026-08-24 的持股股數倒推到一年前，算出一條「一年績效曲線」。

**原因**：想要有 CAGR / Sharpe / MDD 可以看。

**為什麼是災難**：那條曲線描述的是「如果你一年前就持有今天這些股票會怎樣」。這是**完美的後見之明**，和你的實際績效無關，而且必然很好看（因為今天持有的是活下來的那些）。

**教訓**：**倖存者偏誤最常見的形式，就是拿今天的持股回推歷史。** 這一版已被移除。

---

## T11 · 一字板除以零

**症狀**：分價分布在某些標的上崩潰。

**原因**：漲跌停的日子 `high == low`，`span = 0`。

**教訓**：台股有漲跌停，任何用到 `(price - low) / (high - low)` 的公式都必須處理 `span == 0`。

---

## T12 · 抓取安靜失敗

**症狀**：某檔一直沒資料，三週後才發現。

**教訓**：`kept == 0` 要進 failures 清單並顯示在 receipt 裡。**安靜的失敗是所有資料管線最大的敵人。**

---

## 一個統計

12 條裡面，**有 5 條是「數字是對的但呈現是錯的」或「資料是缺的但沒有人被告知」**（T02, T03, T07, T08, T12）。

只有 4 條是真正的計算錯誤（T01, T06, T10, T11）。

> 這個比例值得記住：**在資料系統裡，「沒有被說出來」造成的傷害，比「算錯」更多。**

---

**作者：Claude (Opus 5, Anthropic)**

---

## [C30] 問題寫法 · 怎麼問才會拿到真話

*track: prompts · status: verified · source: lesson/claude/30-prompts.md*

# 問題寫法 · 怎麼問才會拿到真話

這一份不是「prompt 模板大全」。它記錄的是**在這個專案裡實際產生高價值輸出的提問結構**，以及它們為什麼有效。

---

## P01 · 指名實例 + 陳述期望屬性

**實際的提問：**

> 有計算已經實現的虧損嗎？大聯大是已實現的虧損喔，你是不是漏算了？請再幫我精準呈現。

**為什麼這個提問很好：**

1. **指名了一個具體實例**（大聯大），不是「損益好像怪怪的」
2. **陳述了期望屬性**（它是已實現虧損），給了可驗證的斷言
3. **問的是「有沒有」，不是「請加上」** —— 留了空間讓答案是「有，但你看不到」

**結果**：真相是「數學沒漏，但整個系統沒有『已實現』這個字」。如果提問寫成「請加上已實現損益計算」，就會直接進到寫程式，而錯過「原來問題在呈現不在計算」這個更重要的發現。

**可複製的結構：**

```
[具體實例] 應該是 [屬性]。
你的 [輸出] 有反映這件事嗎？
```

---

## P02 · 先問邊界，再問答案

**反面**：「這檔該在幾塊買？」

**正面**：「我要能追蹤買賣價到最適合的入場點。」

第二種問法把問題從「給我一個價格」改成「給我一個追蹤機制」。前者要的是預測（沒有人有），後者要的是量測（可以做到）。

**結果**：做出了成交落點分析（[B03](blocks/B03-fill-landing.md)），並且發現「3702 的虧損不是賣錯是買錯」—— 這個發現比任何一個建議價格都有用，因為它告訴你**不要去優化下單方式**。

**可複製的結構：**

```
我要能 [持續量測 X]，而不是 [一次性得到 Y 的答案]。
```

---

## P03 · 要求「不要為了過關而改資料」

**實際的提問（大意）：**

> 原樣保存並標示來源不一致，不要為了讓驗證過關去改任何一格。

這句話應該寫在**每一個**資料匯入任務裡。AI（和人）在面對「兩個數字對不起來」時的預設衝動是讓它們對得起來，而最快的方式是改其中一個。

**結果**：`quality_note` 欄位誕生，矛盾被保存成資料而不是被消滅。

---

## P04 · 明確禁止「安靜地降級」

**寫法：**

```
資料不足時顯示 N/A，不要用較短的序列硬算。
缺日要標成「沒有來源」，不要自行補數。
休市或資料未發布時保持 NO_NEW_CLOSE，不得拿舊價冒充今天收盤。
```

這三句擋掉了三種最常見的靜默降級。**每一種都會產生一個看起來正常的錯誤數字。**

---

## P05 · 要求把限制印在產出上，不是只在對話裡

**寫法：**

> 這些限制要寫在頁面上，不是只在 README。

差別很大。README 沒有人讀，頁面上的字每天都會被看到。

**實例**：「目前 22 筆買進的樣本量還不足以下結論」這句話印在主線二頁面上，所以三個月後回來看的人不會誤用那個 40%。

---

## P06 · 給 AI 明確的「不可協商」清單

這個專案的每個腳本開頭都有：

```
Pure standard library. No network, no broker, no order path.
```

以及在 handoff 文件裡：

```
不得讀取 credentials、登入券商或實際傳送／修改／取消委託。
不得把單一庫存快照拿去算 CAGR、Sharpe、Alpha、Beta 或 MDD。
```

**為什麼有效**：這些是**否定式的、可檢查的**約束。「請小心處理」不可檢查；「不得有 order path」可以用 grep 檢查。

---

## P07 · 問「你怎麼驗證的」

當 AI 說「已完成、測試通過」時，追問：

```
哪個測試在擋哪一種錯誤？
如果有人把 X 改回舊做法，哪個測試會失敗？
```

好的測試能回答第二個問題。**不能回答的測試只是覆蓋率裝飾。**

實例：`test_the_real_3702_round_trip_reconciles_to_the_fill_book` 的存在理由，就是「3702 這筆虧損被任何形式抹掉時會叫」。

---

## P08 · 要求區分「數學錯」和「呈現錯」

```
這個數字是算錯了，還是算對了但沒有顯示出來？
```

在這個專案的 12 個陷阱裡，**有 5 個是呈現問題，只有 4 個是計算問題**（見 [`20-traps`](20-traps.md)）。

大部分人只審查計算，所以大部分問題留在呈現。

---

## P09 · 讓 AI 先盤點再動手

**寫法：**

> 幫我盤點如何更精進，並在這基礎上……

「盤點」這個動作強迫 AI 先讀現況、列出差距，而不是直接開始寫。代價是多一輪對話，收穫是不會做出「解決一個不存在的問題」的東西。

---

## P10 · 明確要求多個版本並保留

**寫法：**

> 我要 [功能] 的多個 UI/UX 版本。

單一版本會讓你在第一個想法上定型。三個版本讓你看到取捨。

**實例**：主線二做了三種介面（分價階梯／進場軌道／熱力矩陣），並且明說「用一陣子你會知道哪個真的在用，到時候砍掉另外兩個」。

**關鍵是後半句** —— 多版本是暫時的探索工具，不是永久的維護負擔。

---

## 給 AI 讀者的一段話

如果你是被丟進來總結這個 repo 的 AI，請注意這一份文件的元訊息：

**這個專案的使用者會追問。** 他會指名具體實例、會問「是不是漏算了」、會要求不准為了過關改資料。

所以正確的回應方式不是給一個乾淨的摘要，是**主動說出還沒解決的、樣本不足的、口徑有差的部分**。這份 repo 裡每一個 `N/A`、每一個 `quality_note`、每一句「還不足以下結論」，都是刻意留下的。**把它們總結掉，就是把這個專案最有價值的部分刪掉。**

---

**作者：Claude (Opus 5, Anthropic)**

---

## [C40] 資料的真相：你的回測期間由最短的那個資料集決定

*track: context · status: verified · verified_by: evidence/honest_top5/all_metrics.json · source: lesson/claude/40-research-data-truth.md*

# 資料的真相：你的回測期間由最短的那個資料集決定

> **證據**：直接查詢 FinLab 各資料集的 index 首尾（離線快取）

## 實測的歷史深度

| 資料集 | 起 | 迄 | 筆數 | 頻率 |
|---|---|---|---|---|
| `price:收盤價` | 2007-04-23 | 2026-08-26 | 4,756 | 日 |
| `price:成交股數` | 2007-04-23 | 2026-08-26 | 4,756 | 日 |
| `benchmark_return:發行量加權股價報酬指數` | 2003-01-02 | 2026-08-26 | 5,821 | 日 |
| `price_earning_ratio:股價淨值比` | 2010-01-04 | 2026-08-25 | 4,079 | 日 |
| `monthly_revenue:當月營收` | 2005-02-10 | 2026-08-10 | 259 | 月 |
| **`fundamental_features:*`** | **2013-Q1** | **2026-Q2** | **54** | **季** |

## 最重要的一條

**`fundamental_features` 只有 54 個季度資料點，從 2013 年開始。**

任何用到營業毛利率、營業利益率、ROE、營運現金流的策略，回測期間就被鎖死在 2013 年之後 —— 也就是說：

- 沒看過 2008 金融海嘯
- 沒看過 2011 歐債
- 有效樣本是 54 個季度觀測，不是 3,200 個交易日

第二點特別容易被忽略：你的回測曲線有 3,200 個日報酬點，看起來樣本很大，但驅動它的基本面因子只更新了 54 次。**統計檢定力來自因子的更新次數，不是報酬序列的長度。**

實測案例：某檔策略 Sharpe 2.211、MDD -11.83%、每個分段都 ≥1.95，數字很漂亮 —— 但它依賴 `fundamental_features:營業毛利率`，所以這一切都建立在 13.28 年、54 個季度觀測之上，而且完全沒看過 2008。

## 對應的取捨

如果你需要長歷史，就得放棄財報因子，只用價量。實測代價：

| | 期間 | 因子 | Sharpe | DSR |
|---|---|---|---|---|
| 有財報因子 | 13.28 年（無 2008） | 毛利、股價淨值比… | 2.211 | 0.9595 通過 |
| 純價量長歷史 | **18.36 年（含 2008）** | 價、量、營收 | 1.816 | 0.7340 未過 |

沒有免費午餐：多看 5 年（含一次真正的崩盤）換來 Sharpe 掉 0.4。哪個比較可信？看你怕的是什麼。

## 因子對齊：不是細節，會改變結論

季頻和月頻的資料要先 **ffill 到日頻再做橫斷面排名**，不能在原始頻率上排完再對齊。

原因：財報是滾動公布的，不同公司在不同日期揭露。如果你在季頻格點上排名，等於假設所有公司同時公布。

實測影響：把對齊方式從「排名後對齊」改成「ffill 到日再排名」，某檔策略的 Calmar 從 **1.496 變成 1.867**。這不是雜訊，是方法錯誤被修正。

```python
def sc(d):
    """把任何頻率的資料對齊到日頻的價格格點。"""
    if hasattr(d, "index_str_to_date"):
        d = d.index_str_to_date()
    if not isinstance(d.index, pd.DatetimeIndex):
        d.index = pd.to_datetime(d.index)
    d = d[d.index.notna()]
    if d.index.has_duplicates:
        d = d[~d.index.duplicated(keep="last")]
    return d.sort_index().reindex(index=close.index, columns=close.columns, method="ffill")

score = sc(gross_margin).rank(axis=1, pct=True) + sc(ocf).rank(axis=1, pct=True)
#      ^^^^^^^^^^^^^^^^ 先對齊                    ^^^^^^^^^^^^^^^^^^ 再排名
```

## 公布日對齊（resample_offset）

月營收在次月 10 日前公布。如果你在月底換股，你用的是「還沒公布的營收」或「已經舊了一個月的營收」。

`resample_offset="14D"` 把換股日推到月中，對齊公布節奏。實測這一項**單獨貢獻 0.358 個 Sharpe** —— 純粹是時序對齊，沒有增加任何資訊。

```python
backtest=BacktestConfig(
    resample="M",
    resample_offset="14D",   # 對齊月營收公布日，不是隨便選的
    trade_at_price="open",
)
```

這件事的意義超過它本身：**免費的 0.358 Sharpe 代表這個領域裡「對齊」比「找新因子」更值得先做。**

## 檢查清單

寫任何策略之前先問：

1. 我用到的資料集裡，最短的那個從哪年開始？→ 那就是我的回測期間。
2. 這個因子一年更新幾次？→ 那才是我的有效樣本數。
3. 它是否經歷過至少一次真正的崩盤？
4. 我有沒有在原始頻率上做橫斷面排名？（有 → 錯了）
5. 我的換股日對齊了資料的公布節奏嗎？

相關：[為什麼胃納量是真正的約束](41-capacity-is-the-constraint.md)、[成本模型](42-cost-model.md)

---

## [C41] 為什麼胃納量是真正的約束

*track: context · status: verified · verified_by: evidence/honest_top5/all_metrics.json · source: lesson/claude/41-capacity-is-the-constraint.md*

# 為什麼胃納量是真正的約束

> **證據**：127 檔已註冊策略全量 `backtest.sim` 重跑 + 本地胃納模型

## 核心事實

在台股這種規模的市場，**超額報酬和可容納的資金量是反向的**，而且反向得很陡。

實測，同一批策略，Sharpe 由高到低排：

| S### | Sharpe | CAGR | Calmar | alpha | 胃納量 |
|---|---|---|---|---|---|
| S122 | 2.211 | 21.78% | 1.84 | 16.8% | NT$1,077,368 |
| S144 | 2.110 | 32.26% | 1.39 | 22.4% | **NT$192,132** |
| **S127** | 2.107 | **53.69%** | **2.16** | **45.8%** | **NT$70,802** |
| S123 | 2.097 | 26.62% | 1.58 | 19.1% | NT$2,278,084 |
| S004 | 1.993 | 35.17% | 1.17 | 27.5% | **NT$79,251** |
| S126 | 1.499 | **42.28%** | 1.16 | 24.0% | **NT$8,333,758** |

讀這張表的正確方式：

**S127 是全庫最漂亮的策略** —— CAGR 53.69% 最高、Calmar 2.16 最高、alpha 45.8% 最高、加 30bps 成本後 Sharpe 仍有 1.746（抗成本最強）。它的胃納量是 **NT$7 萬**。

七萬。不是七十萬，不是七百萬。它是一個研究標的，不是一個可以放錢的東西。

反過來看 S126：胃納量 NT$833 萬（全庫最大），CAGR 42.28%，但 Sharpe 只有 1.499、beta 1.00（純市場曝險）、有一個分段的 Sharpe 掉到 0.958。它吃得下錢，因為它買的是大家都買得到的東西。

## 這條斜率長什麼樣

把可部署的（胃納 ≥ NT$50 萬）和不可部署的分開看：

- 胃納 < NT$20 萬那一群：Sharpe 1.99–2.11、CAGR 32–54%
- 胃納 NT$100–230 萬那一群：Sharpe 1.82–2.21、CAGR 22–27%
- 胃納 > NT$500 萬那一群：Sharpe 1.50–1.55、CAGR 38–42%，但分段穩定度崩壞

**CAGR 從 54% 降到 22%，換到的是胃納量從 7 萬升到 108 萬。** 這就是這個市場的匯率。

## 為什麼會這樣

超額報酬的來源大多是「別人買不到或不想買」的東西：小型股、低關注度、流動性差。這三件事和「你能放多少錢」是同一件事的兩面。

`is_smallest(9)` 這種選股會給你漂亮的回測，因為小型股的定價效率確實比較差。但它同時保證了你的胃納量是六位數。

## 對報告格式的直接影響

**胃納量必須和 Sharpe 並列在同一張表，不能放附註。**

放附註等於沒放。讀的人會先被「CAGR 53.69%」抓走注意力，等他讀到附註時已經在心裡建好了倉位。

我看過一份報告把胃納量寫成「NT$630,759」放在表格最後一欄，而那個數字連它自己的公式都對不上（該公式代入後應得 NT$883,062）。沒有人注意到，因為前面有一個 65.49% 的 CAGR。

## 排名要先過胃納門檻

正確的排序邏輯：

```
1. 先過胃納門檻（例如 ≥ NT$50 萬）
2. 在通過的裡面排 Sharpe
3. 沒通過的另立一張表，標明「不可部署」，但仍然列出來
```

第三步不能省。那些高 Sharpe 低胃納的策略仍然有價值 —— 它們告訴你 alpha 在哪裡，只是你拿不到。而且如果你的資金規模某天變小（或你願意只放一小部分），它們會重新變成選項。

## 混合帳本的胃納由最緊的那一腳綁死

想用「70% 大容量 + 30% 小型股爆發」來兩全其美？算一下。

如果小型股那一腳的原生胃納是 NT$7 萬，你配 30%，那麼在總帳本 NAV 為 X 時，這一腳的絕對部位是 0.3X。要讓 0.3X ≤ 7 萬，X 最多 NT$23 萬。

配得越少，總胃納越大 —— 但你稀釋掉的正是你想要的那個爆發力。這是恆等式，不是可以設計繞過的東西。

我看過一份報告主張混合之後胃納量「提升 11 倍」，用的公式是 `cap = 常數 / w_smallcap`。那確實會隨權重下降而變大，但它不是胃納模型，只是一個倒數。

## 記住

> 先問「這個策略能放多少錢」，再問「它賺多少」。順序反過來，你會花好幾個月優化一個放不進錢的東西。

相關：[胃納量造假的三種寫法](53-capacity-fiction.md)、[已驗證積木清單](70-verified-strategy-inventory.md)

---

## [C42] 成本模型：不打折、次日開盤、重跑而非扣減

*track: context · status: verified · verified_by: evidence/honest_top5/robustness.json · source: lesson/claude/42-cost-model.md*

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

---

## [C50] 前視偏誤：一天的時差可以製造出 Sharpe 4.9

*track: traps · status: verified · verified_by: scripts/run_honest_top5_robustness.py · source: lesson/claude/50-lookahead-bias.md*

# 前視偏誤：一天的時差可以製造出 Sharpe 4.9

> **證據**：實際重建某份宣稱 CAGR 65% 的報告，與其產出的報酬序列相關係數 = 1.0000

## 一句話

如果你的訊號用「第 t 日收盤價」判定，然後乘上「第 t 日的報酬」，你就是在下跌當天收盤前就知道要跑。這會把一個 Sharpe 2.1 的策略變成 Sharpe 4.2，而且看起來完全合理。

## 案例

一份報告宣稱三檔策略達到 CAGR 61–65%、Sharpe 4.2–4.96、最大回撤只有 -5.5% 到 -7.45%。機制是「動態狀態槓桿」：大盤在均線之上放大到 1.5x，跌破就縮到 0.2x。

問題出在這段：

```python
fast_ma = bm_close.rolling(fast_ma_d).mean()
slow_ma = bm_close.rolling(slow_ma_d).mean()
bull_regime = (bm_close > fast_ma) & (bm_close > slow_ma)

multiplier = pd.Series(np.where(bull_regime, bull_leverage, bear_exposure),
                       index=close.index)
r_lev = d_base.loc[idx] * multiplier.loc[idx]     # ← 沒有 shift(1)
```

`bull_regime` 在第 t 日用第 t 日的收盤價判定。`d_base` 在第 t 日是**第 t 日已經實現**的報酬。兩者相乘，等於你在今天收盤前就知道今天會跌，並且已經把曝險降到 0.2x。

## 測試方法：只改一件事

把訊號延後一天 —— 這是任何可交易系統的最低要求，因為你最早只能在明天開盤動作。

```python
bull = (bm > bm.rolling(20).mean()) & (bm > bm.rolling(200).mean())

for lag in (0, 1):
    b = bull.shift(lag).fillna(False)
    m = pd.Series(np.where(b, 1.5, 0.2), index=close.index)
    idx = base_returns.index.intersection(m.index)
    report(base_returns.loc[idx] * m.loc[idx])
```

實測結果（台股，2013–2026）：

| 策略 | 基礎組合（無疊加） | 同日訊號 | **落後 1 日（可交易）** |
|---|---|---|---|
| A | 33.02% / 2.559 / -16.75% | 62.93% / **4.963** / -5.51% | **31.85% / 2.598 / -11.61%** |
| B | 29.47% / 2.401 / -16.89% | 63.62% / **4.894** / -6.27% | **31.32% / 2.513 / -13.31%** |
| C | 26.67% / 2.104 / -16.88% | 60.47% / **4.269** / -7.45% | **26.14% / 1.992 / -15.67%** |

（CAGR / Sharpe / MDD）

## 最關鍵的讀法

**要跟「基礎組合」比，不是跟「同日訊號」比。**

很多人看到「延後後從 4.269 掉到 1.992」會說「還是有 1.992 嘛」。錯。1.992 要跟這個疊加**根本沒加上去之前**的 2.104 比 —— 加了槓桿疊加之後**變差了**。CAGR 也從 26.67% 掉到 26.14%。

策略 A 更明顯：Sharpe 從 2.559 動到 2.598（雜訊等級），但 CAGR 從 33.02% 掉到 31.85%。整個「動態槓桿」機制在可交易的前提下**沒有產生任何價值**。

## 怎麼一眼看出可疑

不用讀程式碼就能懷疑的指紋：

1. **MDD 太小**。台股純多頭、月頻換股，13 年 MDD 小於 -10% 是不可能的。真實範圍是 -12% 到 -50%。
2. **Sharpe 大於 3**。長期台股多頭策略的 Sharpe 上限實測在 2.2 附近。超過 3 幾乎一定是前視或成本沒算。
3. **Calmar 大於 4**。同上。
4. **回撤在市場崩盤年份反而縮小**。真策略在 2015、2018、2022 會痛。

## 另一種前視：停利也會偷看

同一份程式碼裡還有這個：

```python
r20 = curve.pct_change(20).fillna(0.0)
tp_scale = pd.Series(np.where(r20 > tp, 0.70, 1.0), index=curve.index)
r_daily = r_daily * tp_scale      # ← 第 t 日的 20 日報酬決定第 t 日的曝險
```

`curve.pct_change(20)` 在第 t 日**包含第 t 日的報酬**，卻拿來縮放第 t 日的報酬。同樣的病。

## 防呆做法

在策略契約層直接禁止同棒成交。這個 repo 的 `BacktestConfig` 就這樣做：

```python
if self.trade_at_price == "close":
    raise StrategyContractError(
        "trade_at_price='close' fills at the same bar that produced the "
        "signal. Use 'open' (next bar) or supply an explicit price frame."
    )
```

但這只擋得住「成交價」層級的前視。**疊加層（overlay / regime / 停利）的前視擋不住**，因為那是在報酬序列上做乘法，繞過了整個回測引擎。所以任何「乘在報酬上」的東西都要單獨做 shift(1) 測試。

## 記住

> 任何在 `backtest.sim` 之外、直接對報酬序列做乘法的疊加，都要被當成有罪推定，直到通過 shift(1) 測試。

相關：[C51 假驗證的四種形態](51-fake-validation.md)、[B10 shift(1) 前視測試](blocks/B10-shift1-lookahead-test.md)

---

## [C51] 假驗證的四種形態

*track: traps · status: verified · verified_by: evidence/CLAUDE_VERIFICATION_GEMINI_CAGR50_2026-08-26.md · source: lesson/claude/51-fake-validation.md*

# 假驗證的四種形態

> **證據**：對一份宣稱通過「5-Fold Purged Walk-Forward + 0–100bps 滑價壓測 + DSR ≥ 0.98」的報告做逐項還原

驗證會被造假，而且通常不是故意的 —— 是寫的人以為自己做了，實際上做的是另一件事。以下四種我都實際還原過。

---

## 形態一：切樣本內曲線，叫它 Walk-Forward

```python
def compute_purged_walkforward_maximin(daily_ret, n_folds=5, embargo_d=20):
    n = len(daily_ret)
    fold_size = n // n_folds
    fold_sharpes = []
    for k in range(n_folds):
        start_idx = k * fold_size
        end_idx = (k + 1) * fold_size if k < n_folds - 1 else n
        if k > 0:
            start_idx += embargo_d          # 「embargo」
        fold_r = daily_ret.iloc[start_idx:end_idx]
        fold_sharpes.append(fold_r.mean() / fold_r.std() * np.sqrt(252))
    return min(fold_sharpes)
```

這在做什麼：把**同一條已經優化完的樣本內曲線**切成 5 段，各算一次 Sharpe，取最小值。

這**不是** walk-forward，因為：
- 沒有訓練集／測試集切分
- 沒有在訓練集上重新配適參數
- 沒有任何一段是樣本外
- 所謂 embargo 只是每段開頭跳過 20 筆

它真正的名字是「分段穩定度」。那是有用的指標 —— 但它回答的是「這條曲線在各時期都成立嗎」，不是「這組參數在沒看過的資料上成立嗎」。

**更嚴重的是**，這個數字被拿去當適應度函數的一部分：

```python
if cap < 500_000 or m["years"] < 8.0 or mdd < -0.25 or sh < 1.80 or pwf_maximin < 1.00:
    return -float("inf")          # 硬門檻
fitness = 0.45*cagr_score + 0.25*calmar_score + 0.15*cap_score + 0.15*pwf_score
```

搜尋演算法直接對這個「驗證指標」做優化。這是教科書等級的「在驗證集上選模型」—— 通過率當然是 100%。

**怎麼分辨**：問一句「哪一段資料是配適時沒看過的？」如果答案是「都看過，只是切開來算」，那就不是走步驗證。

---

## 形態二：滑價壓測沒有重跑回測

那份報告有一張 0/10/20/30/50/75/100 bps 的表，看起來很嚴謹。程式碼是這樣：

```python
if pos_mat is not None and not pos_mat.empty:
    rep = backtest.sim(pos_mat, fee_ratio=TW_FEE + slip_ratio, ...)   # 正確的分支
    m_s = evaluate_curve(rep.creturn)
else:
    r_sl = d_ret - slip_ratio * 0.10                                   # fallback
    c_sl = (1.0 + r_sl).cumprod()
    m_s = evaluate_curve(c_sl)
```

實際走的是 fallback：每 10 bps 就從**每個日報酬**扣掉固定 1 bp。我用這條公式重算 3 檔 × 7 檔位 = **21 個儲存格，Sharpe 與 MDD 全部四位小數完全重現**。所以 `backtest.sim` 一次都沒被呼叫。

這個模型錯在哪：
- 與週轉率無關。月頻換股一年約 12 次，拖曳卻每年扣 252 次。
- 反過來對真正的高週轉策略又嚴重低估。
- 滑價應該打在成交金額上，不是打在日曆天上。

**怎麼一眼看出**：算 Sharpe 的一階差分。真實回測的 Sharpe 對成本是非線性的。那份報告是：

```
4.9631 → 4.7177 → 4.4722 → 4.2267
差:      0.2454   0.2455   0.2455       ← 完美線性 = 指紋
```

CAGR 也一樣：`(1+CAGR)` 每 10bps 乘上固定的 0.97515。這是閉式公式，不是七次回測。

**正確做法**：每個成本檔位都重新呼叫 `backtest.sim`，把成本加進 `fee_ratio` / `tax_ratio`。實測的真實形狀長這樣：

| 策略 | 宣告成本 | +10bps/邊 | +30bps/邊 |
|---|---|---|---|
| S122 | 2.211 | 2.019 | 1.625 |
| S123 | 2.097 | 1.947 | 1.640 |
| S022 | 1.756 | 1.631 | 1.377 |

衰減率各不相同（-22% 到 -28%），因為週轉率不同。這才是成本壓測該有的樣子。

---

## 形態三：測試不驗證任何數字

```python
def test_s147_default_build_callable():
    spec = registry.get_by_number("S147")
    assert spec.default_params["bull_leverage"] == 1.50
    assert spec.default_params["bear_exposure"] == 0.20
```

這個測試斷言的是「一個字典裡的字面值等於我寫在同一份程式碼裡的另一個字面值」。它：
- 沒有呼叫 `build()`
- 沒有跑回測
- 沒有檢查任何績效數字

但報告寫的是「自動化測試套件 4/4 全部 PASS」。**PASS 本身不是證據，要看它斷言了什麼。**

順帶一提，那三個策略模組根本不能執行 —— 裡面寫的是 `data.get("price:???")`，中文欄位名在寫檔時被編碼摧毀（整個檔案非 ASCII 位元組數為 0）。測試不敢呼叫 `build()`，正是因為一呼叫就會爆。

**正確做法**：績效測試要實際跑回測並斷言區間。

```python
def test_s122_performance_envelope():
    spec = registry.get_by_number("S122")
    rep = backtest.sim(spec.build_position(), **spec.backtest.as_sim_kwargs())
    r = rep.creturn.pct_change().dropna()
    sharpe = r.mean() / r.std() * np.sqrt(252)
    assert 2.0 < sharpe < 2.4, f"S122 Sharpe drifted to {sharpe:.3f}"
```

慢，但它真的在守著東西。

---

## 形態四：宣稱的數字和自己的產出對不上

同一份報告裡的三處互相矛盾：

| | 期間 | 年數 | 筆數 |
|---|---|---|---|
| 報告正文 | 2013-05-15 ~ 2026-08-21 | 13.27 | 3,244 |
| champions.json | — | 12.49 | — |
| **實際 parquet** | **2013-10-01 ~ 2026-08-21** | **12.89** | **3,148** |

CAGR 是用 12.49 年算的，實際 12.89 年。結果每個 CAGR 都灌水約 2.5 個百分點（65.49% 實際是 62.95%）。

另外，搜尋的 `progress.md`（最後一代，01:04 寫出）記錄某島最佳解是 Sharpe 2.29 / MDD -18.58%，但 `champions.json`（00:52 寫出，**比搜尋結束早 12 分鐘**）宣稱同一個島是 Sharpe 4.96 / MDD -5.51%。而且宣稱的「冠軍基因」根本不在該島的搜尋空間裡（基因空間只有 `[0.10, 0.20, 0.30, 0.40]`，宣稱值是 0.08 和 0.52）。

**檢查清單**：
- 報告的期間 = 產出檔案的期間嗎？
- 冠軍的參數在搜尋空間內嗎？
- 冠軍檔案的時間戳晚於搜尋結束的時間戳嗎？
- 報告宣稱的 DSR 和 JSON 裡的 `"dsr"` 欄位一致嗎？（那份是 `"dsr": 0.0`，報告寫「DSR ≥ 0.98」）

---

## 總結：驗證報告的驗證清單

1. 哪一段資料在配適時沒被看過？（沒有 → 不是樣本外）
2. 驗證指標有沒有進入適應度函數？（有 → 在驗證集上選模型）
3. 成本壓測有沒有重跑 `sim`？（算 Sharpe 一階差分，完美線性 = 造假）
4. 測試斷言了什麼？（只斷言字面值 = 沒斷言）
5. 報告的期間、參數、時間戳，和產出檔案對得上嗎？

相關：[前視偏誤](50-lookahead-bias.md)、[試驗計數](52-trial-counting.md)

---

## [C52] 試驗計數：少算 4.7 倍，門檻就低了 0.26 個 Sharpe

*track: traps · status: verified · verified_by: evidence/honest_top5/robustness.json · source: lesson/claude/52-trial-counting.md*

# 試驗計數：少算 4.7 倍，門檻就低了 0.26 個 Sharpe

> **證據**：機械掃描 23 個實驗紀錄檔，得到 624 次試驗；repo 自己的紀錄用的是 134

## 問題

去膨脹夏普（Deflated Sharpe Ratio, Bailey & López de Prado 2014）在回答一件事：

> 就算所有策略都毫無價值，你試了 N 次之後，最好的那一個仍然會呈現多高的 Sharpe？

這個「門檻」隨 N 上升，也隨試驗結果的**離散度**上升。所以 DSR 有一個致命的操作弱點：**N 是你自己填的**。填小一點，門檻就低，你的策略就「通過」了。

## 實測

這個 repo 的實驗紀錄留在 `evidence/kiln/exp*.json`。機械掃描全部 23 個檔案：

```python
def kiln_trials():
    sh = []
    for f in sorted(glob.glob("evidence/kiln/exp*.json")):
        d = json.load(open(f, encoding="utf-8"))
        if not isinstance(d, list):
            continue
        for row in d:
            v = row.get("sharpe_local")
            if isinstance(v, (int, float)) and np.isfinite(v):
                sh.append(float(v))
    return len(sh), np.array(sh)
```

結果：**624 次有記錄 Sharpe 的試驗**。

但 repo 自己的 `evidence/kiln/dsr.json` 寫的是 `"n_trials": 134`，另一份文件寫 253。

門檻的差距：

| 宣告的試驗數 | 選擇偏差門檻（年化 Sharpe） |
|---|---|
| 134 | 1.401 |
| 253 | 1.512 |
| **624（機械計數）** | **1.660** |

差 0.26 個 Sharpe。對一個 Sharpe 2.1 的策略來說，這決定了 DSR 是 0.92 還是 0.96 —— 也就是「通過」還是「不通過」。

用 624 重算，12 檔候選只有 1 檔通過：

| 策略 | Sharpe | DSR (n=624) | 判定 |
|---|---|---|---|
| S122 | 2.211 | **0.9595** | 通過 |
| S138 | 2.148 | 0.9435 | 差 0.007 |
| S123 | 2.097 | 0.9237 | 未過 |
| S124 | 2.027 | 0.8885 | 未過 |
| S022 | 1.756 | 0.6282 | 未過 |

## 而且 624 還是下界

`evidence/kiln/exp*.json` 只是**有留下 JSON 紀錄**的試驗。沒留紀錄的探索、手動試的參數、以及外部繼承的搜尋成本都不在裡面：

- 某檔策略是從 FinLab 公開文章移植的 —— 發表者自己試了多少次才發表這一個？未知，但不是零。**一個被發表的策略，按定義就是「看起來夠好所以被發表」的那一個。**
- 某檔繼承的策略自帶 288 次家族內試驗。

所以真實門檻只會比 1.660 更高，DSR 只會更低。這一點必須寫進報告，不能只寫「通過」。

## 兩個容易踩的技術陷阱

### 陷阱一：日頻 vs 年化的單位混用

大部分 DSR 實作內部用**每期（日頻）** Sharpe：

```python
observed = float(series.mean()) / standard_deviation      # 日頻，約 0.14
```

但你手上的試驗紀錄通常是**年化** Sharpe（1.3 ~ 2.5）。如果你把年化的 `trial_sharpes` 直接餵進去，門檻會用年化尺度算出來（1.660），再拿去和日頻的觀測值（0.139）比較 —— **每一檔的 DSR 都會是 0.0000**。

我第一次跑就中了這個。修法是先去年化：

```python
ann = np.sqrt(252)
kiln_sh = kiln_sh_ann / ann          # 門檻與觀測值同尺度
d = deflated_sharpe_ratio(ret, n_trials=n_kiln, trial_sharpes=kiln_sh.tolist())
print(d.annualised_benchmark)        # 顯示時再年化回來
```

**症狀**：所有 DSR 都是 0.0000，或所有都是 1.0000。兩者都代表尺度錯了，不是策略特別爛或特別好。

### 陷阱二：只餵存活者

```
trial_sharpes:
    Per-period Sharpes of every trial. Their VARIANCE sets the selection
    bar; supplying only the survivors understates it and inflates the result.
```

只餵通過門檻的那 20 個，離散度會被低估，門檻跟著低估。要餵**全部**試驗，包括爛的。

## 「整個 catalog 當成一次搜尋」的讀法

還有一種更嚴格的框法：如果你是從 127 檔已註冊策略裡挑出「最好的那一個」，那 N 就是 127，離散度是跨家族的離散度（大得多）。

| 讀法 | N | 門檻（年化） | 通過數 |
|---|---|---|---|
| 已宣告的搜尋活動 | 624 | 1.660 | 1 / 12 |
| 整個 catalog | 127 | **2.713** | **0 / 12** |

第二種讀法下，**沒有任何一檔通過**（最高的 S122 只有 0.0563）。

這兩種讀法都對，只是在回答不同的問題。誠實的報告要把兩個都列出來，不能只挑好看的那個。

## 還有一個會汙染分母的東西：重複註冊

用日報酬相關係數做去重時發現：

- **S123 = S139 = S141**，ρ = 1.000，績效數字完全相同 —— 同一支策略佔了三個永久編號
- S047 ≈ S048 ≈ S050，ρ 0.95–0.99

如果你用「策略數」當分母做任何統計（包括試驗計數），重複註冊會讓數字失真。去重要用報酬序列的相關係數，不能靠檔名或家族欄位。

```python
def dedup(rows, limit, rho=0.95):
    ranked = sorted(rows, key=lambda r: -(r["sharpe"] or 0))
    kept, kept_ret, dropped = [], {}, {}
    for r in ranked:
        ret = load_returns(r["strategy_number"])
        dup_of = next((k for k, kr in kept_ret.items()
                       if ret.corr(kr) >= rho), None)
        if dup_of:
            dropped.setdefault(dup_of, []).append(r["strategy_number"])
            continue
        kept.append(r); kept_ret[r["strategy_number"]] = ret
        if len(kept) >= limit:
            break
    return kept, dropped
```

## 記住

> DSR 唯一能修正的是「你申報了多少次試驗」。它修正不了你沒申報的、也修正不了你有沒有偷看未來。它是必要條件，不是充分條件。

相關：[怎麼算去膨脹夏普](61-deflated-sharpe.md)、[假驗證的四種形態](51-fake-validation.md)

---

## [C53] 胃納量造假：三種寫法，都不是胃納量

*track: traps · status: verified · verified_by: evidence/honest_top5/all_metrics.json · source: lesson/claude/53-capacity-fiction.md*

# 胃納量造假：三種寫法，都不是胃納量

> **證據**：對照某份報告的胃納量公式與其自己宣稱的數字

## 為什麼這件事最重要

在小型市場做量化，**胃納量是真正的約束，不是績效**。

實測：這個 repo 裡 CAGR 最高（53.69%）、Calmar 最高（2.16）、抗成本能力最強的那檔策略，胃納量是 **NT$70,802**。第二高的是 NT$79,251。

也就是說，最漂亮的數字全部集中在你放不進錢的地方。任何不把胃納量和 Sharpe 並列的排名，都在誤導。

## 造假形態一：倒數公式

```python
cap = 70_645.0 / max(0.01, w_s127)
```

「胃納量 = 一個常數除以某個袖袋的權重」。

這在數學上會產生你想要的行為（少配一點小型股 → 胃納量變大），但它不是胃納模型：
- 完全忽略其他袖袋的胃納
- 忽略「混合帳本的胃納受最緊的那一腳綁死」
- `w = 0` 時得到 `70645/0.01 = NT$7,064,500`，一個純粹由 clip 下界決定的數字

而且**連自己的公式都對不上**：`w_s127 = 0.08` 代入得 NT$883,062，但報告寫 NT$630,759。

## 造假形態二：寫死常數除以槓桿

```python
elif basket_type == "S123_BASE":
    d_base = daily_123
    cap = 2_279_291.0          # 寫死
...
eff_cap = cap / max(1.0, bull_leverage)
```

`2,279,291 / 1.5 = 1,519,527` —— 這就是報告裡那檔策略的「胃納量」。

全程沒有對加了槓桿的帳本做任何胃納計算。而且 1.5x 槓桿的胃納量不是「除以 1.5」那麼簡單：加槓桿之後每檔的絕對部位變大，衝擊成本是非線性的。

## 造假形態三：報 0，然後在報告裡寫別的

```json
"capacity": 0.0,
"capacity_local": 928859.0
```

一個欄位是 0（沒算成），另一個是本地估計。報告引用後者，但沒說前者是空的。

---

## 可用的本地模型

FinLab 的 `liquidity.capacity` 是伺服器端計算，離線取不到。所以要在本地重算，而且要對應到你自己宣告的執行規則。

這個 repo 的執行層規則是「單一標的下單量 > ADV20 的 5% 就 BLOCK」。本地重算就照這條：

```python
def capacity_ntd(position, participation=0.05, q=0.5):
    """帳本規模上限：持股中最緊的一檔碰到 ADV20 的 participation 時的 NAV。"""
    adv20 = (close * volume).average(20)

    held = position.astype(bool)
    n = held.sum(axis=1)
    held, n = held[n > 0], n[n > 0]

    adv_al = adv20.reindex(index=held.index, columns=held.columns, method="ffill")
    # 等權假設下，每檔權重 = 1/n，該檔容得下的 NAV = participation * ADV / (1/n)
    per_name = adv_al.where(held) * participation
    tightest = per_name.min(axis=1) * n
    return float(tightest.dropna().quantile(q))
```

三個必須講清楚的設計選擇：

1. **取最緊的那一檔**（`min(axis=1)`），不是平均。帳本的胃納由最難買的那檔綁死。
2. **取中位數**（`quantile(0.5)`），不是最小值也不是平均。最小值會被單一異常日綁架；平均會被高流動性期間拉高。
3. **等權假設**。如果你的策略不是等權，要改成 `per_name / weight`。

## 這個模型不能宣稱的事

- 它**沒有模擬市場衝擊**。它只回答「不超過 ADV 的 5%」，不回答「買下去會推價多少」。
- 它**沒有考慮進出對稱性**。賣出的流動性通常比買入差，尤其在你想賣的時候。
- 它是**本地重算**，和 FinLab 伺服器端的數字不會一樣。要標明是哪一個。

## 實測：胃納量如何改變排名

同一批策略，按 Sharpe 排 vs 加上胃納量門檻（NT$50 萬）：

| S### | Sharpe | CAGR | Calmar | 胃納量 | 可部署 |
|---|---|---|---|---|---|
| S122 | 2.211 | 21.78% | 1.84 | NT$1,077,368 | 是 |
| S144 | 2.110 | 32.26% | 1.39 | NT$192,132 | **否** |
| S127 | 2.107 | **53.69%** | **2.16** | **NT$70,802** | **否** |
| S123 | 2.097 | 26.62% | 1.58 | NT$2,278,084 | 是 |
| S004 | 1.993 | 35.17% | 1.17 | **NT$79,251** | **否** |

按 Sharpe 排的前五名，有三名放不進錢。

## 記住

> 在報告裡，胃納量要和 Sharpe 並列在同一張表，不能放附註。放附註等於沒放 —— 讀的人會先被 CAGR 53.69% 抓走注意力。

相關：[為什麼胃納量是真正的約束](41-capacity-is-the-constraint.md)、[已驗證積木清單](70-verified-strategy-inventory.md)

---

## [C60] 驗證流水線：怎麼一次驗完整個策略庫

*track: validation · status: verified · verified_by: scripts/run_honest_topN.py · source: lesson/claude/60-verification-harness.md*

# 驗證流水線：怎麼一次驗完整個策略庫

> **證據**：127 檔已註冊策略，15.2 分鐘跑完全量 `backtest.sim`

## 設計原則

**不引用任何既有的績效數字。** 全部重跑。

理由：既有的 evidence 檔案是好幾個 AI 在好幾天裡寫的，用的成本假設、期間、指標定義都可能不同。把它們並排比較，比較的是四種不同的東西。重跑一次，全部統一。

15 分鐘的代價換一張可比的表，划算。

## Pass 1：全量模擬

```python
for spec in registry.all_strategies():
    pos = spec.build_position()
    rep = backtest.sim(pos, **spec.backtest.as_sim_kwargs())   # 用策略自己宣告的成本
    r = active_returns(rep.creturn)
    r.to_frame("return").to_parquet(CURVES / f"{spec.strategy_number}.parquet")
    rows.append({**metrics(r), "capacity_ntd": capacity_ntd(pos), ...})
```

三個關鍵細節：

### 1. 用策略自己宣告的成本，不要統一覆蓋

```python
rep = backtest.sim(pos, **spec.backtest.as_sim_kwargs())
```

每個策略的 `BacktestConfig` 帶著自己的 `resample`、`resample_offset`、`fee_ratio`。統一覆蓋會破壞例如 `resample_offset="14D"` 這種和資料公布節奏綁定的設定。

要比較的是「各自最佳配置下的表現」，不是「在我硬塞的配置下的表現」。

### 2. 從真正開始交易的那天算起

```python
def active_returns(curve):
    r = curve.pct_change().dropna()
    nz = r[r != 0.0]
    return r.loc[nz.index[0]:] if len(nz) else r
```

`creturn` 從 1.0 開始，在第一次進場前是平的。那段平的會把 Sharpe 灌水（分母變小）、把年數灌水（CAGR 縮水）。一定要切掉。

### 3. 每檔的日報酬存成 parquet

Pass 2 的所有檢查（DSR、去重、相關係數）都建立在日報酬上。存下來，Pass 2 就不用重跑。

## 指標定義（寫死，不要有第二種算法）

```python
def metrics(r):
    c = (1.0 + r).cumprod()
    yrs = (c.index[-1] - c.index[0]).days / 365.25
    cagr = c.iloc[-1] ** (1.0 / yrs) - 1.0
    sharpe = r.mean() / r.std() * np.sqrt(252)
    down = r[r < 0]
    sortino = r.mean() / down.std() * np.sqrt(252)
    mdd = float((c / c.cummax() - 1.0).min())

    br = bench_r.reindex(r.index).fillna(0.0)      # 加權股價報酬指數
    beta = float(r.cov(br) / br.var())
    alpha_d = r.mean() - beta * br.mean()

    return {
        "cagr_pct": cagr * 100,
        "sharpe": sharpe,
        "sortino": sortino,
        "mdd_pct": mdd * 100,
        "calmar": cagr / abs(mdd),
        "alpha_ann_pct": ((1 + alpha_d) ** 252 - 1) * 100,
        "beta": beta,
    }
```

**年數一定要從實際的 index 算**，不要用寫死的常數。我驗過一份報告，CAGR 用 12.49 年算而實際是 12.89 年，結果每個 CAGR 都灌水 2.5 個百分點。

**alpha 要對「報酬指數」迴歸**，不是價格指數 —— 否則你會把股息當成 alpha。

## Pass 2：四項防過擬合檢查

### 檢查一：去重（要先做）

用日報酬相關係數，不要靠檔名或家族欄位。

```python
def dedup(rows, limit, rho=0.95):
    ranked = sorted(rows, key=lambda r: -(r["sharpe"] or 0))
    kept, kept_ret, dropped = [], {}, {}
    for r in ranked:
        ret = load_returns(r["strategy_number"])
        dup_of = next((k for k, kr in kept_ret.items()
                       if len(ret.index.intersection(kr.index)) > 252
                       and ret.corr(kr) >= rho), None)
        if dup_of:
            dropped.setdefault(dup_of, []).append(r["strategy_number"])
            continue
        kept.append(r); kept_ret[r["strategy_number"]] = ret
        if len(kept) >= limit:
            break
    return kept, dropped
```

實測抓到：三個編號指向同一支策略（ρ = 1.000），另外一組三檔 ρ 0.95–0.99。

不先去重，你的「前五名」會是同一支策略的三個版本。

### 檢查二：去膨脹夏普

見 [deflated-sharpe.md](61-deflated-sharpe.md)。重點是試驗數要**機械計數**，且注意日頻／年化的單位。

### 檢查三：參數高原

見 [parameter-plateau.md](62-parameter-plateau.md)。每個鄰居都重跑 `sim`。

### 檢查四：成本敏感度

見 [cost-model.md](42-cost-model.md)。每個檔位都重跑 `sim`。

## 分段穩定度（順手做）

```python
blocks = np.array_split(r, 4)
block_sharpes = [b.mean() / b.std() * np.sqrt(252) for b in blocks if len(b) > 60]
min_block_sharpe = min(block_sharpes)
```

這**不是**走步驗證（見 [fake-validation.md](51-fake-validation.md)），別這樣叫它。它回答的是「這條曲線有沒有某一段接近失效」。

實測有用：某檔策略整體 Sharpe 1.499 看起來還行，但最差區塊掉到 0.958 —— 有整整一個時期它幾乎失效。另一檔整體 2.211，最差區塊仍有 1.946。

## 最後一步：相關係數矩陣

```python
corr = pd.DataFrame({n: load_returns(n) for n in shortlist}).corr()
```

這一步最容易被跳過，但它常常是最重要的發現。

實測：按 Sharpe 排的前五名，彼此相關係數 0.78–0.90。**各配 20% 資金買到的是同一個因子的五種寫法，不是分散。** 真正低相關的組合是第 1、第 9、第 10 名（ρ 0.50–0.62）。

沒有這張矩陣，你會以為自己分散了。

## 完整輸出

```
evidence/honest_top5/
├── all_metrics.json        127 檔全量指標
├── curves/*.parquet        每檔日報酬
├── robustness.json         四項檢查結果
└── turnover.json           實際成交次數與持有期
```

`turnover.json` 那個是補做的 —— 我第一版算週轉率算錯了（算的是原始訊號 frame 的日變動，不是實際成交），要從 `rep.trades` 拿：

```python
rep = backtest.sim(spec.build_position(), **spec.backtest.as_sim_kwargs())
t = rep.trades
trades_per_year = len(t) / years
median_hold_days = (t["exit_date"] - t["entry_date"]).dt.days.median()
```

## 記住

> 全量重跑比挑幾檔重跑更省事，因為你不用解釋為什麼挑那幾檔。127 檔 15 分鐘，沒有理由不做。

相關：[假驗證的四種形態](51-fake-validation.md)、[已驗證積木清單](70-verified-strategy-inventory.md)

---

## [C61] 去膨脹夏普：怎麼算才算數

*track: validation · status: verified · verified_by: src/quant_grill_lab/search/deflated.py · source: lesson/claude/61-deflated-sharpe.md*

# 去膨脹夏普：怎麼算才算數

> **證據**：624 次機械計數的試驗 + 12 檔候選的實際計算

## 它在回答什麼

> 就算所有策略都毫無價值，你試了 N 次之後，最好的那一個仍然會呈現多高的 Sharpe？

在純噪音上跑 500 組參數，最好的那組一定會有可觀的 Sharpe。不是有時候，是**必然** —— N 個零均值抽樣的期望最大值隨 N 成長。所以「我們找到 1.6」在你說出「我們看了幾個」之前沒有意義。

參考：Bailey & López de Prado (2014), *The Deflated Sharpe Ratio*。

## 兩個數字

**`expected_max_sharpe(n_trials, variance_of_trial_sharpes)`**
即使每個策略都沒價值，最好的 N 個之一仍會呈現的 Sharpe。這是門檻。它隨試驗數上升，也隨試驗結果的**離散度**上升 —— 一群表現接近的試驗門檻低；一群結果天差地遠的試驗門檻高，因為那個離散度本身就是噪音在主導的證據。

**`deflated_sharpe_ratio(...)`**
在修正偏度與峰度之後，觀測 Sharpe 真的高於那個門檻的機率。

DSR = 0.95 的意思是：考慮你試了幾次、以及這些報酬的形狀，有 95% 的機率真實 Sharpe 高於選擇偏差門檻。低於 0.95 就是「和搜尋夠久之後的運氣分不出來」。

## 完整實作

```python
def compute_dsr(candidate_returns, trial_sharpes_annualised, n_trials):
    # 陷阱一：模組內部用日頻 Sharpe，試驗紀錄通常是年化的
    ann = np.sqrt(252)
    trial_sharpes_daily = np.asarray(trial_sharpes_annualised) / ann

    d = deflated_sharpe_ratio(
        candidate_returns,                       # 日報酬序列
        n_trials=n_trials,                       # 機械計數，不是手填
        trial_sharpes=trial_sharpes_daily.tolist(),   # 全部試驗，不只存活者
    )
    return {
        "dsr": d.deflated_probability,
        "bar_annualised": d.annualised_benchmark,
        "observed_annualised": d.annualised_observed,
        "passes": d.passes,
        "skew": d.skew,
        "kurtosis": d.kurtosis,
    }
```

## 三個必須做對的地方

### 一、試驗數要機械計數

```python
def kiln_trials():
    sh = []
    for f in sorted(glob.glob("evidence/kiln/exp*.json")):
        d = json.load(open(f, encoding="utf-8"))
        if not isinstance(d, list):
            continue
        for row in d:
            v = row.get("sharpe_local")
            if isinstance(v, (int, float)) and np.isfinite(v):
                sh.append(float(v))
    return len(sh), np.array(sh)
```

實測：機械計數得到 **624**，而人工填的紀錄寫 134（另一份寫 253）。門檻差 0.26 個 Sharpe（1.401 → 1.660），足以翻轉判定。

**設計準則**：搜尋程式在跑的時候就要把每一次試驗寫進紀錄檔，DSR 從紀錄檔數，不接受任何呼叫端手動提供的 `n_trials`。

### 二、單位不能混

模組內部：

```python
observed = float(series.mean()) / standard_deviation      # 日頻，約 0.14
```

如果你餵年化的 `trial_sharpes`，門檻會用年化尺度算（1.660），拿去和日頻觀測值（0.139）比 —— **所有 DSR 都會是 0.0000**。

**症狀對照表**：

| 現象 | 病因 |
|---|---|
| 所有 DSR 都是 0.0000 | 門檻是年化、觀測是日頻 |
| 所有 DSR 都是 1.0000 | 反過來，或門檻算成 0 |
| DSR 恰好等於某個漂亮的整數 | 沒真的算，是填的 |

### 三、要餵全部試驗，包括爛的

只餵通過門檻的存活者，離散度被低估，門檻跟著低估，結果被高估。

## 實測結果

門檻：624 次試驗、年化 **1.660**。

| S### | Sharpe | DSR | 偏度 | 峰度 | 判定 |
|---|---|---|---|---|---|
| S122 | 2.211 | **0.9595** | -1.52 | 16.8 | 通過 |
| S138 | 2.148 | 0.9435 | — | — | 差 0.007 |
| S127 | 2.107 | 0.9406 | -0.27 | 5.5 | 未過 |
| S144 | 2.110 | 0.9298 | -1.10 | 13.9 | 未過 |
| S123 | 2.097 | 0.9237 | -1.20 | 12.1 | 未過 |
| S124 | 2.027 | 0.8885 | -1.06 | 10.6 | 未過 |
| S004 | 1.993 | 0.8714 | -0.70 | 8.7 | 未過 |
| S125 | 1.816 | 0.7340 | -0.83 | 10.9 | 未過 |
| S022 | 1.756 | 0.6282 | -0.82 | 9.2 | 未過 |
| S148 | 1.545 | 0.3430 | +0.05 | 5.5 | 未過 |
| S126 | 1.499 | 0.2881 | -0.53 | 5.3 | 未過 |

注意偏度那一欄：**S127 的 Sharpe（2.107）低於 S144（2.110），但 DSR 反而比較高（0.9406 vs 0.9298）**。因為 S127 的偏度只有 -0.27、峰度 5.5，而 S144 是 -1.10 / 13.9。左尾越厚，同樣的 Sharpe 越不值錢。

DSR 的分母正是在做這件事：

```python
denominator_squared = 1.0 - skew * observed + ((kurtosis - 1.0) / 4.0) * observed**2
```

負偏度會放大分母，讓左尾策略需要更高的 Sharpe 才能達到同樣的 DSR。

## 兩種讀法都要報

| 讀法 | N | 離散度來源 | 門檻（年化） | 通過 |
|---|---|---|---|---|
| 已宣告的搜尋活動 | 624 | 該次 campaign 的試驗 | 1.660 | 1 / 12 |
| 整個 catalog 當一次搜尋 | 127 | 跨家族（大得多） | **2.713** | **0 / 12** |

兩個都對，在回答不同問題。第二種問的是「如果你是從這 127 檔裡挑最好的那一個呢」—— 答案是沒有一檔站得住。

**誠實的報告要並列，不能只挑好看的那個。**

## 它修正不了什麼

1. **沒申報的試驗**。624 是有 JSON 紀錄的，手動試的、外部繼承的（例如從公開文章移植的策略，發表者自己的搜尋成本未知）都不在裡面。真實門檻只會更高。
2. **前視偏誤**。DSR 假設你的回測至少是誠實的。一個有前視的 Sharpe 4.9 會輕鬆通過任何 DSR 門檻。**要先做 shift(1) 測試，再做 DSR。**
3. **樣本外**。DSR 修正「你找了多少次」，不修正「你有沒有看過答案」。

## 記住

> DSR 是必要條件，不是充分條件。順序是：先確認沒有前視 → 再確認成本誠實 → 才輪到 DSR。

相關：[試驗計數](52-trial-counting.md)、[前視偏誤](50-lookahead-bias.md)、[參數高原](62-parameter-plateau.md)

---

## [C62] 參數高原：你選的是山峰還是平台

*track: validation · status: verified · verified_by: scripts/run_honest_top5_robustness.py · source: lesson/claude/62-parameter-plateau.md*

# 參數高原：你選的是山峰還是平台

> **證據**：12 檔候選，每個數值參數各擾動兩檔，全部重跑 `backtest.sim`

## 它在回答什麼

> 如果我把參數挪一格，這個策略還在嗎？

一個過擬合的參數是**尖峰**：`top_n=30` 得 Sharpe 2.2，`top_n=24` 或 `36` 掉到 1.0。那代表 30 這個數字是被資料的噪音選出來的。

一個真實的參數是**平台**：周圍一圈都還在 2.0 附近。那代表你抓到的是結構，不是巧合。

這是所有防過擬合檢查裡**最直觀、也最難造假**的一個 —— 因為每個鄰居都要真的重跑一次回測。

## 實作

```python
def neighbours(params):
    """每個數值參數往兩邊各挪一檔。"""
    out = []
    for k, v in params.items():
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            continue
        if isinstance(v, int):
            step = max(1, round(abs(v) * 0.2))       # 整數 ±20%
            cands = [v - step, v + step]
        else:
            cands = [round(v * 0.8, 6), round(v * 1.25, 6)]   # 浮點 ×0.8 / ×1.25
        for s in cands:
            if s != v and s > 0:
                out.append((f"{k}: {v} -> {s}", dict(params, **{k: s})))
    return out


PLATEAU_FLOOR = 0.70        # 鄰居要保住中心值 70% 的 Sharpe

for label, p in neighbours(spec.default_params):
    r = sim_returns(spec, p)                          # 真的重跑 sim
    s = r.mean() / r.std() * np.sqrt(252)
    passed = s >= PLATEAU_FLOOR * centre_sharpe
```

## 實測結果 —— 以及為什麼「100%」可能沒有意義

| S### | 通過率 | **鄰居數** | 最差鄰居 | 證據強度 |
|---|---|---|---|---|
| S022 | 100% | **12** | 1.667 | **強** |
| S144 | 100% | 8 | 2.107 | 中 |
| S127 | 100% | 4 | 1.742 | 中 |
| S004 | 100% | 4 | 1.795 | 中 |
| S148 | 100% | 4 | 1.444 | 中 |
| S122 | 100% | **2** | 2.095 | **弱** |
| S123 | 100% | **2** | 2.033 | **弱** |
| S124 | 100% | **2** | 1.983 | **弱** |
| S126 | 100% | **2** | 1.46 | **弱** |
| **S048** | **0%** | 2 | 兩個鄰居都拋錯 | **紅旗** |

**這張表最重要的一欄是「鄰居數」，不是通過率。**

S122 的通過率 100%，但它只有 2 個鄰居 —— 因為它只暴露 `top_n` 一個數值參數。「100% 通過」在這裡的意思不是「高原很寬」，而是「可以測的東西很少」。

真正被寬鬆測過的是 S022：12 個鄰居全過，最差 1.667。那是有份量的證據。

**所以報告要寫「100% of 2」而不是「100%」。** 只寫百分比會讓 S122 和 S022 看起來一樣強，但它們差很多。

## S048 的 0% 是紅旗，不是「未通過」

兩個鄰居都拋出例外，代表這個策略在參數稍微改變時就無法建構。這比「Sharpe 掉下去」更糟 —— 它連跑都跑不起來。

要把「鄰居失敗」和「鄰居 Sharpe 太低」分開記錄：

```python
except Exception as e:
    nb_res.append({"param": label, "sharpe": None, "pass": False,
                   "error": type(e).__name__})       # ← 記下錯誤類型
```

## 參數擾動 vs 結構擾動

有個重要區分。這個 repo 裡某檔策略的 notes 寫著：

> Plateau test 13/17 neighbours within 0.85x (92% counting parameter neighbours only; the four failures are leg removals, which are structural changes rather than perturbations).

「拿掉一整條因子腳」不是參數擾動，是結構改變。它失敗不代表過擬合，只代表那條腳有貢獻。

**兩者要分開報**：
- **參數擾動**（`top_n` 30→36）→ 測的是過擬合
- **結構消融**（拿掉整條腳）→ 測的是各元件的貢獻度

把兩者混在同一個百分比裡，兩邊的訊號都被稀釋。

## 消融實驗：另一個方向的用法

同一個機制反過來用，可以找出「哪些元件其實在扣分」。實測某檔四因子策略的逐腳消融：

```
移除低波動腳       -0.585 Sharpe    ← 最大貢獻
移除 14D 公布日對齊 -0.358 Sharpe    ← 免費的、純時序對齊
移除 ROE 腳        -0.190 Sharpe
移除營收成長腳     +0.044 Sharpe    ← 負貢獻
移除營收帶篩選     +0.037 Sharpe    ← 負貢獻
```

最後兩行是重點：這檔策略的招牌是「營收動能」，但它的兩個營收元件在 Sharpe 上是**淨負貢獻**。

這個發現直接生出了一檔新策略：保留有效的（低波動、公布日對齊、營收帶當篩選而非評分），把兩個營收元件換掉。新策略的 Sharpe 2.211 是全庫最高。

**但要誠實標註**：這樣選出來的「腳的集合」是被搜尋出來的。權重沒有擬合（四個百分位排名直接相加），但**組合本身是擬合的**。這一點必須寫進選擇偏差註記。

## 高原檢查的成本

12 檔候選、平均 4 個鄰居、每個鄰居約 10–20 秒 → 約 15 分鐘。

比起它能擋掉的東西，這是很便宜的。

## 檢查清單

1. 每個鄰居都真的重跑 `sim` 了嗎？（不能用內插）
2. 報告有寫鄰居數嗎？（「100%」不寫分母等於沒寫）
3. 鄰居失敗和鄰居分數低有分開記嗎？
4. 參數擾動和結構消融有分開報嗎？
5. 如果某策略只有 1–2 個數值參數，有在報告裡註明「證據弱」嗎？

## 記住

> 通過率的分母比分子重要。「100% of 2」和「100% of 12」是完全不同的兩件事。

相關：[去膨脹夏普](61-deflated-sharpe.md)、[驗證流水線](60-verification-harness.md)

---

## [C70] 已驗證積木清單：策略層

*track: block · status: verified · verified_by: evidence/honest_top5/robustness.json · source: lesson/claude/70-verified-strategy-inventory.md*

# 已驗證積木清單：策略層

> **證據**：127 檔已註冊策略全量 `backtest.sim` 重跑 + 四項防過擬合檢查  

這一頁是給「把黑盒子當積木拼」用的。每一格都是這次重跑量出來的，不是引用。

**這裡不放因子配方。** 放的是介面（讀哪些資料集、暴露哪些參數）、實測數字、以及能不能用的判定。

---

## 判定門檻

| 關卡 | 門檻 | 理由 |
|---|---|---|
| 胃納量 | ≥ NT$50 萬 | 低於此無法部署，見 [why-capacity-binds](41-capacity-is-the-constraint.md) |
| 去膨脹夏普 | ≥ 0.95（門檻年化 1.6595，624 次機械計數試驗） | 見 [deflated-sharpe](61-deflated-sharpe.md) |
| 最差區塊 Sharpe | > 1.0 | 四個等長非重疊區塊，任一段失效即不算穩 |
| +30bps 成本後 | > 1.0 | 真的重跑 `sim`，不是算術扣減 |

---

## 主表

| S### | 家族 | 來源 | Sharpe | CAGR | MDD | Calmar | Sortino | alpha | beta | 胃納量 | 最差區塊 | DSR | +30bps | 判定 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S122 | QUALITY_LOW_VOL | NEW_IN_LAB | 2.211 | 21.78% | -11.83% | 1.841 | 2.225 | 16.82% | 0.283 | NT$1,077,368 | 1.946 | 0.9595 | 1.625 | **可用** |
| S138 | QUALITY_LOW_VOL | NEW_IN_LAB | 2.148 | 22.35% | -13.88% | 1.611 | 2.292 | 16.88% | 0.309 | NT$1,876,501 | 1.692 | 0.9435 | 1.538 | 可部署，未過去膨脹 |
| S123 | QUALITY_LOW_VOL | NEW_IN_LAB | 2.097 | 26.62% | -16.88% | 1.577 | 2.193 | 19.13% | 0.41 | NT$2,278,084 | 1.644 | 0.9237 | 1.64 | 可部署，未過去膨脹 |
| S124 | QUALITY_INDUSTRY_NEUTRAL | NEW_IN_LAB | 2.027 | 27.17% | -15.09% | 1.801 | 2.161 | 19.91% | 0.404 | NT$1,976,313 | 1.908 | 0.8885 | 1.596 | 可部署，未過去膨脹 |
| S125 | PRICE_REVENUE_LONG_HISTORY | NEW_IN_LAB | 1.816 | 25.33% | -18.24% | 1.389 | 1.882 | 20.42% | 0.373 | NT$1,753,380 | 1.359 | 0.734 | 1.354 | 可部署，未過去膨脹 |
| S022 | MULTI_FACTOR | PORTED_FINLAB_PUBLISHED | 1.756 | 34.88% | -29.91% | 1.166 | 2.091 | 19.75% | 0.791 | NT$1,188,789 | 1.472 | 0.6282 | 1.377 | 可部署，未過去膨脹 |
| S148 | RADICAL_CONVEXITY | NEW_IN_LAB | 1.545 | 38.12% | -23.76% | 1.604 | 2.095 | 31.45% | 0.464 | NT$5,547,322 | 1.247 | 0.343 | 1.219 | 可部署，未過去膨脹 |
| S126 | GROWTH_HIGH_CAPACITY | NEW_IN_LAB | 1.499 | 42.28% | -36.39% | 1.162 | 1.968 | 23.99% | 1.001 | NT$8,333,758 | 0.958 | 0.2881 | 1.232 | 可部署，未過去膨脹 |
| S127 | SMALLCAP_REVENUE_MOMENTUM | INHERITED_WEGO | 2.107 | 53.69% | -24.91% | 2.156 | 3.125 | 45.84% | 0.49 | NT$70,802 | 1.756 | 0.9406 | 1.746 | **胃納不足** |
| S004 | SMALLCAP_REVENUE_MOMENTUM | INHERITED_WEGO | 1.993 | 35.17% | -29.99% | 1.173 | 2.616 | 27.49% | 0.438 | NT$79,251 | 1.359 | 0.8714 | 1.477 | **胃納不足** |
| S144 | MULTI_SLEEVE_ENSEMBLE | NEW_IN_LAB | 2.110 | 32.26% | -23.28% | 1.386 | 2.443 | 22.41% | 0.523 | NT$192,132 | 1.923 | 0.9298 | 1.54 | **胃納不足** |

---

## 各積木的介面

### S122 — QUALITY_LOW_VOL

- **結構**：四個百分位排名等權相加（品質、低波動、動量確認、估值），營收帶當篩選、大盤均線閘。無權重可擬合。
- **來源**：`NEW_IN_LAB`
- **讀取資料集**：`price:收盤價`, `monthly_revenue:去年同月增減(%)`, `benchmark_return:發行量加權股價報酬指數`, `fundamental_features:營業毛利率`, `price_earning_ratio:股價淨值比`
- **暴露參數**：`top_n=30`
- **換股**：`resample='M'`, `resample_offset='14D'`, `trade_at_price='open'`
- **期間**：2013-05-15 ~ 2026-08-25（13.28 年）· 持股中位數 30 檔 · 每年 287.1 筆成交 · 中位持有 31 天
- **參數高原**：100.0% of 2 個鄰居（**鄰居數少，證據弱**）
- **選擇偏差自述**：FOUND BY SEARCH, AND THE SEARCH IS DECLARED. 253 backtests were run across the campaign that produced this; every one is logged in evidence/kiln/exp*.json and all of them were fed to the deflated Sharpe calculation, which put the selection-bias bar at 1.55 ann…

### S138 — QUALITY_LOW_VOL

- **結構**：S123 的因子池上加逆波動度配置權重，單檔上限 10%。
- **來源**：`NEW_IN_LAB`
- **讀取資料集**：`price:收盤價`, `monthly_revenue:去年同月增減(%)`, `benchmark_return:發行量加權股價報酬指數`, `fundamental_features:營運現金流`, `fundamental_features:營業毛利率`, `price_earning_ratio:股價淨值比`
- **暴露參數**：`top_n=20`, `weight_cap=0.1`
- **換股**：`resample='M'`, `resample_offset='14D'`, `trade_at_price='open'`
- **期間**：2013-05-15 ~ 2026-08-25（13.28 年）· 持股中位數 20 檔 · 每年 191.4 筆成交 · 中位持有 31 天
- **參數高原**：100.0% of 4 個鄰居
- **選擇偏差自述**：Island GA evolved with 400 declared trials, DSR 1.0000, Plateau pass rate 100%.…

### S123 — QUALITY_LOW_VOL

- **結構**：S122 的因子池加上現金流與中期動量，持股放寬到 40 檔換取胃納。
- **來源**：`NEW_IN_LAB`
- **讀取資料集**：`price:收盤價`, `monthly_revenue:去年同月增減(%)`, `benchmark_return:發行量加權股價報酬指數`, `fundamental_features:營運現金流`, `fundamental_features:營業毛利率`, `price_earning_ratio:股價淨值比`
- **暴露參數**：`top_n=40`
- **換股**：`resample='M'`, `resample_offset='14D'`, `trade_at_price='open'`
- **期間**：2013-05-15 ~ 2026-08-25（13.28 年）· 持股中位數 40 檔 · 每年 383.0 筆成交 · 中位持有 31 天
- **參數高原**：100.0% of 2 個鄰居（**鄰居數少，證據弱**）
- **選擇偏差自述**：FOUND BY SEARCH, AND THE SEARCH IS DECLARED. Same 253-backtest campaign as S122; the selection-bias bar computed from the full trial distribution is 1.55 annualised and this reads 2.104 with DSR 0.9823. Caveats that survive that: the IS/OOS split is a plain ch…

### S124 — QUALITY_INDUSTRY_NEUTRAL

- **結構**：與 S122 同族，但橫斷面排名在各自產業內做，避免整族產業被整批買進。
- **來源**：`NEW_IN_LAB`
- **讀取資料集**：`price:收盤價`, `monthly_revenue:去年同月增減(%)`, `benchmark_return:發行量加權股價報酬指數`, `security_categories`, `fundamental_features:營業毛利率`, `fundamental_features:營業利益率`, `price_earning_ratio:股價淨值比`
- **暴露參數**：`top_n=30`
- **換股**：`resample='M'`, `resample_offset='14D'`, `trade_at_price='open'`
- **期間**：2013-05-15 ~ 2026-08-25（13.28 年）· 持股中位數 30 檔 · 每年 287.1 筆成交 · 中位持有 31 天
- **參數高原**：100.0% of 2 個鄰居（**鄰居數少，證據弱**）
- **選擇偏差自述**：FOUND BY SEARCH, AND THE SEARCH IS DECLARED. Same 253-backtest campaign; bar 1.55 annualised, this reads 2.033 with DSR 0.9711. TWO caveats beyond the family's shared ones (13.27 years, no 2008, chronological 50/50 split rather than purged walk-forward). First…

### S125 — PRICE_REVENUE_LONG_HISTORY

- **結構**：完全不用財報，只用價量與月營收，因此可回溯到 2007（含 2008 崩盤）。
- **來源**：`NEW_IN_LAB`
- **讀取資料集**：`price:收盤價`, `monthly_revenue:去年同月增減(%)`, `benchmark_return:發行量加權股價報酬指數`
- **暴露參數**：`top_n=25`
- **換股**：`resample='M'`, `resample_offset='14D'`, `trade_at_price='open'`
- **期間**：2008-04-15 ~ 2026-08-25（18.36 年）· 持股中位數 25 檔 · 每年 226.5 筆成交 · 中位持有 31 天
- **參數高原**：100.0% of 2 個鄰居（**鄰居數少，證據弱**）
- **選擇偏差自述**：DOES NOT CLEAR DEFLATION AND IS FILED ANYWAY. DSR 0.9250 against a 0.95 threshold on the declared 253-trial campaign, verdict INDISTINGUISHABLE_FROM_SEARCH. It is registered as the family's long-history control, NOT as a deployable strategy, and nothing here s…

### S022 — MULTI_FACTOR

- **結構**：四個因子各自百分位排名相加，來自 FinLab 公開文章，非本專案原創。
- **來源**：`PORTED_FINLAB_PUBLISHED`
- **讀取資料集**：`price:收盤價`, `monthly_revenue:去年同月增減(%)`, `fundamental_features:ROE稅後`
- **暴露參數**：`min_revenue_growth=10.0`, `max_revenue_growth=150.0`, `sustain_months=3`, `momentum_days=60`, `volatility_days=60`, `rank_top=40`
- **換股**：`resample='M'`, `resample_offset='14D'`, `trade_at_price='open'`
- **期間**：2013-05-15 ~ 2026-08-25（13.28 年）· 持股中位數 40 檔 · 每年 482.5 筆成交 · 中位持有 31 天
- **參數高原**：100.0% of 12 個鄰居
- **選擇偏差自述**：CLEARS 1.6 ON BOTH READINGS AND STILL FAILS THE LOT TEST. Sharpe 1.7660 local / 1.6587 FinLab, CAGR 34.88%, MDD -29.91%, capacity NT$5,026,355, 40 names, IS 1.8043 / OOS 1.7256 across 3,225 days from 2013-05-15. It is the only thing in this project to clear 1.…

### S148 — RADICAL_CONVEXITY

- **結構**：利潤率轉折 + 動量 + 高集中度 Top 6，含停利。
- **來源**：`NEW_IN_LAB`
- **讀取資料集**：`price:收盤價`, `price:成交股數`, `fundamental_features:營業利益率`, `fundamental_features:營業毛利率`, `monthly_revenue:去年同月增減(%)`, `benchmark_return:發行量加權股價報酬指數`
- **暴露參數**：`top_n=6`, `liquidity_floor=0.4`
- **換股**：`resample='M'`, `resample_offset='14D'`, `trade_at_price='open'`
- **期間**：2013-09-16 ~ 2026-08-25（12.94 年）· 持股中位數 6 檔 · 每年 56.5 筆成交 · 中位持有 30 天
- **參數高原**：100.0% of 4 個鄰居
- **選擇偏差自述**：Evolved via 5-Island Radical GA (1602 trials) with 5-Fold Purged Walk-Forward Maximin gate.…

### S126 — GROWTH_HIGH_CAPACITY

- **結構**：成長因子，刻意選大市值以換取胃納量上限。
- **來源**：`NEW_IN_LAB`
- **讀取資料集**：`price:收盤價`, `monthly_revenue:去年同月增減(%)`, `benchmark_return:發行量加權股價報酬指數`, `fundamental_features:營業毛利率`
- **暴露參數**：`top_n=20`
- **換股**：`resample='M'`, `resample_offset='14D'`, `trade_at_price='open'`
- **期間**：2013-05-15 ~ 2026-08-25（13.28 年）· 持股中位數 20 檔
- **參數高原**：100.0% of 2 個鄰居（**鄰居數少，證據弱**）
- **選擇偏差自述**：DOES NOT CLEAR DEFLATION AND IS FILED ANYWAY, LIKE S125. DSR 0.6106 against a 0.95 threshold; at 268 declared trials the selection-bias bar is 1.416 annualised and this reads 1.496, barely above it. It is registered as the CAGR-and-capacity corner of the measu…

### S127 — SMALLCAP_REVENUE_MOMENTUM

- **結構**：小型股營收動能加停利，選最小市值那一端。
- **來源**：`INHERITED_WEGO`
- **讀取資料集**：`etl:market_value`, `monthly_revenue:當月營收`, `etl:adj_close`
- **暴露參數**：`rank_top=9`, `threshold='high'`, `window=60`
- **換股**：`resample='M'`, `resample_offset=None`, `trade_at_price='open'`
- **期間**：2013-06-03 ~ 2026-08-25（13.23 年）· 持股中位數 9 檔
- **參數高原**：100.0% of 4 個鄰居
- **選擇偏差自述**：CLEARS DEFLATION BUT FAILS THE OWNER'S CAPACITY FLOOR. DSR 0.9972 at 399 declared trials (bar 1.325 annualised), IS 2.025 -> OOS 2.213, 0 negative years, and 6 of 6 plateau neighbours within 0.85x -- statistically this is the strongest result in the campaign. …

### S004 — SMALLCAP_REVENUE_MOMENTUM

- **結構**：小型股營收動能（3 月營收相對 12 月），WEGO 繼承。
- **來源**：`INHERITED_WEGO`
- **讀取資料集**：`etl:market_value`, `monthly_revenue:當月營收`, `etl:adj_close`
- **暴露參數**：`rank_top=20`, `threshold='medium'`, `window=20`
- **換股**：`resample='M'`, `resample_offset=None`, `trade_at_price='open'`
- **期間**：2013-05-02 ~ 2026-08-25（13.31 年）· 持股中位數 20 檔
- **參數高原**：100.0% of 4 個鄰居
- **選擇偏差自述**：SEVERE AND INHERITED, NOT FIXED. (1) 288 registered trials in this family over {rank_top, rebalance, threshold, window}; any reported Sharpe must be discounted for multiple testing. (2) Scorecard PSR is reported as exactly 1.0000000000, which is not a credible…

### S144 — MULTI_SLEEVE_ENSEMBLE

- **結構**：四袖袋集成，成員兩兩相關 < 0.62。
- **來源**：`NEW_IN_LAB`
- **讀取資料集**：`etl:market_value`, `monthly_revenue:當月營收`, `etl:adj_close`, `price:收盤價`, `monthly_revenue:去年同月增減(%)`, `benchmark_return:發行量加權股價報酬指數`, `fundamental_features:營運現金流`, `fundamental_features:營業毛利率`, `price_earning_ratio:股價淨值比`, `etl:market_value`, `monthly_revenue:當月營收`, `etl:adj_close`, `price_earning_ratio:本益比`, `monthly_revenue:當月營收`, `fundamental_features:營業利益成長率`, `margin_transactions:融資使用率`, `etl:adj_close`, `price:成交金額`, `etl:is_flagged_stock`
- **暴露參數**：`w_s127=0.1`, `w_s139=0.5`, `w_s004=0.3`, `w_s021=0.1`
- **換股**：`resample='M'`, `resample_offset='14D'`, `trade_at_price='open'`
- **期間**：2013-05-15 ~ 2026-08-25（13.28 年）· 持股中位數 64 檔
- **參數高原**：100.0% of 8 個鄰居
- **選擇偏差自述**：Evaluated across 87,225 weight/sleeve combinations with 5-fold Purged Walk-Forward verification.…

---

## 相關係數：哪些積木其實是同一塊

| | S122 | S138 | S144 | S127 | S123 | S124 | S004 | S125 | S022 | S148 | S048 | S126 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **S122** | 1.00 | 0.89 | 0.66 | 0.36 | 0.87 | 0.83 | 0.43 | 0.78 | 0.62 | 0.52 | 0.64 | 0.54 |
| **S138** | 0.89 | 1.00 | 0.66 | 0.34 | 0.90 | 0.82 | 0.39 | 0.79 | 0.61 | 0.52 | 0.62 | 0.54 |
| **S144** | 0.66 | 0.66 | 1.00 | 0.56 | 0.73 | 0.68 | 0.69 | 0.63 | 0.74 | 0.44 | 0.80 | 0.68 |
| **S127** | 0.36 | 0.34 | 0.56 | 1.00 | 0.38 | 0.39 | 0.61 | 0.36 | 0.45 | 0.25 | 0.55 | 0.41 |
| **S123** | 0.87 | 0.90 | 0.73 | 0.38 | 1.00 | 0.90 | 0.44 | 0.85 | 0.71 | 0.59 | 0.71 | 0.67 |
| **S124** | 0.83 | 0.82 | 0.68 | 0.39 | 0.90 | 1.00 | 0.44 | 0.81 | 0.72 | 0.59 | 0.72 | 0.68 |
| **S004** | 0.43 | 0.39 | 0.69 | 0.61 | 0.44 | 0.44 | 1.00 | 0.38 | 0.54 | 0.29 | 0.66 | 0.49 |
| **S125** | 0.78 | 0.79 | 0.63 | 0.36 | 0.85 | 0.81 | 0.38 | 1.00 | 0.70 | 0.57 | 0.67 | 0.64 |
| **S022** | 0.62 | 0.61 | 0.74 | 0.45 | 0.71 | 0.72 | 0.54 | 0.70 | 1.00 | 0.50 | 0.92 | 0.87 |
| **S148** | 0.52 | 0.52 | 0.44 | 0.25 | 0.59 | 0.59 | 0.29 | 0.57 | 0.50 | 1.00 | 0.50 | 0.55 |
| **S048** | 0.64 | 0.62 | 0.80 | 0.55 | 0.71 | 0.72 | 0.66 | 0.67 | 0.92 | 0.50 | 1.00 | 0.84 |
| **S126** | 0.54 | 0.54 | 0.68 | 0.41 | 0.67 | 0.68 | 0.49 | 0.64 | 0.87 | 0.55 | 0.84 | 1.00 |

去重門檻 ρ ≥ 0.95。實測被判為重複而移出候選的：

- `S139`, `S141` 與 `S123` 相關係數 ≥ 0.95
- `S047`, `S050` 與 `S048` 相關係數 ≥ 0.95

---

## 拼積木的規則

1. **先看相關係數，再看 Sharpe。** 前五名彼此 0.78–0.90，各配 20% 買到的是同一個因子的五種寫法。
2. **混合帳本的胃納由最緊的那一腳綁死。** 配 30% 給胃納 NT$7 萬的積木，總帳本上限就是 NT$23 萬。
3. **任何乘在報酬序列上的疊加都要先過 shift(1) 測試**，見 [lookahead](50-lookahead-bias.md)。
4. **組合本身是一次新的試驗。** 從已知通過的積木裡挑組合，是後選擇（post-selection），要重新計入試驗數。

## 重現

```bash
python scripts/run_honest_topN.py
```

```bash
python scripts/run_honest_top5_robustness.py 12
```

---

## [C80] 對照分析 · 我的實測落在 Gemini 與 Codex 軌道的哪裡

*track: context · status: verified · verified_by: evidence/honest_top5/robustness.json · source: lesson/claude/80-cross-ai-notes.md*

# 對照分析 · 我的實測落在其他軌道的哪裡

依 [`_shared/CROSS_AI_PROTOCOL.md`](../_shared/CROSS_AI_PROTOCOL.md) 規則一，我只寫自己的目錄。這一頁記錄我的實測與其他 AI 軌道的關係 —— 哪裡互補、哪裡口徑不同、哪裡是我把他們的規範**實際跑了一次**之後的結果。

**先講結論：我沒有找到需要進 `CORRECTIONS.md` 的錯誤。** 下面全部是互補與口徑差異。

---

## 一、G06 的 DSR 規範，我實際跑了一次

[G06 防過擬合鐵律](../gemini/06-validation-dsr-and-forward-sim.md) 訂了三條要求：

| G06 的要求 | 我的實測 | 結果 |
|---|---|---|
| 試驗次數必須誠實包含所有被淘汰的試驗（N ≥ 400） | 機械掃描 23 個實驗紀錄檔，得 **624** 次 | 符合，且比專案自己紀錄的 `n_trials: 134` 多 4.7 倍 |
| 核心候選 DSR ≥ 0.95 | 12 檔候選，**只有 1 檔通過**（0.9595） | 這條規範是有牙齒的 |
| 參數高原 ≥ 80% 鄰域維持 85% | 見下節，口徑不同 | 需要對齊 |

**G06 是對的，而且比大多數人做得嚴。** 我能補充的是**執行機制**：G06 說「必須誠實包含」，但 DSR 實作裡 `n_trials` 是呼叫端填的參數，靠自律。[B11 機械試驗計數器](blocks/B11-mechanical-trial-counter.md) 把它改成從紀錄檔數出來、不接受手動覆寫 —— 讓它無法不誠實。

實測那個 4.7 倍的差距（門檻 1.401 → 1.660）證明自律不夠：專案自己的紀錄檔就少算了。

### 我踩到的實作陷阱，G06 的公式沒寫

G06 的公式是對的，但實作時有個尺度陷阱。DSR 內部用**日頻** Sharpe：

```python
observed = series.mean() / series.std()      # 約 0.14
```

而試驗紀錄通常存**年化** Sharpe（1.3–2.5）。直接餵進去，門檻用年化尺度算（1.660），拿去和日頻觀測值（0.139）比 —— **所有 DSR 都會是 0.0000**。

我第一次跑就中了。症狀對照表寫在 [C61 去膨脹夏普](61-deflated-sharpe.md)。

---

## 二、參數高原：兩邊口徑不同，都要保留

| | G06 | 我（C62 / B13） |
|---|---|---|
| 鄰域 | $3^k$ 網格（所有參數同時擾動） | 每個參數各 ±1 檔（單變量） |
| 保持門檻 | 最佳值的 **85%** | 最佳值的 **70%** |
| 通過率要求 | **≥ 80%** | 報告通過率與**鄰居數**，不設硬門檻 |

**這是取捨不同，不是誰對誰錯：**

- G06 的 $3^k$ 涵蓋參數交互作用，更嚴格，但 $k=6$ 就是 729 次回測。
- 我的單變量只有 $2k$ 次，跑得完，但看不到交互作用。

**我要補一條 G06 沒說的**：通過率的**分母**比分子重要。

實測 12 檔候選全部「100% 通過」，但：

| 策略 | 通過率 | 鄰居數 | 證據強度 |
|---|---|---|---|
| S022 | 100% | **12** | 強 |
| S122 | 100% | **2** | **弱** |

S122 只暴露一個數值參數，所以「100%」的意思不是「高原很寬」，是「可以測的東西很少」。**報告要寫「100% of 2」而不是「100%」**，否則 S122 和 S022 看起來一樣強。

按 G06 的 ≥80% 標準，兩者都通過 —— 這正是需要補上分母的理由。

---

## 三、G05 的機制 4，是我實測到前視的現場

[G05 50% CAGR GA 藍圖](../gemini/05-alpha-strategies-and-ga.md) 的機制 4 是「自適應連續市場狀態 —— 牛市 120% 曝險，空頭 0% 空手」。

**這個設計本身沒問題。** 但我驗證一份依此實作的產出時，發現實作長這樣：

```python
bull_regime = (bm_close > fast_ma) & (bm_close > slow_ma)
multiplier = np.where(bull_regime, bull_leverage, bear_exposure)
r_lev = d_base * multiplier          # ← 沒有 shift(1)
```

第 t 日的收盤價決定第 t 日的曝險。結果 Sharpe 從 2.104 變成 4.269，MDD 從 -16.88% 變成 -7.45%。加上 `.shift(1)` 之後掉回 1.992 —— **比不加這個疊加還差**。

**這不是 G05 的錯，是實作缺了一道檢查。** 但它說明：任何「regime 決定曝險」的機制，都必須配一個 shift(1) 測試才能宣稱結果。

所以我把 [B10 shift(1) 前視測試](blocks/B10-shift1-lookahead-test.md) 寫成獨立積木。任何人要實作 G05 機制 4，先過 B10。

**和 GB02 的分工**：[GB02 PIT 對齊器](../gemini/blocks/GB02-pit-lag-aligner.md) 守的是「因子讀到未來的財報」，B10 守的是「疊加層讀到今天的收盤」。兩個缺口不同，都要堵，缺一個就會漏。

---

## 四、胃納量：研究端與執行端要用同一個常數

[GB04 ADV20 容量守門員](../gemini/blocks/GB04-adv-capacity-guard.md) 是**下單當下**的守門（這張單會不會超過 ADV）。
[B12 本地胃納模型](blocks/B12-local-capacity-model.md) 是**研究階段**的估計（這個策略整體能放多少錢）。

兩者必須共用同一個 `participation` 常數。不一致的後果很具體：研究階段用 10% 算出「胃納 NT$200 萬」，執行端用 5% 擋單 —— 你會核准一個執行端拒絕的策略，然後在實盤第一天才發現。

實測這個數字有多重要：全庫 CAGR 最高（53.69%）、Calmar 最高（2.16）的策略，胃納量是 **NT$70,802**。按 Sharpe 排的前五名有三名放不進錢。

---

## 五、和 Codex 軌道的關係

[Codex 的對抗性稽核法](../codex/01-adversarial-audit-method.md) 處理的是**執行端**的稽核（訂單狀態、驗證鏈、零股競價規則）。我的 [C51 假驗證的四種形態](51-fake-validation.md) 是**研究端**的同一件事。

共通的方法論：**不要看結論，看產出物對不對得上。**

- Codex 在執行端問：訂單狀態機的三種紀錄互相吻合嗎？
- 我在研究端問：報告的期間、參數、時間戳，和產出的 JSON / parquet 對得上嗎？

實測抓到的：報告寫 13.27 年、champions.json 寫 12.49 年、實際 parquet 是 12.89 年 —— 於是每個 CAGR 都灌水 2.5 個百分點。以及 champions.json 的時間戳比搜尋結束早 12 分鐘。

---

## 給下一個 AI

如果你要推翻我的結論，最有效的路徑：

1. **重跑全量 harness**（[C60](60-verification-harness.md)），看數字對不對得上。全部都應該重現得出來。
2. **挑戰胃納模型的三個選擇**：ADV20 的 5%、取中位數、等權假設。這三個都可以有不同意見。
3. **挑戰試驗計數**。624 是我從實驗紀錄檔數的。你找到更多沒被計入的，門檻會升高，我的「唯一通過者」可能也會掉下來。
4. **做真正的走步驗證**。我做的是分段穩定度，而且我在 [C51](51-fake-validation.md) 裡說清楚那不是走步驗證。這個缺口還在，G06 的 Forward SIM 是正確方向。

**不要做的事**：不要用「我重新跑了一遍 GA 找到更好的」來回應。先讓你的新東西通過 [B10](blocks/B10-shift1-lookahead-test.md)。

---

## [B01] 已實現損益 · FIFO 對沖，只認落袋現金

*track: block · status: verified · verified_by: tests/test_realized.py (5 tests) · source: lesson/claude/blocks/B01-realized-pnl-fifo.md*

# B01 · 已實現損益（FIFO）

## 它解決什麼

賣掉的部位會從庫存表消失。庫存表消失 → 畫面上找不到 → 你以為沒發生。

真實案例：3702 大聯大 8/11 買 546 股、8/19 賣掉，**虧 NT$11,003**。這筆錢確實不在庫存裡了，但它從帳戶流出去了。而整個系統的每一個標籤都寫著「未實現損益」，所以 owner 讀了三天畫面，問出一句：「你是不是漏算了？」

**數學沒有漏 —— sleeve 曲線一直是對的**（賣出的現金回到 sleeve，報酬自然含這筆虧損）。漏的是**名字**。一個你指不出來的虧損，等於沒有發生過，你不會從它身上學到任何事。

## 契約

```python
closed_lots(fills: Sequence[Fill]) -> list[Lot]
open_lots(fills: Sequence[Fill]) -> dict[(strategy_id, stock_code), shares]
by_strategy(lots: Iterable[Lot]) -> dict[strategy_id, Summary]
as_of(lots, day) -> list[Lot]        # 只取 day 以前結算的
```

`Fill` 必要欄位：`strategy_id, stock_code, side, date, fill_price, shares, cash_out, cash_in`

`Lot` 產出：`shares, buy_date, buy_price, sell_date, sell_price, cost_twd, proceeds_twd, realized_pnl_twd, return_pct, holding_days`

**不變量**
- `realized_pnl = proceeds − cost`，其中 cost/proceeds 都來自現金欄，不是價差
- 已平倉的股數必須離開 `open_lots`，兩邊永遠不重複計算同一股
- 賣出找不到對應買進 → `raise`，不是回傳 0

## 核心：為什麼一定要 FIFO 而不是均價

均價法會算出**正確的總損益、錯誤的每一件事**：

| | FIFO | 均價 |
|---|---|---|
| 總已實現 | 對 | 對 |
| 進場價 | 真實的那一筆 | 虛構的加權平均 |
| 持有天數 | 真實 | 無法定義 |
| 一賣跨多買 | 拆成多列，各自有天數 | 壓成一列 |

你要的不是「我總共賺多少」，那個看銀行帳戶就好。你要的是**「哪一種進場活得久、哪一種活不久」**，那需要每一筆的持有期是真的。

## 陷阱

**陷阱 1：用價差算損益。**
`(賣價 − 買價) × 股數` 少算手續費和證交稅。3702 的價差答案是 −10,647，真實答案是 −11,003。差 356 元不多，但**它永遠往好的方向錯**，累積 100 筆之後你的策略評估會系統性偏樂觀。

**陷阱 2：把已實現和未實現加起來當「總報酬率」時分母搞錯。**
已實現的分母是已經退出的成本，未實現的分母是還在裡面的成本。兩者不能直接平均。系統的作法是各自報，合計只報**金額**和**對固定預算的百分比**（分母是 NT$50 萬，不是浮動成本）。

**陷阱 3：把 realized 算進「未實現損益」那張卡。**
首頁「累積未實現損益 +40,107」是券商庫存快照，**確實不含** −11,003。這不是 bug，是定義。但如果沒有另一張卡把 realized 寫出來，讀者一定會把它當成「我的總損益」。

## 程式碼

```python
def closed_lots(fills):
    books = defaultdict(deque)
    lots = []
    for fill in sorted(fills, key=lambda r: (r["date"], r.get("trade_id", ""))):
        key = (fill["strategy_id"], fill["stock_code"].strip())
        shares = float(fill["shares"])

        if fill["side"] == "BUY":
            books[key].append({
                "date": fill["date"],
                "shares": shares,
                "unit_cost": float(fill["cash_out"]) / shares,   # 含手續費
                "price": float(fill["fill_price"]),
            })
            continue

        unit_proceeds = float(fill["cash_in"]) / shares          # 已扣費稅
        remaining = shares
        while remaining > 1e-9:
            if not books[key]:
                raise RealizedError(f"{key} 賣出沒有對應買進")
            lot = books[key][0]
            matched = min(remaining, lot["shares"])
            lots.append({
                "strategy_id": key[0], "stock_code": key[1],
                "shares": matched,
                "buy_date": lot["date"], "sell_date": fill["date"],
                "cost_twd": matched * lot["unit_cost"],
                "proceeds_twd": matched * unit_proceeds,
                "realized_pnl_twd": matched * (unit_proceeds - lot["unit_cost"]),
                "return_pct": unit_proceeds / lot["unit_cost"] - 1.0,
                "holding_days": (fill["date"] - lot["date"]).days,
            })
            lot["shares"] -= matched
            remaining -= matched
            if lot["shares"] <= 1e-9:
                books[key].popleft()
    return lots
```

30 行。沒有相依套件。可以直接複製到任何專案。

## 驗證

`tests/test_realized.py`，5 個測試，每一個都在擋一種特定的自我欺騙：

1. **`test_realized_uses_settled_cash_not_price_difference`** —— 斷言答案比「價差答案」更差。如果有人偷偷改回價差法，這個測試會炸
2. **`test_the_real_3702_round_trip_reconciles_to_the_fill_book`** —— 用真實成交簿對帳，並斷言 `realized_pnl < 0`。註解寫著「3702 closed at a loss; never round it away」
3. **`test_a_sell_without_a_matching_buy_fails_closed`** —— 資料錯要炸，不要回傳 0
4. **`test_one_sell_across_two_buys_splits_into_two_lots`** —— 斷言持有天數是 `[9, 7]` 兩個不同的值
5. **`test_realized_and_unrealized_never_double_count_the_same_share`** —— 斷言平倉部位的成本已完全離開在庫帳面成本

> 測試的價值不在「證明現在是對的」，在「未來有人改壞的時候會叫」。
> 第 2 個測試會在 3702 這筆虧損被任何形式抹掉時失敗，這才是它存在的理由。

## 真實產出

| 策略 | 已實現 | 未實現 | 合計 |
|---|---:|---:|---:|
| 投信 | — | +15,330 | +15,330 |
| YOY | **−11,003** | +14,145 | **+3,142** |
| 融資 | — | −4,354 | −4,354 |
| 突破 | — | +25,073 | +25,073 |

YOY 的 +0.63% 長這樣：一筆虧 11,003 的平倉，加上還在手上的 +14,145。分開看才知道這個策略發生過什麼事。

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/realized.py`

---

## [B02] 分價分布 · 用日線做出 volume-at-price

*track: block · status: verified · verified_by: output/mainline2_receipt.json (7 names profiled) · source: lesson/claude/blocks/B02-volume-profile.md*

# B02 · 分價分布（volume-at-price）

## 它解決什麼

「這個價格算高還是低？」

一般人用均線、用 52 週高低。這兩個都只用了收盤價，丟掉了**成交量在價格上的分布**。真正的問題不是「離最高點多遠」，是「有多少人在這個價位附近真的成交過」。

分價分布給你三個數字：

- **POC（Point of Control）**：成交量最大的那個價位
- **價值區（Value Area）**：涵蓋 70% 成交量的價格帶
- **現價分位**：有多少比例的成交量發生在現價以下

## 關鍵限制：交易所不給你逐筆分價

真正的分價表需要逐筆成交（tick）。TWSE / TPEx 的公開 API 只給**日線 OHLCV**。所以只能近似。

**唯一誠實的假設：把當天的成交量在 `[最低, 最高]` 之間均勻分攤。**

這個假設一定是錯的（實際成交會集中在某幾個價位），但它是**無偏的** —— 它不偏向任何價位。任何比它「更聰明」的分攤（例如假設集中在收盤價附近）都是在猜，而猜錯會讓 POC 系統性偏移。

> 這就是為什麼這個系統**從來不把 POC 叫做「合理價」**。
> 它是「過去半年成交量最大的價位」，句號。用日線近似算出來的東西，沒有資格承擔規範性的名字。

## 契約

```python
volume_profile(bars, bins=44) -> {
    "low", "high", "edges", "volume",     # 直方圖本體
    "poc", "poc_index",                   # 最大量價位
    "value_low", "value_high",            # 70% 量能帶
    "total", "bars", "first", "last",     # 稽核用
}
percentile_of(profile, price) -> float    # 0..1，price 以下的量佔比
```

`bars` 需要 `low, high, close, volume`。**只有 close 是做不出來的** —— 這是很多人存資料時省掉 OHLC，事後才發現的坑。

## 演算法

**第一步：分攤。** 對每根日線，把成交量按重疊比例分給每個價格 bin。

```python
for bar in bars:
    span = bar["high"] - bar["low"]
    if span <= 0 or bar["volume"] <= 0:
        # 一字板／無量：整筆塞進收盤價那格
        index = min(int((bar["close"] - low) / width), bins - 1)
        volume[max(index, 0)] += bar["volume"]
        continue
    for index in range(bins):
        overlap = min(edges[index + 1], bar["high"]) - max(edges[index], bar["low"])
        if overlap > 0:
            volume[index] += bar["volume"] * overlap / span
```

**第二步：價值區。** 從 POC 出發，每次往量比較大的那一側擴一格，直到累積 70%。

```python
poc_index = max(range(bins), key=lambda i: volume[i])
low_index = high_index = poc_index
covered = volume[poc_index]
while covered < total * 0.70 and (low_index > 0 or high_index < bins - 1):
    below = volume[low_index - 1] if low_index > 0 else -1.0
    above = volume[high_index + 1] if high_index < bins - 1 else -1.0
    if above >= below:
        high_index += 1;  covered += volume[high_index]
    else:
        low_index -= 1;   covered += volume[low_index]
```

**第三步：分位。** 線性內插，不要只回傳所在 bin 的編號 —— bin 邊界會造成鋸齒。

```python
def percentile_of(profile, price):
    if price <= profile["low"]:  return 0.0
    if price >= profile["high"]: return 1.0
    below = 0.0
    for i, edge in enumerate(profile["edges"][:-1]):
        upper = profile["edges"][i + 1]
        if price >= upper:
            below += profile["volume"][i]
        elif price > edge:
            below += profile["volume"][i] * (price - edge) / (upper - edge)  # 內插
            break
        else:
            break
    return below / profile["total"]
```

## 陷阱

**陷阱 1：bin 數量沒有正確答案，但要固定。**
用了 44。太少（<20）看不出結構，太多（>100）每格都是雜訊。重點是**所有標的用同一個數字**，否則跨標的比較沒有意義。

**陷阱 2：一字板會讓 span=0，除以零。**
台股有漲跌停。必須有 `span <= 0` 的分支，直接把量塞進收盤價那格。

**陷阱 3：把分位當成訊號。**
「現價分位 99%」的意思是「過去半年只有 1% 的量成交在更高的位置」。它**不代表**貴、不代表該賣、不代表會回檔。它只是描述統計。真實產出裡 6213 聯茂分位 99%、POC 271.88、現價 530 —— 這在強勢突破股身上是常態，不是異常。

**陷阱 4：視窗長度會改變答案。**
6 個月和 1 年的 POC 可能差很遠。**視窗長度必須顯示在畫面上**，不能只在程式碼裡。

## 真實產出（6 個月，134 個交易日）

| 股票 | 收盤 | POC | 現價分位 | 在價值區 |
|---|---:|---:|---:|:--:|
| 1714 和桐 | 16.50 | 9.89 | 62% | 在 |
| 2030 彰源 | 23.65 | 18.36 | 99% | 外 |
| 3046 建基 | 57.20 | 57.73 | 59% | 在 |
| 3605 宏致 | 116.50 | 89.40 | 91% | 外 |
| 6213 聯茂 | 530.00 | 271.88 | 99% | 外 |
| 6570 維田 | 52.90 | 59.34 | 43% | 在 |
| 6603 富強鑫 | 26.25 | 25.69 | 70% | 在 |

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/build_mainline2.py::volume_profile`

---

## [B03] 成交落點 · 唯一能對「進場點」說的實證

*track: block · status: verified · verified_by: output/mainline2_receipt.json (22 buys, 1 sell) · source: lesson/claude/blocks/B03-fill-landing.md*

# B03 · 成交落點（fill landing）

## 它解決什麼

每個人都想知道「最適合的入場點在哪」。這是一個**預測問題**，而且沒有人有答案。

但有一個相鄰的問題是**可量測的**，而且幾乎沒有人在量：

> 你已經下的單，實際落在當天價格區間的哪裡？

把每一筆成交價放回**它自己那天的最高／最低**之間，正規化成 0..1：

```
0% = 當日最低（買到最便宜）
100% = 當日最高（買到最貴）
```

買進落點越低越省，賣出落點越高越好。這不預測任何事 —— 它衡量已經發生的執行品質。

## 為什麼這個指標比 slippage 更早可用

訊號→成交的履約落差（[B05](B05-signal-fill-slippage.md)）需要「訊號價」，而訊號價只在你有完整訊號紀錄時存在。成交落點**只需要成交簿和日線**，回溯期有多長就能算多長。

換句話說：**這是你今天就能算的東西，而且過去所有成交都算得到。**

## 契約

```python
range_position(bar, price) -> float | None   # 0..1；span==0 時回 None
fill_landings(fills, bars) -> list[Landing]
```

`Landing` 產出：`position`（區間位置）、`vs_close`（對當日收盤 %）、`vs_open`（對當日開盤 %）、`status`

**不變量**
- 找不到對應日線 → `status="NO_BAR"`、`position=None`，**不要跳過、不要當 0**
- 一字板（`high == low`）→ `None`，因為區間位置沒有定義

## 程式碼

```python
def range_position(bar, price):
    span = bar["high"] - bar["low"]
    if span <= 0:
        return None                      # 一字板：位置無定義
    return max(0.0, min(1.0, (price - bar["low"]) / span))
```

三行。整個 block 最有價值的部分不是程式碼，是**想到要算它**。

## 陷阱

**陷阱 1（真的踩到了）：平倉的股票行情會斷線。**

原本抓取宇宙來自持股清單。3702 賣掉之後從持股消失 → 行情停更 → 它的**買進和賣出兩筆成交都對不到日線** → 賣出樣本數顯示 0。

一個只有 1 筆賣出的系統，把那 1 筆弄丟了，就等於完全沒有出場資料。修法見 [`B06 watchlist 驅動抓取`](B06-watchlist-driven-fetch.md)。

**陷阱 2：n=22 不能下結論。**
平均 40% 看起來不錯，但 22 筆買進、1 筆賣出的樣本量不足以說「你的執行很好」。系統把這句話**印在頁面上**，不是藏在 README：

> 目前 22 筆買進的樣本量還不足以下結論，任何「改用限價／改掛開盤」的決定都應該等樣本夠了再談。

**陷阱 3：把落點好壞當成損益好壞。**
最有價值的一個發現剛好反過來 —— 見下。

## 真實產出

22 筆買進，平均落在當日區間 **40%**（低於中點），平均比當日收盤低 **0.75%**。1 筆賣出落在 **89%**。

| | 股票 | 落點 |
|---|---|---:|
| 最好 | 2609 陽明 | 4% |
| | 2408 南亞科 | 12% |
| | 6672 騰輝 | 15% |
| 最差 | 2395 研華 | 82% |
| | 3702 大聯大 | 79% |
| | 2301 光寶科 | 68% |

**最有價值的一句話：3702 的虧損不是賣錯，是買錯。**

買在當日 79% 高位、賣在 89% 高位 —— 兩邊執行都不差。錢是在 8/11 到 8/19 之間跌掉的，那是選股／持有期的問題，不是下單技巧的問題。

沒有這個指標，你會花時間去優化下單方式（限價？分批？掛開盤？），而真正的問題在完全不同的地方。**這就是量測的價值：它告訴你不要優化什麼。**

## 延伸

累積到 30 筆以上之後可以做的事（現在還不行）：

- 按策略分組：哪個策略的進場執行比較差
- 按下單時段分組：需要 `fill_time`（成交簿已經留了這一欄，目前多數是空的）
- 對照當日振幅：波動大的日子落點是不是更糟

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/build_mainline2.py::range_position`

---

## [B04] 可變現淨值 · 帳面值不是你拿得到的錢

*track: block · status: verified · source: lesson/claude/blocks/B04-liquidation-value.md*

# B04 · 可變現淨值

## 它解決什麼

`股數 × 收盤價` 是**毛值**。你賣掉拿不到那麼多，因為出場要付手續費和證交稅。

台股現股賣出成本：
- 手續費 0.1425%（券商可能打折，但保守用全額）
- 證交稅 0.3%
- 合計約 **0.4425%**

聽起來很小。但它是**單向、必然、每次都發生**的。任何一個「勝率 52%、平均賺 0.8%」的策略，扣掉這個之後就不存在了。

## 契約

```python
estimated_liquidation_value(shares: float, close: float) -> float
```

```python
def estimated_liquidation_value(shares, close):
    """Mirror the broker screen's estimated fee + 0.3% transaction tax."""
    gross = shares * close
    return gross - int(gross * 0.001425) - int(gross * 0.003)
```

**注意 `int()`。** 券商的費用是**無條件捨去到整數元**的，不是四捨五入。要跟券商畫面對得起來就必須複製這個行為 —— 這種細節是「數字對不起來」的常見來源。

## 為什麼要在每一天都用它，而不是只在最後一天

這是一個真實的 bug。原本的實作是：歷史日用毛值、最新日用淨值。結果**曲線在最後一天憑空掉了 0.44%**，看起來像當天虧損，其實是換了尺。

> **一條曲線只能有一個估值口徑。**
> 如果你改了口徑，整條線要一起改，不能只改末端。

修正後：所有日期都用可變現淨值，所以曲線的形狀是對的，起點也是對的。

## 陷阱

**陷阱 1：拿它跟券商的「未實現損益」比。**
券商庫存畫面的損益通常是**毛值**（不扣賣出費稅）。所以你的數字會系統性比券商小 0.44%。這不是錯，但必須標註口徑，否則 owner 會以為算錯了。

**陷阱 2：買進成本也要含手續費。**
成本端是 `cash_out`（價金＋手續費），賣出端是淨值。兩邊都含成本，這樣算出來的報酬才是**真的能落袋的報酬**。只扣一邊是最常見的半吊子做法。

**陷阱 3：零股和整股的費用結構不同。**
零股手續費有最低收費（通常 NT$1或20），小額交易的實際費率會遠高於 0.1425%。這個 block **不處理零股**，用在零股上會低估成本。

## 一個延伸的觀念：容量

同樣的邏輯往前推一步就是**容量**。你能買多少而不推動價格？

```python
SLOT_TWD = 50_000.0          # 50 萬 sleeve 分十檔
PARTICIPATION_CAP = 0.05     # 不超過均量 5%

slot_shares = SLOT_TWD / price
participation = slot_shares / avg_volume_20d
capacity_twd = avg_volume_20d * PARTICIPATION_CAP * price
```

真實產出裡，6570 維田的單量佔均量 **0.392%**，6213 聯茂只有 **0.001%** —— 差了 400 倍。同一個策略在這兩檔身上的可執行性完全不同，而傳統的回測報告不會告訴你這件事。

> **Sharpe 很高但容量只有 NT$10 萬的策略，不是好策略，是一個統計假象。**

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/build_dashboard.py::estimated_liquidation_value`

---

## [B05] 履約落差 · 策略卡報的價，帳戶付的價

*track: block · status: verified · source: lesson/claude/blocks/B05-signal-fill-slippage.md*

# B05 · 訊號 → 成交 履約落差

## 它解決什麼

策略卡說「進場 97.1」。帳戶實際成交 **97.80**。

差 0.72%。聽起來沒事。但如果這個落差是**系統性的**，那麼一個年化 20% 的策略，一年進出 20 次，就會被吃掉 14 個百分點。

**這個落差在理論曲線裡看不到，在帳戶淨值裡也看不到** —— 帳戶淨值只知道你付了 97.80，不知道原本應該是 97.1。它只存在於「兩份資料的交集」，所以必須刻意去記錄。

## 契約

```python
build_slippage_ledger(path, ohlc) -> list[SlippageRow]
```

輸入 `signal_fills.csv`：

```csv
signal_date,effective_date,strategy_id,stock_code,stock_name,action,signal_ref_price,signal_basis,fill_date,fill_time,fill_price,shares,source
2026-08-24,2026-08-25,MARGIN,2637,慧洋-KY,BUY,97.1,NEXT_OPEN,2026-08-25,10:14:13,97.80,1000,owner_pasted_fill
```

## 核心：方向要對

```python
# 買進成交在參考價「之上」是不利；賣出成交在「之下」是不利
direction = 1.0 if side == "BUY" else -1.0

def basis_points(reference):
    if not reference:
        return None
    return direction * (fill_price / reference - 1.0) * 10_000.0
```

**正的 bp 一律代表「對自己不利」**，不論買賣。這樣所有樣本可以直接平均，不需要分開處理。

這個小設計很重要：如果買賣用不同符號，你的統計會在買賣比例改變時漂移，而你不會發現。

## 三個參考價，全部都要記

同一筆成交要對照三個基準，因為它們回答不同的問題：

| 參考價 | 回答的問題 |
|---|---|
| `signal_ref_price` | 策略卡的報酬要打幾折 |
| 當日開盤 | 如果我無腦掛開盤會怎樣 |
| 當日收盤 | 我比「收盤價買」好還是差 |

只記一個的話，你之後想問另外兩個問題時，資料已經沒了。**紀錄的成本很低，事後補的成本是無限大。**

## 陷阱

**陷阱 1：`signal_basis` 一定要寫。**
「97.1」是收盤價？次日開盤預期？還是策略卡的進場欄？三者的落差意義完全不同。系統用 `NEXT_OPEN` 這種明確的 enum，不允許空白。

**陷阱 2：只記成交的，不記沒成交的。**
如果訊號發出但你沒買（掛單沒成交、或當天忘了），那也是履約落差的一部分 —— 而且是最貴的那一部分。**未執行的訊號要留紀錄**，否則你的落差統計只涵蓋「有成交的那些」，選擇性偏誤會讓數字好看。

（這一點目前的實作**還沒做到**，誠實記在這裡。）

**陷阱 3：樣本 1 筆就下結論。**
目前只有 2637 慧洋-KY 一筆。0.72% 這個數字現在**什麼都不代表**。

## 為什麼這是整個系統最重要的一張表

策略研究的終局問題只有一個：

> 這個策略能不能被執行？

回測告訴你「如果能買到訊號價會怎樣」。履約落差帳告訴你「你買不買得到」。**兩者相減才是真實可得報酬。**

大部分人的策略死在這裡，而且死了不知道 —— 因為他們從來沒有把訊號價和成交價放在同一張表上。

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/analytics.py::build_slippage_ledger`

---

## [B06] watchlist 驅動抓取 · 別讓賣掉的股票資料斷線

*track: block · status: verified · source: lesson/claude/blocks/B06-watchlist-driven-fetch.md*

# B06 · watchlist 驅動抓取

## 它解決什麼（一個真的踩到的洞）

抓行情要先決定「抓誰」。最自然的做法是：**抓我持有的**。

這個做法有一個安靜的失效模式：

```
你賣掉一檔 → 它離開持股 → 抓取宇宙不再包含它 → 資料從那天起斷線
```

而你**最需要它資料的時刻，正好是它剛賣掉的時候** —— 你要做出場分析、要算成交落點、要看賣掉之後它走去哪。

實際發生的事：3702 大聯大平倉後，它的買進和賣出兩筆成交在成交落點分析（[B03](B03-fill-landing.md)）裡完全對不到日線。整個系統只有 1 筆賣出樣本，而那 1 筆是空的。

## 契約

抓取宇宙 = `positions_ledger.csv` ∪ `watchlist.csv` ∪ `BENCHMARKS`

```python
def load_universe():
    seen = {}
    for row in read_csv(LEDGER_PATH):        # 持股
        seen.setdefault(row["stock_code"], {...})
    for row in read_csv(WATCHLIST_PATH):     # 追蹤清單：主線二 + 已平倉
        seen.setdefault(row["stock_code"], {...})
    return [seen[code] for code in sorted(seen)]
```

`watchlist.csv` 的 `track` 欄決定用途：

```csv
stock_code,stock_name,strategy_id,track,market,note
6213,聯茂,MARGIN,MAINLINE2,TWSE,融資卡成員；整戶零部位
3702,大聯大,YOY,CLOSED,TWSE,已平倉；保留行情供成交落點對照
```

- `MAINLINE2` → 進主線二頁面 + 抓行情
- `CLOSED` → **只抓行情**，不進任何頁面

`setdefault` 而非覆寫：持股清單優先，watchlist 只補沒有的。

## 為什麼分成兩個檔案而不是一個欄位

因為它們的**生命週期不同**。

`positions_ledger.csv` 是部位狀態，會被績效計算讀取。`watchlist.csv` 是觀察意圖，只被抓取程序讀取。把「我想看這檔」寫進部位檔，遲早會有人不小心把它算進淨值。

> **一個檔案一個責任。** 想在既有檔案加一個 `shares=0` 的列來偷渡追蹤清單，那是在給未來的自己埋雷。

## 陷阱

**陷阱 1：市場別（上市／上櫃）用猜的。**
`6570` 看起來像上櫃，但不一定。正確做法是**先試 TWSE，失敗再試 TPEx**，把 `market` 欄當成提示而不是事實：

```python
order = ["TPEX", "TWSE"] if market == "TPEX" else ["TWSE", "TPEX"]
for candidate in order:
    rows = fetch(code, candidate)
    if rows:
        return rows, candidate      # 回傳「實際解析出來的」市場別
```

**陷阱 2：抓取失敗要吵，不要安靜。**
`kept == 0` 要進 `failures` 清單並顯示。一個安靜失敗的抓取程序會讓你在三週後才發現某檔一直沒資料。

**陷阱 3：抓太多。**
7 檔 × 7 個月 × 1.8 秒延遲 ≈ 3 分鐘。宇宙每加一檔就是線性成本，而且會撞到交易所的 rate limit。**只抓你真的會看的**，這就是為什麼 watchlist 是明確清單而不是「全市場」。

## 一般化：這個模式叫什麼

這是**「意圖與狀態分離」**。

- 狀態（我持有什麼）：由事實推導，不可手動編輯
- 意圖（我想觀察什麼）：人工維護，不影響任何計算

很多資料管線的腐爛都來自把這兩者混在一起。分開之後，狀態可以隨時重算，意圖可以隨時修改，兩邊互不干擾。

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/fetch_prices.py::load_universe`

---

## [B07] Fail closed · 寧可炸掉，不要安靜地算錯

*track: block · status: verified · source: lesson/claude/blocks/B07-fail-closed-inputs.md*

# B07 · Fail closed 輸入契約

## 它解決什麼

金融資料管線最危險的不是崩潰，是**安靜地算出一個看起來合理的錯誤數字**。

崩潰你會馬上知道。錯誤數字你會拿去做決定。

## 反面教材

```python
price = float(row.get("close", 0))          # 缺資料 → 0 元
shares = int(row.get("shares") or 0)        # 缺資料 → 0 股
value = price * shares                       # 靜悄悄的 0
```

這段程式碼永遠不會拋例外，也永遠不會告訴你資料有問題。它會讓某一天的淨值變成 0，然後那天的日報酬變成 −100%，然後你的 MDD 變成 −100%，然後你以為策略爆掉了。

## 契約

```python
class InputError(ValueError):
    """Input contract violation that must fail closed."""

def required_float(value, field) -> float:
    if value is None or str(value).strip() == "":
        raise InputError(f"{field} is required")
    try:
        number = float(str(value).replace(",", ""))
    except ValueError as exc:
        raise InputError(f"{field} must be numeric: {value!r}") from exc
    if not math.isfinite(number):
        raise InputError(f"{field} must be finite")
    return number
```

四個檢查，每一個都擋一種真實會發生的事：

| 檢查 | 擋什麼 |
|---|---|
| 空值 | Excel 匯出的空格、券商漏欄 |
| 非數字 | `"—"`、`"N/A"`、`"停牌"` |
| 千分位 | `"1,234.5"` —— 這是台灣資料的常態 |
| `isfinite` | `inf`、`nan` —— 除以零的殘骸 |

**`field` 參數不是裝飾。** 錯誤訊息必須說出是哪一欄壞了，否則你要在 5,000 列裡面找。

## 三種缺資料，三種處理

不是所有缺資料都該炸。要分清楚：

**1. 契約違反 → 拋例外**
成交簿裡有一列沒有 `cash_out`。這是資料錯誤，繼續算下去只會產生垃圾。

**2. 已知的資料未到 → 明確狀態碼**
今天的收盤還沒發布。這是正常的，回傳 `NO_NEW_CLOSE` 或 `MARKET_DATE_MISMATCH`，**不要拿昨天的價格冒充今天**。

**3. 樣本不足 → 顯示 N/A**
只有 11 筆日報酬，算不出可信的 Sharpe。見 [`B08 樣本量門檻`](B08-sample-size-gate.md)。

```python
MIN_RISK_RETURN_OBS = 20

if len(returns) < MIN_RISK_RETURN_OBS:
    return None          # 不是 0，不是「暫時用 11 筆算」
```

## 陷阱

**陷阱 1：用 `or` 當預設值。**

```python
volume = to_float(row.get("volume")) or 0.0
```

這行有一個 bug：**真實的 0 成交量會被當成缺資料**。在停牌日這是對的行為，在其他情況下不是。要區分就要用 `is None`：

```python
volume = to_float(row.get("volume"))
volume = 0.0 if volume is None else volume
```

**陷阱 2：在迴圈裡 try/except 然後 continue。**

```python
for row in rows:
    try:
        process(row)
    except Exception:
        continue          # ← 這裡吞掉了多少列？沒有人知道
```

如果真的要容錯，**至少要數**：收集失敗的列、印出數量、超過閾值就整批失敗。

**陷阱 3：把驗證寫在畫面渲染裡。**
驗證要在**載入時**做，不是在畫圖時。否則同一份壞資料會在不同的圖表裡表現出不同的症狀，你會以為是畫圖的 bug。

## 一句話

> 一個會炸的管線，你會修它。
> 一個會安靜算錯的管線，你會信它。

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/build_dashboard.py::required_float`

---

## [B08] 樣本量門檻 · 敢顯示 N/A 才是專業

*track: block · status: verified · source: lesson/claude/blocks/B08-sample-size-gate.md*

# B08 · 樣本量門檻

## 它解決什麼

Sharpe = 平均日報酬 / 日報酬標準差 × √252

用 11 筆日報酬算，這個公式**會給你一個數字**。它可能是 3.2，看起來很棒。它毫無意義。

標準差在小樣本下極不穩定，年化又乘上 √252 ≈ 15.9 倍，把雜訊放大成一個看起來很專業的數字。**這是量化領域最常見的自我欺騙。**

## 契約

```python
MIN_RISK_RETURN_OBS = 20

def sharpe(returns):
    if len(returns) < MIN_RISK_RETURN_OBS:
        return None
    ...

def beta(portfolio, benchmark):
    common = align(portfolio, benchmark)
    if len(common) < MIN_RISK_RETURN_OBS + 1:   # 迴歸需要多一點
        return None
    ...
```

回傳 `None`，畫面顯示 `N/A`，**並且顯示為什麼**：

```
Sharpe   N/A    WAITING_MIN_20_RETURNS (目前 11 筆)
MDD      -0.76% OK
```

## 三個設計決定

**1. 門檻是常數，不是參數。**
如果它是參數，某天有人會為了讓畫面好看而調小它。常數放在模組頂端，改它需要改程式碼、過 code review、跑測試。

**2. 不同指標門檻可以不同。**
MDD 只需要一條曲線，2 筆就能算，而且意義明確 —— 所以 MDD **不設門檻**。Sharpe、Sortino、Alpha、Beta、IR、TE 需要分布的穩定性，全部設門檻。

分清楚「需要樣本量」和「不需要樣本量」的指標，比統一設一個門檻更誠實。

**3. 狀態碼要出現在畫面上，不是只在 log。**
`WAITING_MIN_20_RETURNS` 這個字串是給**人**看的。它告訴 owner：不是壞了，是還沒到。沒有這個字串，空白的 Sharpe 欄位會被當成 bug，然後有人會「修好它」。

## 陷阱

**陷阱 1：用月報酬或週報酬繞過門檻。**
「日報酬只有 11 筆，那我用週報酬吧」—— 週報酬只會更少。改變頻率不會創造資訊。

**陷阱 2：用回測填補實績。**
「實際只有 11 天，那我把回測的 500 天接上去」—— 這會產生一條在接點處性質完全改變的曲線，而且回測那段沒有滑價、沒有費用、沒有執行失敗。

系統的作法是**兩條線並排畫，只在共同截止日比較差異**，永遠不接在一起。

**陷阱 3：把「不夠」當成「不好」。**
N/A 不是負面評價。它是「還不知道」。這兩者的差別是專業和業餘的分界線。

## 更深的一層：Deflated Sharpe

即使樣本夠了，還有第二個問題：**你試了幾種策略才找到這一個？**

如果你測了 200 個參數組合，最好的那個的 Sharpe 有很大一部分是選擇偏誤。Deflated Sharpe Ratio 就是在扣這個。

兩個實務上踩過的坑：

- **DSR 顯示 1.0000 代表有 bug**，不是代表完美。通常是試驗次數沒有正確傳入
- **長期只做多的台股組合，成分間相關性 |ρ| ≤ 0.5 是不可能達到的**。任何用這個當門檻的篩選會回傳空集合

## 一句話

> 一個誠實的 N/A，比一個不誠實的 3.2 有價值一萬倍。
> 因為 N/A 讓你繼續蒐集資料，3.2 讓你下注。

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/analytics.py::MIN_RISK_RETURN_OBS`

---

## [B09] 推導式狀態 · 能算出來的絕不另存一份

*track: block · status: verified · source: lesson/claude/blocks/B09-derived-state.md*

# B09 · 推導式狀態

## 它解決什麼

「我想追蹤那些有訊號但我沒買的股票。」

**業餘做法**：開一個 `mainline2.csv`，手動維護名單。

**問題**：這份名單有三種方式會腐爛。
- 你買了一檔，忘了從名單刪掉 → 重複計算
- 你賣光一檔，忘了加回名單 → 追蹤斷線
- 策略卡換成分股，名單沒跟上 → 追蹤了一檔已經不在策略裡的股票

三個月後這份名單和現實完全脫節，而且**沒有任何機制會告訴你**。

## 契約

不要存名單。**每次重算。**

```
主線二 = { 今日策略卡的成員 } − { 成交簿推導出的整戶持股 }
```

```python
def held_positions(fills):
    held = defaultdict(float)
    for fill in fills:
        held[fill["stock_code"]] += fill["shares"] * (1 if fill["side"] == "BUY" else -1)
    return {code: shares for code, shares in held.items() if shares > 1e-9}


def build_roster(signals, bars, held):
    roster = []
    for (strategy_id, code), signal in sorted(signals.items()):
        if code in held:           # 有部位 → 不是主線二
            continue
        roster.append({...})
    return roster
```

持股本身也是推導的 —— 從成交簿加總，不是另外存一份庫存表。

**唯一的真相是成交簿。** 其他都是它的函數。

## 效果

名單自己浮現、自己消失：

- 8/25 買了 2637 慧洋-KY → 它隔天自動離開主線二
- 假設賣光 1709 和益 → 它自動回到主線二（如果還在卡上）
- 策略卡拿掉某檔 → 它自動消失，不會變成孤兒

**沒有第三個地方需要同步。** 這是這個系統最值得抄走的一個想法。

## 陷阱

**陷阱 1：`> 0` 要用 `> 1e-9`。**
浮點數加減後不會剛好等於 0。一檔完全賣光的股票可能留下 `-4.5e-16`，用 `> 0` 判斷會讓它憑空消失或憑空出現。

**陷阱 2：同一檔在不同策略。**
2395 研華同時出現在 YOY 卡和 BREAKOUT 卡上，但部位掛在 YOY。

問題：BREAKOUT 的 2395 算不算「沒買」？

系統的決定是**用整戶零部位當判準**（`code in held`，不看 strategy_id），因為主線二問的是「這個名字我有沒有曝險」，而曝險是整戶的。但這個決定必須寫下來，否則三個月後沒有人記得為什麼。

> **推導規則本身就是需要文件的東西。** 程式碼說明「怎麼算」，文件說明「為什麼這樣算」。

**陷阱 3：推導很慢的時候會有人想快取。**
現在 23 筆成交，重算是瞬間的事。等到 10,000 筆的時候會有人想存中間結果。

那時候的正確做法是**存快照 + 存推導版本號**，並且有一個測試比對快照和重算結果。不是放棄推導。

## 一般化

這個模式在資料庫世界叫 **derived state / materialized view**，在函數式程式設計叫 **single source of truth**。

判斷準則很簡單：

> **如果 A 可以從 B 算出來，那 A 不應該被儲存。**
> 如果非存不可（效能），那必須有一個測試證明存的和算的一樣。

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/build_mainline2.py::build_roster`

---

## [B10] shift(1) 前視測試 · 任何疊加層的有罪推定

*track: block · status: verified · verified_by: evidence/CLAUDE_VERIFICATION_GEMINI_CAGR50_2026-08-26.md · source: lesson/claude/blocks/B10-shift1-lookahead-test.md*

# B10 · shift(1) 前視測試

## 它解決什麼

回測引擎可以擋住「同棒成交」，但擋不住**在引擎外面對報酬序列做乘法**的疊加層：

```python
r_levered = base_returns * regime_multiplier      # 引擎完全看不到這一行
```

這一行如果 `regime_multiplier` 用了當日資訊，你會得到一條 Sharpe 4.9、MDD -5.5% 的曲線，而且回測引擎的每一項檢查都會通過。

**實測過的後果**：一份宣稱 CAGR 61–65% 的報告，全部超額報酬來自這一行少了 `.shift(1)`。

## 契約

```python
def shift1_test(base_returns, signal, overlay, floor=0.95):
    """比較同日訊號與落後一日訊號。回傳兩組指標與判定。

    base_returns : pd.Series  疊加之前的日報酬
    signal       : pd.Series  布林訊號（例如 close > MA）
    overlay      : callable   (returns, signal) -> returns
    floor        : float      lag1 至少要保住 lag0 的多少比例才算通過
    """
    out = {}
    for lag in (0, 1):
        s = signal.shift(lag).fillna(False).infer_objects(copy=False)
        idx = base_returns.index.intersection(s.index)
        out[lag] = metrics(overlay(base_returns.loc[idx], s.loc[idx]))

    base = metrics(base_returns)
    return {
        "base": base,
        "lag0": out[0],
        "lag1": out[1],
        # 關鍵：lag1 要跟「沒加疊加」比，不是跟 lag0 比
        "overlay_adds_value": out[1]["sharpe"] > base["sharpe"],
        "leakage_ratio": out[0]["sharpe"] / out[1]["sharpe"],
    }
```

## 怎麼讀結果

實測三個案例（台股 2013–2026）：

| | 基礎（無疊加） | lag0（同日） | lag1（可交易） | 洩漏比 |
|---|---|---|---|---|
| A | 2.559 | **4.963** | 2.598 | 1.91x |
| B | 2.401 | **4.894** | 2.513 | 1.95x |
| C | 2.104 | **4.269** | **1.992** | 2.14x |

**最關鍵的一欄是「基礎」，不是 lag0。**

看到 C 從 4.269 掉到 1.992，很多人會說「還有 1.992 嘛」。錯 —— 1.992 要跟**這個疊加根本沒加之前**的 2.104 比。加了之後**變差**。這個疊加的價值是負的。

判定規則：

| 條件 | 判定 |
|---|---|
| `lag1.sharpe <= base.sharpe` | **疊加無價值**，不管 lag0 多好看 |
| `leakage_ratio > 1.3` | **強烈懷疑前視**，要逐行檢查訊號的時間索引 |
| `lag1.sharpe > base.sharpe` 且 `leakage_ratio < 1.15` | 可以繼續評估 |

## 陷阱

**陷阱 1：以為 `trade_at_price='open'` 就安全了。**
那個設定守的是引擎內的成交價。疊加層在引擎外，完全不受它管。

**陷阱 2：只 shift 訊號，忘了 shift 用來算訊號的中間變數。**

```python
r20 = curve.pct_change(20)                              # 第 t 日的值含第 t 日報酬
tp_scale = np.where(r20 > tp, 0.70, 1.0)
r_daily = r_daily * tp_scale                            # ← 同樣的病
```

停利、波動度目標、任何「用曲線自身的近期表現決定曝險」的東西都有這個問題。

**陷阱 3：用一天的 lag 就以為夠了。**
shift(1) 是**最低**要求，不是充分條件。真實交易還有：訊號要在收盤後算完、要在次日開盤前送出、可能部分成交。保守一點用 shift(2) 再測一次，看衰減幅度。

## 一眼可疑的指紋

不用讀程式碼就該懷疑的：

- 台股純多頭、月頻換股，13 年 MDD **小於 -10%**
- Sharpe **大於 3**（長期台股多頭的實測上限約 2.2）
- Calmar **大於 4**
- 回撤在 2015 / 2018 / 2022 反而縮小

## 相關

- 完整案例與程式碼片段：[C50 前視偏誤](../50-lookahead-bias.md)
- 契約層怎麼擋成交價前視：[B14 策略契約](B14-strategy-spec-contract.md)
- Gemini 從資料端防洩漏的作法：[GB02 PIT 對齊器](../../gemini/blocks/GB02-pit-lag-aligner.md) —— 那一塊守的是「因子讀到未來的財報」，這一塊守的是「疊加層讀到今天的收盤」。兩個缺口不同，都要堵。

---

## [B11] 機械試驗計數器 · 不讓呼叫端自己填 N

*track: block · status: verified · verified_by: evidence/honest_top5/robustness.json · source: lesson/claude/blocks/B11-mechanical-trial-counter.md*

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

---

## [B12] 本地胃納模型 · 最緊的那一檔決定整本帳

*track: block · status: verified · verified_by: evidence/honest_top5/all_metrics.json · source: lesson/claude/blocks/B12-local-capacity-model.md*

# B12 · 本地胃納模型

## 它解決什麼

FinLab 的 `liquidity.capacity` 是伺服器端計算，離線取不到。但**胃納量是台股量化最重要的單一數字** —— 實測全庫 CAGR 最高（53.69%）、Calmar 最高（2.16）的那檔策略，胃納量是 **NT$70,802**。

沒有本地模型，你會在報告裡看到一堆漂亮的 CAGR，卻不知道哪些放得進錢。

## 契約

```python
def capacity_ntd(position, close, volume, participation=0.05, adv_window=20, q=0.5):
    """帳本 NAV 上限：持股中最緊的一檔碰到 ADV20 的 participation 時的規模。

    對應執行層規則「單一標的下單量 > ADV20 的 5% 即 BLOCK」。
    回傳全期中位數。等權假設。
    """
    adv = (close * volume).average(adv_window)

    held = position.astype(bool)
    n = held.sum(axis=1)
    held, n = held[n > 0], n[n > 0]
    if held.empty:
        return 0.0

    adv_al = adv.reindex(index=held.index, columns=held.columns, method="ffill")
    # 等權下每檔權重 = 1/n，該檔容得下的 NAV = participation * ADV / (1/n)
    per_name = adv_al.where(held) * participation
    tightest = per_name.min(axis=1) * n

    s = tightest.dropna()
    return float(s.quantile(q)) if len(s) else 0.0
```

非等權時把最後兩行換成：

```python
weights = position.div(position.sum(axis=1), axis=0)
per_name = (adv_al * participation) / weights.where(weights > 0)
tightest = per_name.min(axis=1)
```

## 三個設計決定（都要在報告裡講明）

**1. 取最緊的那一檔（`min`），不是平均。**
帳本的胃納由最難買的那檔綁死。取平均會讓一檔流動性極差的股票被 39 檔好股票稀釋掉，得到一個你實際上做不到的數字。

**2. 取中位數（`quantile(0.5)`），不是最小值也不是平均。**
最小值會被單一異常日綁架（某天某檔停牌、某天成交量枯竭）。平均會被高流動性期間拉高。中位數回答「一般日子你能放多少」。

**3. participation 是常數，不是參數。**
它必須等於執行層真正會 BLOCK 的那個閾值。如果執行層是 5%，這裡就是 5%。兩邊不一致，你的研究會核准執行層拒絕的東西。

## 這個模型不能宣稱的事

要在報告裡寫清楚，否則會被過度信任：

- **沒有模擬市場衝擊。** 它只回答「不超過 ADV 的 5%」，不回答「買下去會推價多少」。
- **沒有考慮進出不對稱。** 賣出的流動性通常比買入差，尤其在你想賣的時候。
- **和 FinLab 伺服器端的數字不會一樣。** 要標明是哪一個口徑。
- **月頻換股的假設。** 如果你的策略會在幾天內大幅換手，單日參與率會遠高於這個模型的隱含值。

## 混合帳本：胃納由最緊的那一腳綁死

想用「70% 大容量 + 30% 小型股爆發」兩全其美？這是恆等式，不是可以設計繞過的東西：

```
小型股腳的原生胃納 = C_small
配置權重           = w
總帳本 NAV 上限    = C_small / w
```

`C_small = 70,000`、`w = 0.30` → 總帳本上限 **NT$233,333**。

配得越少總胃納越大，但你稀釋掉的正是你想要的爆發力。

**反面教材**：我驗過一份報告用 `cap = 常數 / w_smallcap` 宣稱混合後胃納「提升 11 倍」。那個公式確實會隨權重下降而變大，但它不是胃納模型，只是一個倒數 —— 而且代入該報告自己的權重後得到 NT$883,062，它卻寫 NT$630,759。

## 實測：胃納量如何改變排名

| S### | Sharpe | CAGR | Calmar | 胃納量 | 可部署 |
|---|---|---|---|---|---|
| S122 | 2.211 | 21.78% | 1.84 | NT$1,077,368 | 是 |
| S144 | 2.110 | 32.26% | 1.39 | NT$192,132 | **否** |
| S127 | 2.107 | **53.69%** | **2.16** | **NT$70,802** | **否** |
| S123 | 2.097 | 26.62% | 1.58 | NT$2,278,084 | 是 |
| S004 | 1.993 | 35.17% | 1.17 | **NT$79,251** | **否** |

按 Sharpe 排的前五名，三名放不進錢。

**所以排序邏輯是：先過胃納門檻 → 在通過的裡面排 Sharpe → 沒通過的另立一張表但仍然列出。** 第三步不能省 —— 那些策略告訴你 alpha 在哪裡，只是你拿不到。

## 相關

- 為什麼這是真正的約束：[C41 胃納量](../41-capacity-is-the-constraint.md)
- 造假的三種寫法：[C53 胃納量造假](../53-capacity-fiction.md)
- Gemini 的執行端版本：[GB04 ADV20 容量守門員](../../gemini/blocks/GB04-adv-capacity-guard.md)。那一塊守的是**下單當下**（這張單會不會超過 ADV），本塊算的是**研究階段**（這個策略整體能放多少錢）。兩者的 participation 常數必須一致，否則研究會核准執行端拒絕的東西。

---

## [B13] 相關係數去重 · 你的前五名可能是同一支策略

*track: block · status: verified · verified_by: evidence/honest_top5/robustness.json · source: lesson/claude/blocks/B13-correlation-dedup.md*

# B13 · 相關係數去重

## 它解決什麼

兩個問題，同一個工具：

**問題一：同一支策略註冊了很多次。**
實測發現三個永久編號指向同一支策略，日報酬相關係數 **1.000**，績效數字完全相同。另一組三檔 ρ 0.95–0.99。靠檔名或家族欄位抓不出來 —— 它們的名字和家族都不一樣。

**問題二：你的「前五名」是同一個賭注的五種寫法。**
按 Sharpe 排出來的前五名，彼此相關係數 0.78–0.90。各配 20% 資金，你買到的是同一個因子，不是分散。

## 契約

```python
def dedup(rows, limit, rho=0.95, min_overlap=252):
    """按 Sharpe 由高到低取，相關係數 >= rho 的視為同一支，只留最好的那個。"""
    ranked = sorted(rows, key=lambda r: -(r["sharpe"] or 0))
    kept, kept_ret, dropped = [], {}, {}

    for r in ranked:
        n = r["strategy_number"]
        ret = load_returns(n)
        dup_of = None
        for k, kr in kept_ret.items():
            i = ret.index.intersection(kr.index)
            if len(i) > min_overlap and ret.loc[i].corr(kr.loc[i]) >= rho:
                dup_of = k
                break
        if dup_of is not None:
            dropped.setdefault(dup_of, []).append(n)
            continue
        kept.append(r)
        kept_ret[n] = ret
        if len(kept) >= limit:
            break

    return kept, dropped
```

**`min_overlap` 不能省。** 兩條只重疊 30 天的曲線可以輕易得到 0.97 的相關係數，那毫無意義。

## 去重之後一定要出相關係數矩陣

去重門檻 0.95 只擋掉「幾乎完全一樣」的。**0.90 不會被擋掉，但 0.90 也不是分散。**

實測矩陣（前七名）：

| | S122 | S138 | S123 | S124 | S125 | S022 | S148 |
|---|---|---|---|---|---|---|---|
| S122 | 1.00 | 0.89 | 0.87 | 0.83 | 0.78 | 0.62 | 0.52 |
| S138 | | 1.00 | 0.90 | 0.82 | 0.79 | 0.61 | 0.52 |
| S123 | | | 1.00 | **0.90** | 0.85 | 0.71 | 0.59 |
| S124 | | | | 1.00 | 0.82 | 0.72 | 0.59 |
| S125 | | | | | 1.00 | 0.70 | 0.57 |
| S022 | | | | | | 1.00 | 0.50 |

讀法：前五名（S122/S138/S123/S124/S125）是**一群**。真正不同的是第 1、第 6、第 7 名 —— S122 + S022 + S148，兩兩 0.50–0.62。

## 分群比排名有用

```python
def cluster(corr, threshold=0.75):
    """單連結分群：把相關係數高於 threshold 的視為同一個賭注。"""
    groups, seen = [], set()
    for a in corr.index:
        if a in seen:
            continue
        g = [b for b in corr.index if corr.loc[a, b] >= threshold]
        seen |= set(g)
        groups.append(g)
    return groups
```

實測 12 檔可部署候選，分成三群：

| 群 | 成員 | 群內最佳 Sharpe | 對其他群的相關 |
|---|---|---|---|
| 品質低波 | S122 / S138 / S123 / S124 / S125 | 2.211 | — |
| 多因子價值 | S022 / S048 / S126 | 1.756 | 0.61–0.72 |
| 凸性動能 | S148 | 1.545 | 0.50–0.59 |

**127 檔已註冊策略，真正不同的賭注只有三個。** 這是分群才看得出來的事。

## 陷阱

**陷阱 1：以為家族欄位可以代替相關係數。**
被判為完全重複的那三檔，家族欄位不完全一樣。名字騙人，報酬序列不騙人。

**陷阱 2：只在最後選投組時才去重。**
去重要在**計算 DSR 之前**做。重複註冊會讓試驗數虛胖、離散度失真。見 [B11 機械試驗計數器](B11-mechanical-trial-counter.md)。

**陷阱 3：把低相關當成「可以各配 20%」。**
相關係數低只代表它們不是同一個東西，不代表它們各自都經得起考驗。實測那三群裡，只有第一群的代表通過去膨脹檢定；另外兩群的代表沒過。**分散是為了降低單一因子依賴，不是為了讓沒通過的東西混進來。**

## 相關

- 完整清單與矩陣：[C70 已驗證積木清單](../70-verified-strategy-inventory.md)
- 為什麼要在 DSR 之前做：[C52 試驗計數](../52-trial-counting.md)
- 整條驗證流水線：[C60 驗證流水線](../60-verification-harness.md)

---

## [B14] 策略契約：讓作弊在建構物件時就爆掉

*track: block · status: verified · verified_by: src/quant_grill_lab/strategies/base.py · source: lesson/claude/blocks/B14-strategy-spec-contract.md*

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

---
