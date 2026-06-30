# Prompt Design

## Purpose

Job情報をLLMへ入力し、
案件評価および応募判断に必要な分析結果を取得する。

---

## Prompt Structure

プロンプトは以下の3つの要素で構成する。

1. System Prompt
2. User Prompt
3. Expected Output

---

## System Prompt

AIの役割を定義する。

例

- あなたはクラウドソーシング案件を分析する専門アシスタントです。
- 客観的な根拠をもとに案件を評価してください。
- 判断理由を必ず説明してください。
- 不確実な情報は推測ではなく可能性として表現してください。

---

## User Prompt

Jobクラスの情報を入力する。

入力項目

- title
- description
- reward
- application_deadline
- published_at
- application_count
- recruitment_count

---

## Expected Output

AnalysisResultに対応するJSON形式で出力する。

評価項目

- reward_score
- competition_score
- ai_score
- continuity_score
- quality_score
- total_score

説明項目

- strengths
- concerns
- application_strategy
- summary

---

## Future Extension

将来的にはUserProfileをPromptへ追加し、
パーソナライズ評価を行う。


## Prompt Version

Current Version: v1

- v1
  - Job情報のみを入力
  - UserProfile未対応

- v2（予定）
  - UserProfile追加
  - パーソナライズ評価対応

- v3（予定）
  - 過去の応募履歴を考慮