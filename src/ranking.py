def rank_job_analysis_results(items: list[dict]) -> list[dict]:
    """分析結果を total_score の高い順に並び替え、rank を付与する。"""
    if not items:
        return []

    ranked_items = sorted(
        items,
        key=lambda item: item.get("analysis", {}).get("total_score", 0),
        reverse=True,
    )

    results = []
    for index, item in enumerate(ranked_items, start=1):
        new_item = {
            "rank": index,
            "job": item.get("job", {}),
            "analysis": item.get("analysis", {}),
        }
        results.append(new_item)

    return results
