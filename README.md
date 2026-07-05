# CrowdWorks AI Analyzer

CrowdWorks AI Analyzer は、クラウドワークスで案件を探すときの「どの案件に応募するか」「どのように応募するか」といった検討を、あなたが普段使っているAIエージェント（ChatGPT、Gemini、Claude）と一緒に進めやすくするための Python CLI ツールです。

クラウドワークス上の案件情報を収集し、AIエージェントが扱いやすいデータを生成します。生成した案件データは、案件の比較、応募優先度の整理、リスク確認、提案文作成などに活用できます。

---

## こんなときに使えます

クラウドワークスで案件を探すときには、以下のような迷いが生まれやすくなります。

* どの案件に応募するかを決めづらい
* 報酬、応募人数、納期、仕事内容などを比較しづらい
* 自分の経験やスキルと案件の相性を判断しづらい
* 応募前に確認すべきリスクや懸念点を見落としやすい
* 提案文で何を伝えればよいか整理しづらい

このツールでは、クラウドワークス上の案件情報を収集・構造化し、AIエージェントが読み取り・分析しやすいデータを生成します。このデータをあなたが普段使っているAIエージェントに読み込ませることで、案件の比較、応募優先度の整理、リスク確認、提案文作成などの相談・検討に活用できます。

---

## 主な機能

* クラウドワークスの案件一覧URLから、報酬、応募人数、納期、仕事内容、クライアント情報などの案件情報をまとめて収集します。
* 収集した案件データ一覧を、AIエージェントが読み取り・分析しやすい JSONL 形式ファイルとして出力します。
* OpenAI APIによる簡易分析を行い、案件を応募候補ランキング順に並べた Markdown 形式レポートとして出力します。

---

## 使い方の流れ

1. クラウドワークスで気になる検索条件の案件一覧URLを用意します。
    例（「ライティング・記事制作」案件一覧ページ）: https://crowdworks.jp/public/jobs/group/writing_beginner
