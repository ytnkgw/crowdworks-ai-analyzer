# Experiments

このドキュメントでは、本プロジェクトで実施した技術検証（PoC）を記録する。

---

## Experiment 001 - CrowdWorks検索結果ページの取得

### 実施日

2026-06-04

### 背景

CrowdWorksの検索結果ページから案件一覧を取得する方法を調査する。

Playwrightによるブラウザ自動操作が必要か、それとも `curl` や `requests` のみで取得可能かを確認する。

### 仮説

検索結果がJavaScriptで動的に描画されている場合は、Playwrightが必要になる。

一方、HTML内に案件情報が埋め込まれていれば、`curl` や `requests` のみで取得できる可能性がある。

### 実施内容

以下のコマンドで検索結果ページのHTMLを取得した。

```bash
curl https://crowdworks.jp/public/jobs/group/ai_bpo
```

取得したHTMLを解析した。

### 結果

HTML内の `#vue-container` 要素に検索結果データが含まれていることを確認した。

`data` 属性内には案件一覧(JSON)が格納されており、以下のような情報が含まれていた。

* 案件ID
* 案件タイトル
* クライアント情報
* 報酬
* その他案件詳細

### 結論

検索結果はHTML取得のみで解析可能である。

現時点ではPlaywrightを導入する必要はなく、`requests` + HTML解析のみで実装を進められる見込み。

### 今後のアクション

* `requests` による取得を実装する
* `BeautifulSoup` で `#vue-container` を取得する
* `html.unescape()` を適用する
* `json.loads()` により案件一覧(JSON)へ変換する

---

### 学んだこと

* まず最もシンプルな方法を検証することが重要
* ブラウザ操作が必要とは限らない
* PoCによって不要な技術選定を避けられることを確認した

## Experiment002

requests

未実施

## Experiment003

Playwright必要？

結果：不要
