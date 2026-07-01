from pathlib import Path


def format_ranked_job_as_markdown(item: dict) -> str:
    """ランキング済み案件1件をMarkdown形式に変換する。"""
    job = item.get("job", {})
    analysis = item.get("analysis", {})

    recommendation_reasons = analysis.get("recommendation_reasons", []) or []
    concerns = analysis.get("concerns", []) or []
    application_strategy = analysis.get("application_strategy", []) or []
    overall_comment = analysis.get("overall_comment", "") or ""

    lines = [
        f"## #{item.get('rank', '-')} : {analysis.get('total_score', '-')}点",
        "",
        "### 案件情報",
        f"- Title: {job.get('title', '-')}",
        f"- URL: {job.get('url', '-')}",
        "",
        "### スコア",
        "| 項目 | 点数 |",
        "|---|---:|",
        f"| 報酬 | {analysis.get('reward_score', '-')} |",
        f"| 競争率 | {analysis.get('competition_score', '-')} |",
        f"| AI適性 | {analysis.get('ai_score', '-')} |",
        f"| 継続案件 | {analysis.get('continuity_score', '-')} |",
        f"| 案件品質 | {analysis.get('quality_score', '-')} |",
        f"| 総合評価 | {analysis.get('total_score', '-')} |",
        "",
        "### おすすめ理由",
        *[f"- {reason}" for reason in recommendation_reasons],
        "",
        "### 注意点",
        *[f"- {concern}" for concern in concerns],
        "",
        "### 応募戦略",
        *[f"- {strategy}" for strategy in application_strategy],
        "",
        "### 総評",
        overall_comment,
        "",
        "---",
    ]
    return "\n".join(lines)


def format_ranked_jobs_report(items: list[dict], limit: int = 5) -> str:
    """ランキング済み案件リストをMarkdownレポート形式に変換する。"""
    if not items:
        return "# CrowdWorks Job Ranking Report\n\nランキング結果がありません。"

    limited_items = items[:limit]
    sections = [
        "# CrowdWorks Job Ranking Report",
        "",
        "## Summary",
        "",
        f"- Total Jobs: {len(items)}",
        f"- Displayed Jobs: {len(limited_items)}",
        "",
        "---",
        "",
    ]

    sections.extend(format_ranked_job_as_markdown(item) for item in limited_items)
    return "\n".join(sections).rstrip() + "\n"


def export_ranked_jobs_report(
    items: list[dict], output_path: str, limit: int = 5
) -> None:
    """ランキング済み案件リストをMarkdownレポートとして保存する。"""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(format_ranked_jobs_report(items, limit=limit), encoding="utf-8")
