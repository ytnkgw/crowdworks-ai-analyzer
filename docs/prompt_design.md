# Prompt Design

## Purpose

Job情報をLLMへ入力し、案件評価結果を構造化データとして取得し、応募判断を支援する。
---

## Prompt Structure

プロンプトは以下の4つの要素で構成する。

1. System Prompt
2. Input Data
3. Expected Output
4. Constraints

---

### System Prompt
AIの役割を定義する。
#### Role
- あなたはクラウドソーシング案件を分析する専門アシスタントです。
#### Principles
- 客観的な根拠をもとに案件を評価してください。
- 判断理由を必ず説明してください。
- 入力データに存在しない情報は推測しない。
- 不確実な内容は「可能性」として表現する。
- 評価理由は入力データに基づいて説明する。

---

### Input Data
Jobクラスの情報を入力する。
- title
- description
- reward
- application_deadline
- published_at
- application_count
- recruitment_count

#### Future Input
- UserProfile
- Application History

---

### Expected Output

AnalysisResultに対応するJSON形式で出力する。

#### 評価項目
- reward_score: integer (1〜5)
- competition_score: integer (1〜5)
- ai_score: integer (1〜5)
- continuity_score: integer (1〜5)
- quality_score: integer (1〜5)
- total_score: integer (0〜100)
#### 説明項目
- recommendation_reasons: list[str]  
- concerns: list[str]  
- application_strategy: list[str]  
- overall_comment: str
#### Example
```json
{
  "reward_score": 4,
  "competition_score": 3,
  "ai_score": 5,
  "continuity_score": 4,
  "quality_score": 5,
  "total_score": 91,
  "recommendation_reasons": [
    "生成AIスキルを活かせる案件である",
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
```
---

### Constraints
LLMは以下を守ること。
- 必ずJSONのみを返すこと
- Markdownを出力しないこと
- コードブロックを使用しないこと
- JSON以外の文章を出力しないこと
- JSONスキーマを変更しないこと
- 必須キーを省略しないこと
- 新しいキーを追加しないこと
- 入力データに存在しない情報は推測しないこと
- 不明な情報は null または "不明" とすること
- 各スコアは Evaluation Criteria と Score Scale に基づいて評価すること

## Future Extension

将来的にはUserProfileをPromptへ追加し、
パーソナライズ評価を行う。


## Prompt Version

Current Version: v1

- v1
  - 目的：案件単体を評価する
  - Job情報のみを入力
  - UserProfile未対応

- v2（予定）
  - 目的：ユーザーとの適合度を追加する
  - UserProfile追加
  - パーソナライズ評価対応

- v3（予定）
  - 応募履歴を考慮する
  - 過去の応募履歴を考慮