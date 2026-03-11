# US Stock Candle Gainers - API リファレンス

## 1. 概要

US Stock Candle Gainers は FastAPI ベースの REST API を提供します。ローソク足パターン分析、財務リスク分析、複数銘柄スキャン、パターン逆引き検索、AIトレードプロンプト生成の各機能をエンドポイントとして公開しています。

- **フレームワーク**: FastAPI
- **データソース**: yfinance
- **レスポンス形式**: JSON
- **エラーメッセージ**: 日本語

---

## 2. Base URL

```
http://localhost:8000
```

---

## 3. エンドポイント一覧

| メソッド | パス | 説明 |
|---------|------|------|
| `GET` | `/` | メインHTMLページ |
| `GET` | `/screener` | スクリーナーHTMLページ |
| `GET` | `/pattern-search` | パターン検索HTMLページ |
| `POST` | `/analyze` | ローソク足パターン分析 |
| `POST` | `/risk` | 財務リスク分析 |
| `POST` | `/screener` | 複数銘柄一括スキャン |
| `GET` | `/api/patterns` | パターン一覧取得 |
| `POST` | `/api/pattern-search` | パターン逆引き検索 |
| `POST` | `/trade-prompt` | AIトレードプロンプト生成 |

---

## 4. 各エンドポイント詳細

### 4.1 GET / - メインHTMLページ

メインの分析画面を提供する静的HTMLページを返却します。

- **レスポンス**: `text/html`（`static/index.html`）

---

### 4.2 GET /screener - スクリーナーHTMLページ

スクリーナー画面を提供する静的HTMLページを返却します。

- **レスポンス**: `text/html`（`static/screener.html`）

---

### 4.3 GET /pattern-search - パターン検索HTMLページ

パターン検索画面を提供する静的HTMLページを返却します。

- **レスポンス**: `text/html`（`static/pattern-search.html`）

---

### 4.4 POST /analyze - ローソク足パターン分析

指定した銘柄のローソク足パターンを検出します。

#### リクエスト

```json
{
  "ticker": "AAPL",
  "change1": null,
  "change2": null,
  "change3": null,
  "candle_count": 3
}
```

| フィールド | 型 | 必須 | デフォルト | 説明 |
|-----------|-----|------|-----------|------|
| `ticker` | `string` | はい | - | ティッカーシンボル（1文字以上、自動大文字変換） |
| `change1` | `float \| null` | いいえ | `null` | 1本目の変動率（シミュレーション用） |
| `change2` | `float \| null` | いいえ | `null` | 2本目の変動率（シミュレーション用） |
| `change3` | `float \| null` | いいえ | `null` | 3本目の変動率（シミュレーション用） |
| `candle_count` | `int \| null` | いいえ | `null` | ローソク足本数（2 または 3。nullの場合は3） |

#### モード判定ロジック

| 条件 | モード |
|------|--------|
| change1 + change2 + change3 を全て指定 | `simulation_confirmed` |
| change1 + change2 のみ指定 | `simulation_predicted` |
| 上記以外（change未指定 or change1のみ） | `realdata` / `realdata_2candle` |

#### レスポンス

```json
{
  "ticker": "AAPL",
  "mode": "realdata",
  "atr": 3.45,
  "base_price": null,
  "candles": [
    {
      "date": "2026-03-07",
      "open": 175.50,
      "high": 178.20,
      "low": 174.80,
      "close": 177.30,
      "volume": 52345678
    }
  ],
  "patterns": [
    {
      "type": "confirmed",
      "name": "明けの明星",
      "signal": "買いシグナル",
      "description": "下降トレンドの底で出現する強気反転パターン",
      "required_third": null,
      "direction": "bullish",
      "pattern_id": "morning_star",
      "pattern_candle_count": 3
    }
  ],
  "short_interest": {
    "short_percent_of_float": 1.23,
    "short_ratio": 2.5,
    "shares_short": 12345678,
    "shares_short_prior_month": 11234567,
    "date_short_interest": "2026-02-15",
    "date_short_prior_month": "2026-01-15"
  }
}
```

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `ticker` | `string` | ティッカーシンボル |
| `mode` | `string` | 分析モード（`realdata`, `realdata_2candle`, `simulation_predicted`, `simulation_confirmed`） |
| `atr` | `float \| null` | ATR(14)値（realdataモードのみ） |
| `base_price` | `float \| null` | 基準価格（simulationモードのみ） |
| `candles` | `CandleData[]` | OHLCVデータの配列 |
| `patterns` | `PatternResult[]` | 検出されたパターンの配列 |
| `short_interest` | `ShortInterest \| null` | ショートインタレスト情報（realdataモードのみ） |

