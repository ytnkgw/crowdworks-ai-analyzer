from models import Job

from prompt_builder import build_analysis_prompt


def test_build_analysis_prompt_contains_job_details_and_output_schema() -> None:
    job = Job(
        id=1,
        title="AI翻訳案件",
        url="https://example.com/jobs/1",
        description="英語・中国語の翻訳案件です。",
        reward="5000円",
        application_deadline="2026-07-10",
        published_at="2026-07-01",
        application_count=12,
        recruitment_count=3,
    )

    prompt = build_analysis_prompt(job)
    print(prompt)

    assert "あなたはクラウドソーシング案件を分析する専門アシスタントです。" in prompt
    assert "AI翻訳案件" in prompt
    assert "5000円" in prompt
    assert '"reward_score"' in prompt
    assert '"overall_comment"' in prompt


def test_build_analysis_prompt_includes_field_descriptions() -> None:
    job = Job(
        id=2,
        title="データ整形案件",
        url="https://example.com/jobs/2",
    )

    prompt = build_analysis_prompt(job)
    print(prompt)

    assert "各フィールドの説明" in prompt
    assert "reward_score" in prompt
    assert "応募前に注意すべき点" in prompt
