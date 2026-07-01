# CrowdWorks Analyzer

AIがクラウドソーシング案件を分析し、応募優先順位を提案するツールです。

---


## 開発環境設定

### Pythonコンポーネントインストール

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

### API Key Setup

OpenAI API キーは環境変数として設定してください。

#### 永続的な設定

zsh を使用している場合、次のコマンドで今後のセッションでも有効になります。

```bash
echo 'export CW_AI_ANALYZER_OPENAI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

#### 一時的な設定方法

現在のターミナルセッションでのみ有効です。

```bash
export CW_AI_ANALYZER_OPENAI_API_KEY="your-api-key-here"
```

設定が反映されているか確認するには、次のコマンドを実行してAPI Keyが正しく表示されるか確認してください。

```bash
echo $CW_AI_ANALYZER_OPENAI_API_KEY
```


## AI分析と結果の確認方法

OpenAI APIによる案件分析結果は、JSONファイルとして出力できます。

この機能では、CrowdWorksから取得した `Job` 情報をOpenAI APIで分析し、分析結果である `AnalysisResult` と紐づけた形式で保存します。

---

### 分析実行方法

```bash
python3 src/main.py
```

---

### 出力先

分析結果は以下のファイルに保存されます。

```text
output/analysis_results.json
```

出力先ディレクトリが存在しない場合は、自動で作成されます。

---

### 出力形式

出力されるJSONには、案件情報とAI分析結果がセットで保存されます。

```json
[
  {
    "job": {
      "id": 12345678,
      "title": "案件タイトル",
      "url": "https://crowdworks.jp/public/jobs/12345678"
    },
    "analysis": {
      "reward_score": 4,
      "competition_score": 3,
      "ai_score": 5,
      "continuity_score": 4,
      "quality_score": 5,
      "total_score": 91,
      "recommendation_reasons": [
        "生成AIを活用できる案件である",
        "継続案件の可能性が高い"
      ],
      "concerns": [
        "応募人数が多く競争率が高い"
      ],
      "application_strategy": [
        "AI活用経験を具体例付きでアピールする"
      ],
      "overall_comment": "AIスキルとの親和性が高く、応募価値の高い案件です。"
    }
  }
]
```

---

### 主な出力項目

#### job

案件情報を表します。

| フィールド | 内容 |
|---|---|
| `id` | CrowdWorks案件ID |
| `title` | 案件タイトル |
| `url` | 案件詳細ページURL |

#### analysis

AIによる案件分析結果を表します。

| フィールド | 内容 |
|---|---|
| `reward_score` | 報酬の魅力度 |
| `competition_score` | 応募しやすさ |
| `ai_score` | AIとの親和性 |
| `continuity_score` | 継続案件となる可能性 |
| `quality_score` | 案件品質 |
| `total_score` | 案件全体の応募価値 |
| `recommendation_reasons` | 応募をおすすめする理由 |
| `concerns` | 応募前に注意すべき点 |
| `application_strategy` | 採用率を高めるための応募戦略 |
| `overall_comment` | 案件全体の総評 |

---

### 備考

- JSONはUTF-8で出力されます。
- 日本語はエスケープされず、そのまま読める形式で保存されます。
- インデント付きJSONとして保存されるため、人間が確認しやすい形式になっています。
- `analysis_results.json` は、今後のランキング機能や応募優先度判定の入力データとして利用できます。


## 案件ランキング機能

AI分析結果をもとに、案件を応募優先度の高い順に並び替えることができます。

この機能では、`output/analysis_results.json` に保存された `Job` と `AnalysisResult` のセットを読み込み、`analysis.total_score` の高い順にランキングします。

---

### 実行方法

```bash
python3 src/main.py
```

---

### 入力ファイル

ランキング処理では、以下のAI分析結果ファイルを読み込みます。

```text
output/analysis_results.json
```

このファイルには、案件情報とAI分析結果が紐づいたデータが保存されています。

---

### 出力先

ランキング結果は以下のファイルに保存されます。

```text
output/ranked_jobs.json
```

出力先ディレクトリが存在しない場合は、自動で作成されます。

---

### ランキング基準

初期実装では、以下のルールでランキングします。

- `analysis.total_score` の高い順に並び替える
- 各案件に `rank` を付与する
- `rank` は1から順番に付与する

---

### 出力形式

```json
[
  {
    "rank": 1,
    "job": {
      "id": 12345678,
      "title": "案件タイトル",
      "url": "https://crowdworks.jp/public/jobs/12345678"
    },
    "analysis": {
      "reward_score": 4,
      "competition_score": 3,
      "ai_score": 5,
      "continuity_score": 4,
      "quality_score": 5,
      "total_score": 91,
      "recommendation_reasons": [
        "生成AIを活用できる案件である"
      ],
      "concerns": [
        "応募人数が多く競争率が高い"
      ],
      "application_strategy": [
        "AI活用経験を具体例付きでアピールする"
      ],
      "overall_comment": "AIスキルとの親和性が高く、応募価値の高い案件です。"
    }
  }
]
```

---

### 備考

- ランキング結果はUTF-8で保存されます。
- 日本語はエスケープされず、そのまま読める形式で保存されます。
- インデント付きJSONとして保存されるため、人間が確認しやすい形式になっています。
- `ranked_jobs.json` は、応募優先度の確認や今後のレポート機能の入力データとして利用できます。


## ランキング結果の表示

`output/ranked_jobs.json` に保存されたランキング結果を、ターミナル上で見やすく表示できます。

この機能では、AI分析済み・ランキング済みの案件データを読み込み、上位案件の応募判断に必要な情報を整形して表示します。

---

### 実行方法

```bash
python3 src/main.py
```

---

### 入力ファイル

ランキング表示機能では、以下のファイルを読み込みます。

```text
output/ranked_jobs.json
```

このファイルには、AI分析結果をもとに `total_score` 順でランキングされた案件情報が保存されています。

---

### 表示内容

ターミナルには、各案件について以下の情報が表示されます。

| 項目 | 内容 |
|---|---|
| `rank` | 応募優先度ランキング |
| `total_score` | AIによる総合評価点 |
| `title` | 案件タイトル |
| `url` | CrowdWorks案件URL |
| `recommendation_reasons` | 応募をおすすめする理由 |
| `concerns` | 応募前に注意すべき点 |
| `application_strategy` | 採用率を高めるための応募戦略 |
| `overall_comment` | 案件全体の総評 |

---

### 表示例

```text
========================================
#1 91点
【サッカー好き歓迎】AIアパレルデザイン＆AI女性モデルを活用したSNSプロモーション担当募集！
https://crowdworks.jp/public/jobs/12345678

