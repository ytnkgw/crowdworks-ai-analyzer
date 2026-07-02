# CrowdWorks AI Analyzer

CrowdWorks AI Analyzer は、CrowdWorksの案件情報を収集し、AIで応募優先度を分析・ランキングする Python CLI ツールです。

CrowdWorks上の案件一覧・詳細ページから案件情報を取得し、OpenAI APIを用いて報酬条件、AI活用可能性、継続性、競争率、応募戦略などを分析します。
応募判断に必要な情報をJSON・Markdownレポートとして整理し、案件選定の効率化を目指します。

> 現在は個人開発中のポートフォリオプロジェクトです。
> 実案件データやAPIキーなどの機密情報はリポジトリに含めない方針で開発しています。

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

* CrowdWorks案件一覧ページのHTML取得
* 案件一覧ページのパース
* 案件詳細ページのパース
* URL指定による案件収集
* Jobモデルによる案件情報の構造化
* `jobs.json` への案件データ出力
* OpenAI APIを用いた案件分析
* AnalysisResultモデルによる分析結果の構造化
* `analysis_results.json` への分析結果出力
* `total_score` による案件ランキング
* `ranked_jobs.json` へのランキング結果出力
* ターミナル上でのランキング表示
* Markdown形式のレポート出力
* CLIオプションによる実行制御
* pytestによるテスト

---

## 分析項目

AI分析では、主に以下の観点から案件を評価します。

* 報酬条件
* 応募人数・競争率
* AI活用との相性
* 継続案件の可能性
* 案件内容の明確さ
* 自分のスキルとの親和性
* 懸念点
* 応募時の提案方針
* 総合コメント

出力結果は、応募優先度を判断しやすいようにスコアとコメントで整理します。

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

```bash
python3 -m pip install -r requirements.txt
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

主な出力ファイルは以下です。

```text
output/jobs.json
output/raw/jobs_YYYYMMDD_{category}_{page:02d}.json
output/analysis_results.json
output/ranked_jobs.json
output/ranked_jobs_report.md
```

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
      "overall_comment": "AI活用・業務自動化のポートフォリオと相性がよく、優先的に応募を検討できる案件です。"
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

現在は `v0.4.0` として、URLベースの案件収集・JSON出力・AI分析・ランキング出力の整理を進めています。

### 完了済み

* v0.3.0: Usable Ranking Output
* v0.2.0: AI Analysis MVP
* v0.1.0: Data Collection Engine

### v0.4.0で対応済み

* READMEのポートフォリオ向け整理
* サンプル出力の匿名化
* GitHub公開前チェック項目の整理

### 整理中

* v0.4.0: URL-based Job Collection Export
* GitHub公開前チェック
* CHANGELOG / Decision Log の整備

---

## 今後の改善予定

* 応募期限切れ案件の自動除外
* 案件カテゴリ別の分析精度改善
* CLIオプションの整理
* Markdownレポートの見やすさ改善
* テストカバレッジの改善
* GitHub Actionsによる自動テスト
* 分析プロンプトの改善
* 応募文ドラフト生成機能の検討

---

## 注意事項

* このツールは個人開発中のCLIツールです
* CrowdWorksの利用規約やアクセス頻度に配慮して利用してください
* 実案件データ、クライアント名、個人情報、APIキーは公開しない方針です
* 公開用サンプルデータは匿名化・サンプル化したものを使用します
* AI分析結果は応募判断の補助であり、最終判断は人間が行います

---

## License

未定

---

## Author

Yuta Nakagawa
