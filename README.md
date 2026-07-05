# CrowdWorks AI Analyzer

CrowdWorks AI Analyzer は、クラウドワークスで案件を探すときの「どの案件に応募するか」「どのように応募するか」といった検討を、AIエージェント（ChatGPT、Gemini、Claude）と一緒に進めやすくするための Python CLI ツールです。

クラウドワークス上の案件情報を収集し、AIエージェントが扱いやすいデータを生成します。生成した案件データは、案件の比較、応募優先度の整理、リスク確認、提案文作成などに活用できます。

---

## 目的

CrowdWorksで案件を探す際には、以下のような課題があります。

* 案件数が多く、1件ずつ確認するのに時間がかかる
* 報酬、応募人数、納期、スキル要件などを比較しづらい
* 自分のスキルと案件の相性を判断するのに手間がかかる
* AI活用・業務自動化系の案件を効率よく見つけたい

このツールでは、案件情報の収集・構造化・AI分析・ランキングをCLI上で行い、応募判断を効率化することを目的としています。

---

## 主な機能

* CrowdWorks案件一覧ページURL指定による案件情報収集
* `jobs.json` への案件データ出力
* OpenAI APIを用いた案件分析
* ターミナル上でのランキング表示
* Markdown形式のレポート出力
* CLIオプションによる実行制御

---

## 分析項目

AI分析では、主に以下の観点から案件を評価します。

* 報酬条件
* 応募人数・競争率
* AI活用との相性
* 継続案件の可能性
* 案件内容の明確さ
* 懸念点
* 応募時の提案方針
* 総合コメント

---

## 使用技術

* Python
* OpenAI API
* BeautifulSoup
* Requests
* JSON
* Markdown
* argparse
* pytest
* Git / GitHub

開発補助として、ChatGPTおよびGitHub Copilotを活用しています。

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
| `output/jobs.json` | 継続更新される案件データ本体 |
| `output/raw/jobs_YYYYMMDD_{category}_{page:02d}.json` | URL取得ごとのraw案件データ |
| `output/snapshots/jobs_YYYYMMDD_HHMMSS.json` | 更新時点の `jobs.json` のスナップショット |
| `output/jobs_for_ai.jsonl` | ChatGPTやClaudeなどに渡しやすいJSON Lines形式の案件データ |
| `output/update_summary.json` | 最新更新時の件数・出力ファイルパスなどのサマリー |
| `output/analysis_results.json` | OpenAI APIによる案件分析結果 |
| `output/ranked_jobs.json` | 分析結果をスコア順に並べたランキング |
| `output/ranked_jobs_report.md` | ランキング結果のMarkdownレポート |

公開用サンプルとして、匿名化済みのサンプル出力を以下に配置しています。

```text
sample_outputs/sample_jobs.json
sample_outputs/sample_analysis_results.json
sample_outputs/sample_ranked_jobs.json
sample_outputs/sample_report.md
```

---

## 出力サンプル

### analysis_results.json

```json
[
  {
    "job": {
      "id": 12345678,
      "title": "業務自動化ツール開発のサンプル案件",
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
        "Pythonによるデータ処理経験を活かしやすい",
        "AI活用・業務改善の実績として展開しやすい"
      ],
      "concerns": [
        "応募人数が多く、提案文で差別化が必要"
      ],
      "application_strategy": [
        "類似ツールの開発経験を具体的に説明する",
        "作業範囲と納品物を明確に確認する"
      ],
      "overall_comment": "AI活用・業務自動化の案件として相性がよく、優先的に応募を検討できる案件です。"
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

## AI活用ポイント

このプロジェクトでは、AIを単なる文章生成ではなく、案件判断の補助ロジックとして利用しています。

具体的には、CrowdWorks案件情報を構造化したうえで、OpenAI APIに渡し、以下のような判断材料を生成します。

* 案件の応募優先度
* 自分のスキルとの相性
* 応募時に強調すべきポイント
* 事前に確認すべき懸念点
* 継続案件化の可能性
* AI活用案件としての有望度

また、開発プロセスにおいても ChatGPT / GitHub Copilot を活用し、設計補助、実装補助、README整理、テスト方針検討を行っています。

---

## 開発ステータス

現在は `v0.4.0` として、URLベースの案件収集・JSON出力・AI分析・ランキング出力を整理し、GitHub公開に向けた基本機能を整備しています。

### 完了済み

* v0.3.0: Usable Ranking Output
* v0.2.0: AI Analysis MVP
* v0.1.0: Data Collection Engine

### v0.4.0で対応済み

* URL指定による案件収集と `jobs.json` 出力
* 応募期限切れ案件の自動除外
* `--analyze` によるAI分析パイプラインの正式化
* ランキング、ターミナル表示、Markdownレポート出力の整理
* READMEのプロダクト説明・利用フローを整理
* 匿名化済みサンプル出力の追加
* 実案件データを公開しないための `.gitignore` 整備
* GitHub公開前チェック項目の整理
* pytestによるCLI・期限フィルタ・出力処理のテスト整備

---

## 今後の開発方針

今後は、アプリ内の独自分析ロジックを過度に作り込むよりも、各ユーザーが普段利用しているAIエージェントに渡しやすい案件データを生成することを重視します。

ユーザーの職務経歴、得意分野、稼働条件、収入目標などは、日常的に利用しているAIエージェント側に文脈が蓄積されている可能性があります。そのため、本ツールではCrowdWorks案件情報を網羅的かつ構造化された `jobs.json` として出力し、ユーザー自身のAIエージェントで応募判断、提案文作成、リスク確認を行いやすくすることを目指します。

OpenAI APIによる分析・ランキング機能は補助機能として残しつつ、今後は「AIエージェントに渡しやすい案件データの生成」を主軸に改善していきます。

### 優先して改善すること

* `jobs.json` の情報量と精度の向上
* 報酬、応募期限、応募人数、クライアント情報などの正規化
* AIエージェントに貼り付けやすいMarkdown/JSONL出力
* 活用プロンプト集の整備
* 匿名化済みサンプルデータの充実
* JSONスキーマ・出力仕様の明文化
* GitHub Actionsによる自動テスト

### 補助的に改善すること

* OpenAI API分析・ランキング機能の改善
* Markdownレポートの見やすさ改善
* 応募文ドラフト生成機能の検討

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