#### 使用例

**実データ分析（3本足）:**

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'
```

**実データ分析（2本足）:**

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "candle_count": 2}'
```

**予測シミュレーション:**

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "change1": -3.5, "change2": -1.2}'
```

**確定シミュレーション:**

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "change1": -3.5, "change2": -1.2, "change3": 4.0}'
```

---

### 4.5 POST /risk - 財務リスク分析

指定した銘柄の財務健全性とオファリングリスクを分析します。

#### リクエスト

```json
{
  "ticker": "AAPL"
}
```

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `ticker` | `string` | はい | ティッカーシンボル（1文字以上、自動大文字変換） |

#### レスポンス

```json
{
  "ticker": "AAPL",
  "financial_health": {
    "de_ratio": {
      "name": "D/Eレシオ",
      "value": 1.52,
      "level": "中",
      "description": "負債資本比率は1.52で、中程度の水準です。"
    },
    "current_ratio": { "name": "...", "value": 1.07, "level": "...", "description": "..." },
    "profit_margin": { "name": "...", "value": 0.25, "level": "...", "description": "..." },
    "fcf": { "name": "...", "value": 95000000000, "level": "...", "description": "..." },
    "overall_level": "低",
    "summary": "財務健全性は良好です。"
  },
  "offering_risk": {
    "cash_runway": { "name": "...", "value": null, "level": "...", "description": "..." },
    "dilution": { "name": "...", "value": null, "level": "...", "description": "..." },
    "net_income": { "name": "...", "value": null, "level": "...", "description": "..." },
    "debt_cash_ratio": { "name": "...", "value": null, "level": "...", "description": "..." },
    "overall_level": "低",
    "summary": "オファリングリスクは低いと判断されます。"
  }
}
```

#### 使用例

```bash
curl -X POST http://localhost:8000/risk \
  -H "Content-Type: application/json" \
  -d '{"ticker": "TSLA"}'
```

---

### 4.6 POST /screener - 複数銘柄一括スキャン

最大50銘柄に対してローソク足パターンの一括検出を行います。

#### リクエスト

```json
{
  "tickers": ["AAPL", "TSLA", "NVDA", "MSFT"],
  "candle_count": 3
}
```

| フィールド | 型 | 必須 | デフォルト | 説明 |
|-----------|-----|------|-----------|------|
| `tickers` | `string[]` | はい | - | ティッカーシンボルの配列（1〜50件） |
| `candle_count` | `2 \| 3` | いいえ | `3` | ローソク足本数 |

#### バリデーション

- `tickers` が空の場合: `422 Unprocessable Entity`
- `tickers` が50件を超える場合: `422 Unprocessable Entity`

#### レスポンス

```json
{
  "results": [
    {
      "ticker": "AAPL",
      "candles": [...],
      "patterns": [...],
      "change_pct": 2.35,
      "error": null
    },
    {
      "ticker": "INVALID",
      "candles": [],
      "patterns": [],
      "change_pct": null,
      "error": "'INVALID' は有効な株式銘柄ではありません。"
    }
  ],
  "total": 4,
  "scanned": 3,
  "errors": 1
}
```

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `results` | `TickerScanResult[]` | 各銘柄のスキャン結果 |
| `total` | `int` | リクエストされた銘柄の総数 |
| `scanned` | `int` | 正常にスキャンされた銘柄数 |
| `errors` | `int` | エラーが発生した銘柄数 |

#### 使用例

```bash
curl -X POST http://localhost:8000/screener \
  -H "Content-Type: application/json" \
  -d '{"tickers": ["AAPL", "TSLA", "NVDA"], "candle_count": 2}'
```

---

### 4.7 GET /api/patterns - パターン一覧取得

登録されている全60パターンの一覧を返却します。

#### リクエスト

パラメータなし。

#### レスポンス

```json
{
  "patterns": [
    {
      "id": "bearish_pin_bar",
      "name": "ベアリッシュ・ピンバー",
      "direction": "bearish",
      "available_types": ["confirmed"],
      "pattern_candle_count": 1
    },
    {
      "id": "morning_star",
      "name": "明けの明星",
      "direction": "bullish",
      "available_types": ["confirmed", "predicted"],
      "pattern_candle_count": 3
    }
  ],
  "total": 60
}
```

#### 使用例

```bash
curl http://localhost:8000/api/patterns
```

