## [0.3.1] - 2026-07-01

### Added

#### URL-based Job Collection

- CrowdWorksの案件一覧URLから案件収集を行う `--collect-jobs` オプションを追加
- `--url` オプションで対象URLを指定できるようにした
- `--limit` で取得件数を制限できるようにした
- 指定URLから一覧HTMLと詳細HTMLを取得し、詳細情報付きのJob配列を生成できるようにした
- 収集結果を `output/jobs.json` にUTF-8・インデント付きJSONで保存できるようにした
- CLI・コレクター・エクスポートのテストを追加

### Verified

- `--collect-jobs --url <URL>` で案件収集を実行できることを確認
- `--collect-jobs` 指定時に `--url` 未指定でエラーが表示されることを確認
- `limit` 指定時に取得件数が制限されることを確認
- 収集結果が `output/jobs.json` に保存されることを確認

## [0.3.0] - 2026-07-01

### Added

#### Ranking Summary Display

- ランキング済み案件をターミナル上で見やすく表示する機能を追加
- `output/ranked_jobs.json` を読み込み、上位案件を表示できるようにした
- ランキング済み案件1件を表示用文字列に変換する `format_ranked_job()` を追加
- 複数件のランキング済み案件を表示用文字列に変換する `format_ranked_jobs()` を追加
- `rank`、`total_score`、案件タイトル、URL、おすすめ理由、注意点、応募戦略、総評を表示できるようにした
- 空のランキング結果に対応した表示処理を追加
- Ranking Summary Displayのテストを追加

#### Markdown Report Export

- ランキング済み案件をMarkdown形式のレポートとして出力する機能を追加
- `output/ranked_jobs.json` を読み込み、`output/ranked_jobs_report.md` を生成できるようにした
- ランキング済み案件1件をMarkdown形式に変換する `format_ranked_job_as_markdown()` を追加
- 複数件のランキング済み案件をMarkdownレポート形式に変換する `format_ranked_jobs_report()` を追加
- Markdownレポートをファイル出力する `export_ranked_jobs_report()` を追加
- レポートにSummary、案件情報、スコア表、おすすめ理由、注意点、応募戦略、総評を出力できるようにした
- 空のランキング結果に対応したMarkdown出力を追加
- Markdown Report Exportのテストを追加

#### CLI Options

- `main.py` にCLIオプションを追加
- `--rank` オプションで `analysis_results.json` から `ranked_jobs.json` を生成できるようにした
- `--display-ranking` オプションでランキング結果をターミナル表示できるようにした
- `--export-report` オプションでMarkdownレポートを出力できるようにした
- `--limit` オプションで表示・出力件数を指定できるようにした
- 複数オプションを同時に指定できるようにした
- オプション未指定時はヘルプを表示して終了するようにした
- CLI引数パースのテストを追加

### Verified

#### Ranking Summary Display

- `ranked_jobs.json` を読み込み、表示用関数へ渡せることを確認
- 上位案件をrank順にターミナル表示できることを確認
- `rank`、`total_score`、案件タイトル、URLが表示されることを確認
- `recommendation_reasons`、`concerns`、`application_strategy`、`overall_comment` が表示されることを確認
- 表示件数の指定が反映されることを確認
- 空配列を渡した場合でもエラーにならないことを確認

#### Markdown Report Export

- `ranked_jobs.json` を読み込み、Markdownレポート化できることを確認
- `rank`、`total_score`、案件タイトル、URLがMarkdownに出力されることを確認
- 各スコアがMarkdownテーブルとして出力されることを確認
- `recommendation_reasons`、`concerns`、`application_strategy` が箇条書きで出力されることを確認
- `overall_comment` が出力されることを確認
- 出力件数の指定が反映されることを確認
- 空配列を渡した場合でもエラーにならないことを確認
- `output/ranked_jobs_report.md` がUTF-8で保存されることを確認

#### CLI Options

- `--rank` で `output/ranked_jobs.json` を生成できることを確認
- `--display-ranking` でランキング結果をターミナル表示できることを確認
- `--export-report` で `output/ranked_jobs_report.md` を出力できることを確認
- `--limit` で表示・出力件数を変更できることを確認
- `--rank --display-ranking --export-report` の同時指定ができることを確認
- オプション未指定時にヘルプが表示され、予期しない処理が実行されないことを確認


## [0.2.0]
### Data
2026年7月1日

### Added
- OpenAI APIを利用してJobを分析する `openai_client.py` を追加
- `analyze_job(job)` により、JobからAnalysisResultを生成できるようにした
- Prompt Builderで生成したプロンプトをOpenAI APIへ送信する処理を追加
- OpenAI APIキーを環境変数から取得する設定を追加
- OpenAI Clientのモックテストを追加
- `Job` と `AnalysisResult` を紐づけた分析結果Export機能を追加
- AI分析結果を `output/analysis_results.json` に保存できるようにした
- 出力先ディレクトリが存在しない場合に自動作成する処理を追加
- 分析結果Export関数のテストを追加
- AI分析結果をもとに案件をランキングする機能を追加
- `analysis.total_score` の降順で案件を並び替える `ranking.py` を追加
- ランキング済み案件に `rank` を付与できるようにした
- ランキング結果を `output/ranked_jobs.json` に保存できるようにした
- Ranking関数のテストを追加

### Changed
- READMEにOpenAI APIキーのセットアップ方法を追記
- READMEにAI分析と結果の確認方法を追記

### Verified
- 実際のJobをOpenAI APIへ送信し、JSON形式の分析結果を取得できることを確認
- JSONレスポンスをAnalysisResultへ変換できることを確認
- 1件のJob分析結果をJSON形式で保存できることを確認
- 複数件のJob分析結果をJSON形式で保存できることを確認
- 出力JSONにJob情報とAnalysisResult情報が含まれることを確認
- 分析結果をUTF-8で日本語を正しく保存できることを確認
- `analysis_results.json` を読み込み、ランキング処理へ渡せることを確認
- `analysis.total_score` の高い順に案件が並ぶことを確認
- `rank` が1から順番に付与されることを確認
- 空配列を渡した場合でもエラーにならないことを確認
- ランキング結果をUTF-8・インデント付きJSONで保存できることを確認


## v0.1.0
### Data
2026年6月28日

### Added
- Job List Parser
- Job Detail Parser
- Job Pipeline
- Detail HTML Fetcher
- Job Model

---