# Decision Log

このドキュメントでは、本プロジェクトにおける重要な設計判断（Architecture Decision）を記録する。
---

# Decision 008 - AI分析結果をtotal_score順にランキングする

AI分析結果を保存した `output/analysis_results.json` を読み込み、`analysis.total_score` の高い順に案件を並び替えるランキング機能を追加する。

ランキング済みデータは `output/ranked_jobs.json` に保存し、各案件には `rank` を付与する。

## 日付

2026-07-01

### Reason

- AI分析結果をそのまま保存するだけでは、応募優先度が直感的に分かりにくい
- `total_score` を基準に並び替えることで、優先して確認すべき案件を把握しやすくなる
- `rank` を付与することで、ランキング結果を後続処理やUI表示で扱いやすくなる
- 将来的なレポート出力や応募判断支援機能の土台になる

### Result

- `analysis_results.json` を読み込み、`total_score` の降順でランキングできるようになった
- 各案件に `rank` を付与できるようになった
- ランキング結果を `output/ranked_jobs.json` として保存できるようになった
- Ranking処理のテストを追加し、正常に動作することを確認した

### Notes

初期実装では、ランキング基準は `analysis.total_score` のみとする。

同点時の詳細な並び替えルールや、`quality_score`、`ai_score`、`reward_score` を使った補助的な順位付けは、必要になったタイミングで追加する。


# Decision 007 - AI分析結果をJob情報と紐づけてJSON Exportする

OpenAI APIで取得した `AnalysisResult` は、単体ではなく `Job` 情報と紐づけた形式で `output/analysis_results.json` に保存する。

## 日付

2026-07-01

## Reason

- 分析結果だけでは、どの案件に対する評価なのか分かりにくい
- Job ID、タイトル、URLを一緒に保存することで、後から確認しやすくなる
- 次のランキング機能で `total_score` をもとに並び替えやすくなる
- 将来的なUI表示やCSV出力にも利用しやすい

## Result

- `Job` と `AnalysisResult` をセットにしたJSON出力が可能になった
- 1件および複数件の分析結果を保存できることを確認した
- `output/analysis_results.json` を次フェーズの入力データとして利用できる状態になった


# Decision　006 - OpenAI Clientを導入する

CrowdWorks案件情報をAIで分析するため、OpenAI APIを利用する `openai_client.py` を追加した。

`Job` を入力として受け取り、`Prompt Builder` で生成したプロンプトをOpenAI APIへ送信し、JSONレスポンスを `AnalysisResult` に変換する構成とした。

## 日付

2026-07-01

### 理由

- Prompt BuilderとAnalysisResultモデルを活用できる
- AI分析処理を `openai_client.py` に集約できる
- main.pyからは `analyze_job(job)` を呼び出すだけで済む
- 将来的なモデル変更やプロンプト改善に対応しやすい

### 結果

- OpenAI APIへの接続に成功
- JobをAIに分析させ、JSONレスポンスを取得できた
- JSONレスポンスをAnalysisResultへ変換できた

# Decision 005 - Decision: CrowdWorks検索結果はDOM構造ではなく、#vue-container の data 属性に格納されたJSONを解析する方式を採用する。
## 日付

2026-06-29

## 理由

* 当初HTMLタグでそれぞれの要素が格納されていると考えていたが、実際に解析してみるとdata属性にjson形式でのみ保存されていたから。



# Decision 004 - Pythonソースコードは src/ 配下に配置する。

## 日付

2026-06-29

## 理由

* プロジェクトの見通しを良くし、将来的な機能追加やテストを容易にするため。


# Decision 003 - ドキュメントファーストで開発を進める

## 日付

2026-06-28

## 背景

本プロジェクトは個人開発であるが、将来的な事業化や長期運用を視野に入れている。

コードだけでは設計意図が失われるため、ドキュメントを資産として蓄積する方針を採用する。

## 決定

設計・検証・判断・ロードマップをMarkdownで管理する。

## 理由

* 数か月後の自分でも理解しやすい
* 新しい機能追加時の判断基準になる
* GitHub上で開発経緯を追跡できる
* 将来的に他の開発者が参加しやすくなる

## 対象ドキュメント

* vision.md
* roadmap.md
* requirements.md
* architecture.md
* experiments.md
* decision_log.md

## 影響

コードだけでなく、設計や判断の履歴もプロジェクトの成果物として扱う。


# Decision 002 - PoCを実装前に必ず行う

## 日付

2026-06-28

## 背景

不要な技術選定や実装コストを避けるため、設計だけで判断せず、小さな検証を行ってから実装する開発スタイルを採用する。

## 決定

新しい技術や外部サービスを採用する場合は、必ずPoC（Proof of Concept）を実施してから本実装へ進む。

## 理由

* 思い込みによる設計ミスを防げる
* 不要なライブラリ導入を避けられる
* 実装コストを最小化できる
* Decision Logに根拠を残せる

## 影響

今後は以下の流れを基本とする。

1. Issue作成
2. PoC実施
3. Decision記録
4. 実装
5. レビュー
6. ドキュメント更新

---


# Decision 001 - Playwrightを初期実装では採用しない

## 日付

2026-06-28

## 関連Issue

- [#1 検索結果取得](https://github.com/ytnkgw/crowdworks-ai-analyzer/issues/1)

## 背景

CrowdWorksの検索結果ページはJavaScriptで構築されているように見えたため、Playwright等のブラウザ自動操作ライブラリが必要になる可能性があった。

初期実装の方針を決定するため、まずHTML取得のみで案件情報を取得できるか検証を行った。

## 検討した選択肢

### 案1：Playwrightを採用する

**メリット**

* JavaScript実行後の画面を取得できる
* 将来的な画面変更への対応力が高い

**デメリット**

* セットアップが重い
* 実行速度が遅い
* ブラウザ環境が必要になる
* 保守コストが高くなる

---

### 案2：requests + HTML解析

**メリット**

* 軽量
* 実装がシンプル
* 高速
* サーバー環境でも動作しやすい

**デメリット**

* HTML構造変更の影響を受けやすい

---

## 決定

初期実装では **requests + BeautifulSoup** を採用する。

## 理由

PoCの結果、検索結果ページのHTML内に案件一覧データが埋め込まれていることを確認した。

現時点ではブラウザ操作は不要であり、よりシンプルな構成で実装できるため。

## 影響

* 開発環境が軽量になる
* 実装速度が向上する
* 将来的に必要になった場合のみPlaywrightを導入する

---