---

### 4.8 POST /api/pattern-search - パターン逆引き検索

指定したパターンIDを持つ銘柄を、ティッカーリストから検索します。

#### リクエスト

```json
{
  "tickers": ["AAPL", "TSLA", "NVDA", "MSFT"],
  "pattern_ids": ["morning_star", "bullish_engulfing"],
  "candle_count": 3
}
```

| フィールド | 型 | 必須 | デフォルト | 説明 |
|-----------|-----|------|-----------|------|
| `tickers` | `string[]` | はい | - | ティッカーシンボルの配列（1〜50件、自動大文字変換） |
| `pattern_ids` | `string[]` | はい | - | 検索するパターンIDの配列（1件以上） |
| `candle_count` | `2 \| 3` | いいえ | `3` | ローソク足本数 |

#### バリデーション

- `tickers` が空の場合: `422 Unprocessable Entity`
- `tickers` が50件を超える場合: `422 Unprocessable Entity`
- `pattern_ids` が空の場合: `422 Unprocessable Entity`
- `pattern_ids` に無効なIDが含まれる場合: `400 Bad Request`

#### レスポンス

```json
{
  "results": [
    {
      "ticker": "AAPL",
      "change_pct": 1.85,
      "patterns": [
        {
          "type": "confirmed",
          "name": "明けの明星",
          "signal": "買いシグナル",
          "description": "...",
          "required_third": null,
          "direction": "bullish",
          "pattern_id": "morning_star",
          "pattern_candle_count": 3
        }
      ],
      "error": null
    }
  ],
  "total": 4,
  "matched": 1,
  "errors": 0
}
```

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `results` | `PatternSearchResult[]` | 各銘柄の検索結果 |
| `total` | `int` | リクエストされた銘柄の総数 |
| `matched` | `int` | 正常にスキャンされた銘柄数 |
| `errors` | `int` | エラーが発生した銘柄数 |

#### 使用例

```bash
curl -X POST http://localhost:8000/api/pattern-search \
  -H "Content-Type: application/json" \
  -d '{"tickers": ["AAPL", "TSLA"], "pattern_ids": ["morning_star"]}'
```

---

### 4.9 POST /trade-prompt - AIトレードプロンプト生成

指定した銘柄のトレード分析用Markdownプロンプトを生成します。

#### リクエスト

```json
{
  "ticker": "AAPL"
}
```

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `ticker` | `string` | はい | ティッカーシンボル（1文字以上、自動大文字変換） |

#### レスポンス

```json
{
  "ticker": "AAPL",
  "prompt": "# AAPL トレード分析\n\n## 企業概要\n..."
}
```

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `ticker` | `string` | ティッカーシンボル |
| `prompt` | `string` | Markdown形式のトレード分析プロンプト |

#### 備考

- 本エンドポイントは非同期処理（`async`）で実装されています
- 外部AI APIの呼び出しは行いません。プロンプトテキストの生成のみです

#### 使用例

```bash
curl -X POST http://localhost:8000/trade-prompt \
  -H "Content-Type: application/json" \
  -d '{"ticker": "NVDA"}'
```

---

## 5. データモデル定義

### 5.1 CandleData

1本のローソク足のOHLCVデータ。

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `date` | `string` | 日付（YYYY-MM-DD形式） |
| `open` | `float` | 始値 |
| `high` | `float` | 高値 |
| `low` | `float` | 安値 |
| `close` | `float` | 終値 |
| `volume` | `int` | 出来高 |

### 5.2 PatternResult

検出されたローソク足パターンの結果。

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `type` | `string` | パターンの種別（`"confirmed"` または `"predicted"`） |
| `name` | `string` | パターン名（日本語） |
| `signal` | `string` | シグナル表示 |
| `description` | `string` | パターンの説明（日本語） |
| `required_third` | `string \| null` | 3本目のローソク足条件（predictedモードのみ） |
| `direction` | `"bullish" \| "bearish"` | パターンの方向性 |
| `pattern_id` | `string \| null` | 機械可読なパターン識別子 |
| `pattern_candle_count` | `1 \| 2 \| 3` | パターンに必要なローソク足本数 |

### 5.3 ShortInterest

ショートインタレスト（空売り）データ。月次更新。

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `short_percent_of_float` | `float \| null` | 浮動株に対する空売り比率（%） |
| `short_ratio` | `float \| null` | ショートレシオ（Days to Cover） |
| `shares_short` | `int \| null` | 空売り株数 |
| `shares_short_prior_month` | `int \| null` | 前月の空売り株数 |
| `date_short_interest` | `string \| null` | 空売りデータ日付（YYYY-MM-DD） |
| `date_short_prior_month` | `string \| null` | 前月の空売りデータ日付（YYYY-MM-DD） |

