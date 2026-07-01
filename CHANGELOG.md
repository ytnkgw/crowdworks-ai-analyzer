## [Unreleased]

### Added

- OpenAI APIを利用してJobを分析する `openai_client.py` を追加
- `analyze_job(job)` により、JobからAnalysisResultを生成できるようにした
- Prompt Builderで生成したプロンプトをOpenAI APIへ送信する処理を追加
- OpenAI APIキーを環境変数から取得する設定を追加
- OpenAI Clientのモックテストを追加

### Changed

- READMEにOpenAI APIキーのセットアップ方法を追記

### Verified

- 実際のJobをOpenAI APIへ送信し、JSON形式の分析結果を取得できることを確認
- JSONレスポンスをAnalysisResultへ変換できることを確認

## v0.1.0

### Added

- Job List Parser
- Job Detail Parser
- Job Pipeline
- Detail HTML Fetcher
- Job Model

---

## v0.2.0

・JSON出力

---

## v0.3.0

・AI分析
