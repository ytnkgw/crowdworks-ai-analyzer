# Development Rules

本リポジトリでは、**CrowdWorks AI Analyzer** の開発において、再現性・拡張性・継続性を重視した開発ルールを採用する。

---

# 1. 基本方針

## Issue First

実装前に必ずIssueを作成する。

---

## Small PR

1 PR = 1機能（または1責務）

---

## PoC First

実装前に必ず検証（PoC）を行い、必要性と実現可能性を確認する。

---

## Documentation First

仕様変更・設計変更時は、コードより先にドキュメントを更新する。

---

## Design & Decision as Asset

コードだけでなく、設計判断もプロダクト資産として残す。

重要な意思決定は必ず `decision_log.md` に記録する。

---

## Continuous Improvement

「動くものを作る」のではなく、**長期的に改善可能な設計**を優先する。

---

# 2. 開発フロー

新機能は以下の流れで進める。

```text
Issue作成
    ↓
設計レビュー
    ↓
ブランチ作成
    ↓
実装
    ↓
テスト
    ↓
Pull Request
    ↓
マージ
    ↓
Decision Log更新
    ↓
CHANGELOG更新（必要に応じて）
    ↓
Weekly Review更新
```

---

# 3. Issue命名規則

Issueは目的ごとにプレフィックスを付与する。

| Prefix       | 用途       |
| ------------ | -------- |
| `[Feature]`  | 新機能      |
| `[Bug]`      | バグ修正     |
| `[Refactor]` | リファクタリング |
| `[Design]`   | 設計    |
| `[Research]` | 調査・検証    |
| `[Docs]`     | ドキュメント   |
| `[Test]`     | テスト      |
| `[Chore]`    | 環境構築・保守  |

### 例

```text
[Feature] 検索結果取得
[Research] CrowdWorks HTML解析
[Docs] README更新
[Chore] Python開発環境構築
```

---

# 4. ブランチ命名規則

```
feature/<feature-name>
bugfix/<bug-name>
refactor/<target>
docs/<document-name>
research/<topic>
chore/<task>
```

### 例

```text
feature/html-parser
feature/json-export
research/crowdworks-html
docs/update-readme
chore/python-setup
```

---

# 5. コミットメッセージ規則

以下の Conventional Commits を基本とする。

| Prefix   | 内容       |
| -------- | -------- |
| feat     | 新機能      |
| fix      | バグ修正     |
| docs     | ドキュメント   |
| refactor | リファクタリング |
| test     | テスト      |
| chore    | その他      |

### 例

```text
feat: add HTML parser

fix: handle missing URL

docs: update architecture

refactor: split parser module

chore: setup Python environment
```

---

# 6. Pull Request

Pull Requestでは以下を確認する。

* Issueとの対応
* Acceptance Criteriaを満たしているか
* 不要なコードが含まれていないか
* ドキュメント更新が必要か

---

# 7. ドキュメント更新ルール

機能追加・設計変更時は、必要に応じて以下を更新する。

| ドキュメント               | 更新タイミング     |
| -------------------- | ----------- |
| requirements.md      | 要件変更        |
| architecture.md      | 構成変更        |
| decision_log.md      | 設計判断        |
| roadmap.md           | 計画変更        |
| product_metrics.md   | KPI変更       |
| business_model.md    | 収益モデル変更     |
| CHANGELOG.md         | ユーザー影響のある変更 |
| weekly/YYYY-MM-DD.md | 週次振り返り      |

---

# 8. 使用技術

* Python
* OpenAI API
* BeautifulSoup
* Requests
* JSON
* Markdown
* argparse
* pytest
* Git / GitHub

---

# 9. Issue完了条件

以下を満たした場合に、そのIssueは完了とする。

* Acceptance Criteriaを満たしている
* コードレビュー完了
* 必要なテストを実施
* 必要なドキュメントを更新
* mainブランチへマージ済み

---

# 10. 開発時の考え方

実装速度よりも、継続して改善できる設計を優先する。

「動くものを素早く作る」のではなく、

**「長く育てられるプロダクトを作る」**

ことを開発方針とする。