### 5.4 RiskMetric

個別のリスク指標。

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `name` | `string` | 指標名（日本語） |
| `value` | `float \| null` | 指標の値 |
| `level` | `string` | リスクレベル（`"低"`, `"中"`, `"高"`） |
| `description` | `string` | 指標の説明（日本語） |

### 5.5 FinancialHealth

財務健全性の評価結果。

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `de_ratio` | `RiskMetric` | D/Eレシオ |
| `current_ratio` | `RiskMetric` | 流動比率 |
| `profit_margin` | `RiskMetric` | 利益率 |
| `fcf` | `RiskMetric` | フリーキャッシュフロー |
| `overall_level` | `string` | 総合リスクレベル（`"低"`, `"中"`, `"高"`） |
| `summary` | `string` | 総合サマリー（日本語） |

### 5.6 OfferingRisk

オファリングリスクの評価結果。

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `cash_runway` | `RiskMetric` | キャッシュランウェイ |
| `dilution` | `RiskMetric` | 希薄化リスク |
| `net_income` | `RiskMetric` | 純利益 |
| `debt_cash_ratio` | `RiskMetric` | 負債現金比率 |
| `overall_level` | `string` | 総合リスクレベル（`"低"`, `"中"`, `"高"`） |
| `summary` | `string` | 総合サマリー（日本語） |

### 5.7 PatternEntry

パターンレジストリの1エントリ。

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `id` | `string` | パターンID（機械可読な識別子） |
| `name` | `string` | パターン名（日本語） |
| `direction` | `"bullish" \| "bearish"` | パターンの方向性 |
| `available_types` | `string[]` | 利用可能な検出タイプ（`"confirmed"`, `"predicted"`） |
| `pattern_candle_count` | `1 \| 2 \| 3` | パターンに必要なローソク足本数 |

### 5.8 TickerScanResult

スクリーナーでの個別銘柄スキャン結果。

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `ticker` | `string` | ティッカーシンボル |
| `candles` | `CandleData[]` | OHLCVデータの配列 |
| `patterns` | `PatternResult[]` | 検出されたパターンの配列 |
| `change_pct` | `float \| null` | 変動率（%） |
| `error` | `string \| null` | エラーメッセージ（エラー時のみ） |

### 5.9 PatternSearchResult

パターン逆引き検索での個別銘柄結果。

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `ticker` | `string` | ティッカーシンボル |
| `change_pct` | `float \| null` | 変動率（%） |
| `patterns` | `PatternResult[]` | 検出されたパターンの配列 |
| `error` | `string \| null` | エラーメッセージ（エラー時のみ） |

### 5.10 ErrorResponse

APIエラーレスポンス。

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `detail` | `string` | エラーメッセージ（日本語） |

---

## 6. エラーハンドリング

### HTTPステータスコード

| コード | 例外クラス | 説明 |
|--------|-----------|------|
| `400` | `TickerNotFoundError` | 指定されたティッカーが見つからない |
| `400` | `TickerNotEquityError` | 指定されたティッカーが株式ではない |
| `400` | `ValueError`（pattern-search） | 無効なパターンIDが指定された |
| `422` | Pydantic `ValidationError` | リクエストバリデーションエラー（FastAPI自動処理） |
| `500` | `DataFetchError` | yfinance APIからのデータ取得エラー |

### エラーレスポンス形式

全てのエラーレスポンスは `detail` フィールドに日本語のエラーメッセージを含みます。

#### TickerNotFoundError（400）

```json
{
  "detail": "'XXXXX' は有効な株式銘柄ではありません。"
}
```

#### TickerNotEquityError（400）

```json
{
  "detail": "'SPY' は株式ではありません（種別: ETF）。"
}
```

#### DataFetchError（500）

```json
{
  "detail": "データの取得中にエラーが発生しました。しばらく経ってから再試行してください。"
}
```

#### ValidationError（422）

```json
{
  "detail": [
    {
      "loc": ["body", "ticker"],
      "msg": "String should have at least 1 character",
      "type": "string_too_short"
    }
  ]
}
```

#### 無効なパターンID（400）

```json
{
  "detail": "Invalid pattern IDs: invalid_pattern_1, invalid_pattern_2"
}
```
