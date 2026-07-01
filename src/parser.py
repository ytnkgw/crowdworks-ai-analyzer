import json
from pathlib import Path
from typing import List
from bs4 import BeautifulSoup
import config
from models import Job
import utils


def parse_jobs(html: str) -> list[Job]:
    """
    HTMLから案件タイトル一覧を取得する。
    """
    soup = BeautifulSoup(html, "html.parser")

    # id="vue-container" の要素を取得
    container = soup.find("div", id="vue-container")

    if container and "data" in container.attrs:
        try:
            jobs: List[Job] = []
            json_data = json.loads(str(container["data"]))
            job_offers = json_data.get("searchResult", {}).get("job_offers", [])

            for item in job_offers:
                job_offer = item.get("job_offer")

                if not job_offer or "id" not in job_offer or "title" not in job_offer:
                    continue
                jobs.append(
                    Job(
                        id=job_offer.get("id"),
                        title=job_offer.get("title"),
                        url=f"{config.CW_JOB_DETAIL_URL}/{job_offer['id']}",
                    )
                )

            return jobs

        except json.JSONDecodeError:
            raise KeyError("JSONのパースに失敗しました。")
        except KeyError as e:
            raise KeyError(f"JSONの構造が想定と異なります。不足しているキー: {e}")
    else:
        raise KeyError("対象の要素が見つかりませんでした。")


def parse_job_detail(job: Job, html: str) -> Job:
    soup = BeautifulSoup(html, "html.parser")

    # 1. 案件タイトル
    # h1タグのテキストから後ろの余分なサブタイトル（カテゴリ情報等）を削ぎ落として取得
    title_tag = soup.find("h1")
    if title_tag:
        # 内包されているspan（サブタイトル）のテキストを除外して、メインタイトルのみを抽出
        title = title_tag.get_text(strip=True)
        if title:
            job.title = title.strip()

    # 2. 仕事の詳細 (全文)
    # <td class="confirm_outside_link"> 内に改行付きの全文が格納されています
    detail_td = soup.find("td", class_="confirm_outside_link")
    if detail_td:
        # <br>タグを実際の改行に変換しつつテキストを綺麗にする
        job.description = detail_td.get_text(separator="\n").strip()

    # 3. 報酬 / 4. 応募期限 / 5. 募集開始日（掲載日）
    # これらは「仕事の概要」テーブル（class="cw-table summary"）から抽出するのが確実です
    summary = {}
    for row in soup.find(
        "table", class_="summary"
    ).find_all(  # pyright: ignore[reportOptionalMemberAccess]
        "tr"
    ):
        th = row.find("th")
        td = row.find("td")
        if th and td:
            summary[th.get_text(strip=True)] = td.get_text(strip=True)
    job.reward = None
    for reward_type in ("固定報酬制", "時間単価制"):
        matched_key = next(
            (key for key in summary.keys() if reward_type in key),
            None,
        )
        if matched_key:
            reward_value = summary.get(matched_key)
            if reward_value:
                job.reward = f"{reward_type} : {reward_value}"
                break
    job.published_at = summary.get("掲載日")
    job.application_deadline = summary.get("応募期限")

    # 6. 応募状況 (応募した人、募集人数)
    # class="application_status_table" のテーブルから抽出します
    status = {}
    for row in soup.find(
        "table", class_="application_status_table"
    ).find_all(  # pyright: ignore[reportOptionalMemberAccess]
        "tr"
    ):
        th = row.find("th")
        td = row.find("td")
        if th and td:
            status[th.get_text(strip=True)] = td.get_text(strip=True)
    status_table = soup.find("table", class_="application_status_table")
    job.application_count = utils.extract_number(status.get("応募した人"))
    job.recruitment_count = utils.extract_number(status.get("募集人数"))

    return job