おすすめ理由:
- 生成AIを活用できる案件である
- 継続案件の可能性が高い

注意点:
- 応募人数が多く競争率が高い

応募戦略:
- AI活用経験を具体例付きでアピールする

総評:
AIスキルとの親和性が高く、応募価値の高い案件です。
========================================
```

---

### 備考

- デフォルトでは上位5件を表示します。
- 表示件数は引数で指定できます。
- ランキング結果が空の場合は、エラーではなく `ランキング結果がありません。` と表示されます。
- この機能は新しいファイルを出力せず、ターミナル表示のみを行います。


## Markdownレポート出力

`output/ranked_jobs.json` に保存されたランキング済み案件を、Markdown形式のレポートとして出力できます。

この機能では、AI分析済み・ランキング済みの案件情報を読み込み、応募判断に必要な情報をあとから見返しやすいMarkdownファイルとして保存します。

---

### 実行方法

```bash
python3 src/main.py
```

---

### 入力ファイル

Markdownレポート出力では、以下のファイルを読み込みます。

```text
output/ranked_jobs.json
```

このファイルには、AI分析結果をもとに `total_score` 順でランキングされた案件情報が保存されています。

---

### 出力先

Markdownレポートは以下のファイルに保存されます。

```text
output/ranked_jobs_report.md
```

出力先ディレクトリが存在しない場合は、自動で作成されます。

---

### レポート内容

Markdownレポートには、各案件について以下の情報が出力されます。

| 項目 | 内容 |
|---|---|
| `rank` | 応募優先度ランキング |
| `total_score` | AIによる総合評価点 |
| `title` | 案件タイトル |
| `url` | CrowdWorks案件URL |
| `reward_score` | 報酬の魅力度 |
| `competition_score` | 応募しやすさ |
| `ai_score` | AIとの親和性 |
| `continuity_score` | 継続案件となる可能性 |
| `quality_score` | 案件品質 |
| `recommendation_reasons` | 応募をおすすめする理由 |
| `concerns` | 応募前に注意すべき点 |
| `application_strategy` | 採用率を高めるための応募戦略 |
| `overall_comment` | 案件全体の総評 |

---

### 出力例

```markdown
# CrowdWorks Job Ranking Report