2. [実行方法](#実行方法)に沿って、このツールで案件情報を収集し、AIエージェントが読み取り・分析しやすい形式に整理します。
3. 出力された jobs_for_ai.jsonl ファイルをアップロードするか、ファイルの中身をコピー＆ペーストして、あなたが普段使っているAIエージェントに読み込ませます。
4. AIエージェントに案件データを読み込ませたうえで、案件の比較、応募優先度の整理、リスク確認、提案文作成などを相談します。

<!-- 以下後日追加予定 -->
<!--
活用例として、以下のような使い方を想定しています。
* 検索用サンプルプロンプトを使って、条件に合う案件を探す
* 応募文作成用サンプルプロンプトを使って、提案文のたたき台を作る
* 自由形式のプロンプトで、自分の状況に合わせた案件相談を行う
### 検索用サンプルプロンプト
![検索用サンプルプロンプトの実行例](docs/images/sample-prompt-search.png)
### 応募文作成用サンプルプロンプト
![応募文作成用サンプルプロンプトの実行例](docs/images/sample-prompt-application.png)
### 自由形式プロンプト
![自由形式プロンプトの実行例](docs/images/sample-prompt-freeform.png)
-->

---

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/ytnkgw/crowdworks-ai-analyzer.git
cd crowdworks-ai-analyzer
```

### 2. 仮想環境を作成

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 依存パッケージをインストール

実行のみ行う場合は、以下を実行してください。

```bash
python3 -m pip install -r requirements.txt
```

開発・テストも行う場合は、以下を実行してください。

```bash
python3 -m pip install -r requirements-dev.txt
```

### 4. OpenAI APIキーを設定

OpenAI APIキーは、環境変数として設定してください。  

一時的に利用する場合は、以下のコマンドを実行してください。

```bash
export CW_AI_ANALYZER_OPENAI_API_KEY="your-api-key-here"
```

永続化する場合は、以下のコマンドを実行してください。

```bash
echo 'export CW_AI_ANALYZER_OPENAI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

> 注意: APIキーを `.env`、JSON、ログ、README、コミット履歴などに含めないでください。

---


## 実行方法

### 実行方法一覧を表示

```bash
python3 src/main.py --help
```

### 案件一覧URLから案件情報を収集

```bash
python3 src/main.py --collect-jobs --url "https://crowdworks.jp/public/jobs/search?..." --limit 10
```

このコマンドでは、指定したCrowdWorksのURLから案件一覧と詳細情報を取得し、以下のファイルに保存します。

```text
output/jobs.json
output/raw/jobs_YYYYMMDD_{category}_{page:02d}.json
output/snapshots/jobs_YYYYMMDD_HHMMSS.json
output/jobs_for_ai.jsonl
output/update_summary.json
```

### 収集済み案件をAI分析

事前に `output/jobs.json` が存在する状態で、以下を実行します。

```bash
python3 src/main.py --analyze --limit 10
```

分析結果は以下に保存されます。

```text
output/analysis_results.json
```

### 分析結果をランキング

事前に `output/analysis_results.json` が存在する状態で、以下を実行します。

```bash
python3 src/main.py --rank
```

ランキング結果は以下に保存されます。

```text
output/ranked_jobs.json
```

### ランキング結果をターミナル表示

```bash
python3 src/main.py --display-ranking --limit 5
```

### Markdownレポートを出力

```bash
python3 src/main.py --export-report --limit 5
```

Markdownレポートは以下に保存されます。

```text
output/ranked_jobs_report.md
```

### ランキング生成・表示・レポート出力を同時に実行

```bash
python3 src/main.py --rank --display-ranking --export-report --limit 5
```

---

## 出力ファイル

各ファイルの役割は以下です。

| ファイル | 役割 |
| --- | --- |
| `output/jobs.json` | 収集した案件情報を保存するためのJSONファイルです。同じ案件を重複して保存せず、継続的に更新するためのデータ本体として利用します。 |
| `output/jobs_for_ai.jsonl` | AIエージェントに読み込ませやすいように、jobs.jsonをJSON Line形式で出力したファイルです。 |
| `output/update_summary.json` | 最新更新時の件数・出力ファイルパスなどのサマリー |
| `output/analysis_results.json` | OpenAI APIによる案件分析結果 |
| `output/ranked_jobs.json` | 分析結果をスコア順に並べたランキング |
| `output/ranked_jobs_report.md` | ランキング結果のMarkdownレポート |
| `output/raw/jobs_YYYYMMDD_{category}_{page:02d}.json` | URL取得ごとのraw案件データ |
| `output/snapshots/jobs_YYYYMMDD_HHMMSS.json` | 更新時点の `jobs.json` のスナップショット |

公開用サンプルとして、匿名化済みのサンプル出力を以下に配置しています。

```text
sample_outputs/sample_jobs.json
sample_outputs/sample_analysis_results.json
sample_outputs/sample_ranked_jobs.json
sample_outputs/sample_report.md
```

---

## 出力サンプル

### jobs_for_ai.jsonl

```json
{"id":12345678,"title":"業務自動化ツール開発のサンプル案件","url":"https://crowdworks.jp/public/jobs/12345678","category":"システム開発","sub_category":"業務システム・ツール開発","description":"Googleスプレッドシートを使った業務管理を効率化するため、データ入力や集計作業を自動化するツールを開発する案件です。","reward":"固定報酬制 : 50,000円 〜 100,000円","application_deadline":"2026年07月31日","is_remote":true,"application_count":5,"contract_count":0,"recruitment_count":1,"favorite_count":12,"client":{"name":"sample_client","rating":4.8,"identity_verified":true},"metadata":{"first_seen_at":"2026-07-05T23:21:43+09:00","last_seen_at":"2026-07-05T23:21:43+09:00","updated_at":"2026-07-05T23:21:43+09:00","sources":[{"url":"https://crowdworks.jp/public/jobs/search?...","first_seen_at":"2026-07-05T23:21:43+09:00","last_seen_at":"2026-07-05T23:21:43+09:00","seen_count":1}]}}
```

### jobs.json

```json
[
  {
    "id": 12345678,
    "title": "業務自動化ツール開発のサンプル案件",
    "url": "https://crowdworks.jp/public/jobs/12345678",
    "category": "システム開発",
    "sub_category": "業務システム・ツール開発",
    "description": "Googleスプレッドシートを使った業務管理を効率化するため、データ入力や集計作業を自動化するツールを開発する案件です。",
    "reward": "固定報酬制 : 50,000円 〜 100,000円",
    "application_deadline": "2026年07月31日",
    "published_at": "2026年07月01日",
    "delivery_deadline": null,
    "is_remote": true,
    "application_count": 5,
    "contract_count": 0,
    "recruitment_count": 1,
    "favorite_count": 12,
    "client": {
      "name": "sample_client",
      "rating": 4.8,
      "identity_verified": true
    },
    "metadata": {
      "first_seen_at": "2026-07-05T23:21:43+09:00",
      "last_seen_at": "2026-07-05T23:21:43+09:00",
      "updated_at": "2026-07-05T23:21:43+09:00",
      "sources": [
        {
          "url": "https://crowdworks.jp/public/jobs/search?...",
          "first_seen_at": "2026-07-05T23:21:43+09:00",
          "last_seen_at": "2026-07-05T23:21:43+09:00",
          "seen_count": 1
        }
      ]
    }
  }
]
```

---

## ディレクトリ構成

```text
.
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   └── ...
├── tests/
│   └── ...
├── output/
│   └── ...
└── sample_outputs/
    └── ...
```

> ディレクトリ構成は開発中のため、今後変更される可能性があります。

---

## 注意事項

* 本ツールは学習・個人利用を目的としたCLIツールです。
* CrowdWorksの利用規約およびアクセス先サーバーへの負荷に配慮し、短時間に大量のリクエストを送信しないでください。
* 本ツールの利用にあたっては、対象サイトの利用規約・ガイドライン・robots.txt等を確認し、利用者自身の責任で適切に利用してください。
* 実案件データ、クライアント名、個人情報、APIキーは公開しない方針です
* 公開用サンプルデータは匿名化・サンプル化したものを使用します

---

## License

未定

---

## Author

Yuta Nakagawa