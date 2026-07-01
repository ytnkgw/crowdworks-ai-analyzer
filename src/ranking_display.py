def format_ranked_job(item: dict) -> str:
    """ランキング済み案件1件を表示用文字列に変換する。"""
    job = item.get("job", {})
    analysis = item.get("analysis", {})

    recommendation_reasons = analysis.get("recommendation_reasons", []) or []
    concerns = analysis.get("concerns", []) or []
    application_strategy = analysis.get("application_strategy", []) or []
    overall_comment = analysis.get("overall_comment", "") or ""

    lines = [
        "=" * 40,
        f"#{item.get('rank', '-') } {analysis.get('total_score', '-') }点",
        job.get("title", "-"),
        job.get("url", "-"),
        "",
        "おすすめ理由:",
        *[f"- {reason}" for reason in recommendation_reasons],
        "",
        "注意点:",
        *[f"- {concern}" for concern in concerns],
        "",
        "応募戦略:",
        *[f"- {strategy}" for strategy in application_strategy],
        "",
        "総評:",
        overall_comment,
        "=" * 40,
    ]
    return "\n".join(lines)


def format_ranked_jobs(items: list[dict], limit: int = 5) -> str:
    """ランキング済み案件リストを表示用文字列に変換する。"""
    if not items:
        return "ランキング結果がありません。"

    limited_items = items[:limit]
    formatted_items = [format_ranked_job(item) for item in limited_items]
    return "\n\n".join(formatted_items)
