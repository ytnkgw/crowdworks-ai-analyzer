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