## Summary

- Total Jobs: 3
- Displayed Jobs: 3

---

## #1 91点

### 案件情報

- Title: 【サッカー好き歓迎】AIアパレルデザイン＆AI女性モデルを活用したSNSプロモーション担当募集！
- URL: https://crowdworks.jp/public/jobs/12345678

### スコア

| 項目 | 点数 |
|---|---:|
| 報酬 | 4 |
| 競争率 | 3 |
| AI適性 | 5 |
| 継続案件 | 4 |
| 案件品質 | 5 |
| 総合評価 | 91 |

### おすすめ理由

- 生成AIを活用できる案件である
- 継続案件の可能性が高い

### 注意点

- 応募人数が多く競争率が高い

### 応募戦略

- AI活用経験を具体例付きでアピールする

### 総評

AIスキルとの親和性が高く、応募価値の高い案件です。

---
```

---

### 備考

- デフォルトでは上位5件をレポート出力します。
- 出力件数は引数で指定できます。
- ランキング結果が空の場合は、`ランキング結果がありません。` を含むMarkdownが出力されます。
- MarkdownはUTF-8で保存されます。
- 日本語はエスケープされず、そのまま読める形式で保存されます。
- `ranked_jobs_report.md` は、応募候補の比較や後からの振り返りに利用できます。


## CLIオプション

`main.py` では、実行する処理をCLIオプションで指定できます。

### 使い方

```bash
python3 src/main.py [options]
```

---

### オプション一覧

| オプション | 内容 |
|---|---|
| `--rank` | `analysis_results.json` から `ranked_jobs.json` を生成する |
| `--display-ranking` | ランキング結果をターミナルに表示する |
| `--export-report` | ランキング結果をMarkdownレポートとして出力する |
| `--limit` | 表示・出力する上位件数を指定する |

---

### 実行例

ランキングJSONを生成する。

```bash
python3 src/main.py --rank
```

ランキング結果をターミナルに表示する。

```bash
python3 src/main.py --display-ranking
```

上位10件をターミナルに表示する。

```bash
python3 src/main.py --display-ranking --limit 10
```

Markdownレポートを出力する。

```bash
python3 src/main.py --export-report
```

上位10件のMarkdownレポートを出力する。

```bash
python3 src/main.py --export-report --limit 10
```

ランキング生成・表示・レポート出力をまとめて実行する。

```bash
python3 src/main.py --rank --display-ranking --export-report --limit 5
```

---

### 出力ファイル

| ファイル | 内容 |
|---|---|
| `output/ranked_jobs.json` | ランキング済み案件データ |
| `output/ranked_jobs_report.md` | Markdown形式のランキングレポート |

---

### 備考

オプションを指定しない場合は、ヘルプを表示して終了します。


## Vision

[docs/vision.md](/docs/vision.md)

---

## Features

- HTML Parser
- AI Analyzer
- Score Ranking

---

## Development

CONTRIBUTING.md

---

## Roadmap

docs/roadmap.md
