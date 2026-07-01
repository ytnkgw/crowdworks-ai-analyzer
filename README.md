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
