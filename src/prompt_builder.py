from __future__ import annotations

from models import Job

SYSTEM_PROMPT = """
あなたはクラウドソーシング案件を分析する専門アシスタントです。

【Role】
- クラウドソーシング案件を客観的に分析する。

【Principles】
- 客観的な根拠をもとに評価する。
- 判断理由を必ず説明する。
- 入力データに存在しない情報は推測しない。
- 不確実な内容は「可能性」として表現する。
- 評価理由は入力データに基づいて説明する。
""".strip()

INPUT_TEMPLATE = """
案件情報

- title: {title}
- description: {description}
- reward: {reward}
- application_deadline: {application_deadline}
- published_at: {published_at}
- application_count: {application_count}
- recruitment_count: {recruitment_count}
""".strip()

OUTPUT_SCHEMA = """
出力形式（JSON）

{
  "reward_score": 1,
  "competition_score": 1,
  "ai_score": 1,
  "continuity_score": 1,
  "quality_score": 1,
  "total_score": 0,
  "recommendation_reasons": [
    ""
  ],
  "concerns": [
    ""
  ],
  "application_strategy": [
    ""
  ],
  "overall_comment": ""
}
""".strip()

SAMPLE_OUTPUT = """
サンプル出力

{
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
""".strip()

FIELD_DESCRIPTION = """
各フィールドの説明

- reward_score
    - 型: integer
    - 範囲: 1〜5
    - 説明: 報酬の魅力度
- competition_score
    - 型: integer
    - 範囲: 1〜5
    - 説明: 応募しやすさ
- ai_score
    - 型: integer
    - 範囲: 1〜5
    - 説明: AIとの親和性
- continuity_score
    - 型: integer
    - 範囲: 1〜5
    - 説明: 継続案件となる可能性
- quality_score
    - 型: integer
    - 範囲: 1〜5
    - 説明: 案件品質
- total_score
    - 型: integer
    - 範囲: 0〜100
    - 説明: 5つのスコアを総合的に評価した案件全体の応募価値
- recommendation_reasons
    - 型: array[string]
    - 応募をおすすめする理由を出力する。
    - 必要な件数だけ出力する。通常は2〜5件程度。
- concerns
    - 型: array[string]
    - 応募前に注意すべき点を出力する。
    - 箇条書きで1〜5件程度記載する。
- application_strategy
    - 型: array[string]
    - 採用率を高めるための応募戦略を出力する。
    - 箇条書きで2〜5件程度記載する。
- overall_comment
    - 型: string
    - 案件全体の総評を出力する。
    - 2〜4文程度で簡潔にまとめる。
""".strip()

SCORE_SCALE = """
スコア基準

- reward_score
    - 5: 非常に魅力的（報酬水準が高く、内容とのバランスも良い）
    - 4: 魅力的（報酬は良好）
    - 3: 標準的（妥当）
    - 2: やや低い（報酬面に課題がある）
    - 1: 魅力が低い（報酬面で不利）
- competition_score
    - 5: 非常に魅力的（競争が緩く応募しやすい）
    - 4: 魅力的（比較的応募しやすい）
    - 3: 標準的（平均的）
    - 2: やや低い（競争がやや厳しい）
    - 1: 魅力が低い（競争が非常に厳しい）
- ai_score
    - 5: 非常に魅力的（生成AI活用が非常にしやすい）
    - 4: 魅力的（AI活用がしやすい）
    - 3: 標準的（AI活用可能）
    - 2: やや低い（AI活用に制約がある）
    - 1: 魅力が低い（AI活用が難しい）
- continuity_score
    - 5: 非常に魅力的（継続案件の可能性が高い）
    - 4: 魅力的（継続の可能性がある）
    - 3: 標準的（継続性は普通）
    - 2: やや低い（継続性は低め）
    - 1: 魅力が低い（継続性がほぼ見込めない）
- quality_score
    - 5: 非常に魅力的（案件内容が具体的で品質が高い）
    - 4: 魅力的（品質面で良好）
    - 3: 標準的（品質は平均的）
    - 2: やや低い（品質面に不安がある）
    - 1: 魅力が低い（品質面で不安が大きい）
- total_score
    - 各評価項目の 1〜5 点を重み付き平均し、0〜100 点に換算する
    - 重みの合計は 100% とし、端数は四捨五入する
    - 報酬・競争率・AI適性・継続案件・案件品質を主な要素とする。
        - 報酬：20%
        - 競争率：20%
        - AI適性：20%
        - 継続案件：20%
        - 案件品質：20%
""".strip()

EVALUATION_CRITERIA = """
評価基準

1. 報酬 (reward_score)
- 報酬金額
- 時給換算の妥当性
- 固定報酬か成果報酬か
- 作業内容に対するコストパフォーマンス

2. 競争率 (competition_score)
- 応募人数
- 募集人数
- 掲載日からの経過日数
- 人気案件である可能性

3. AI適性 (ai_score)
- 生成AIの活用が可能か
- AIによる効率化が期待できるか
- AIスキルを活かせる案件か

4. 継続案件 (continuity_score)
- 長期契約の可能性
- 継続依頼の記載
- 定期的な業務であるか

5. 案件品質 (quality_score)
- 業務内容が具体的か
- 求めるスキルが明確か
- 成果物が定義されているか
- 発注者の意図が読み取りやすいか
""".strip()

CONSTRAINTS = """
制約

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
""".strip()


def build_analysis_prompt(job: Job) -> str:
    """案件情報から LLM へ渡す分析用プロンプトを生成する。"""

    input_data = INPUT_TEMPLATE.format(
        title=job.title,
        description=job.description or "未記載",
        reward=job.reward or "未記載",
        application_deadline=job.application_deadline or "未記載",
        published_at=job.published_at or "未記載",
        application_count=(
            job.application_count if job.application_count is not None else "未記載"
        ),
        recruitment_count=(
            job.recruitment_count if job.recruitment_count is not None else "未記載"
        ),
    )

    return f"""
# System Prompt
{SYSTEM_PROMPT}

# Input Data
{input_data}

# Evaluation Criteria
{EVALUATION_CRITERIA}

# Expected Output
{OUTPUT_SCHEMA}

# Field Descriptions
{FIELD_DESCRIPTION}

# Score Scale
{SCORE_SCALE}

# Sample Output
{SAMPLE_OUTPUT}

# Constraints
{CONSTRAINTS}
""".strip()
