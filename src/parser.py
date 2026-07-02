import json
import html as html_lib
from pathlib import Path
from typing import List
from bs4 import BeautifulSoup
import config
from models import Client, Job
import utils


def _to_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return utils.extract_number(value)
    return None


def _to_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        normalized = value.strip().replace(",", "")
        if not normalized or normalized == "-":
            return None
        try:
            return float(normalized)
        except ValueError:
            return None
    return None


def _to_bool(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized == "true":
            return True
        if normalized == "false":
            return False
    return None


def _is_client_empty(client: Client) -> bool:
    return (
        client.id is None
        and client.name is None
        and client.rating is None
        and client.identity_verified is None
        and client.rule_checked is None
        and client.jobs_posted_count is None
        and client.project_finished_rate is None
    )


def _extract_client_from_header(soup: BeautifulSoup) -> Client | None:
    name_tag = soup.select_one(".client_name a") or soup.select_one(".client_name")
    rating_tag = soup.select_one(".client_rating .star_container")

    name = name_tag.get_text(strip=True) if name_tag else None
    rating = _to_float(rating_tag.get_text(strip=True)) if rating_tag else None

    client = Client(name=name or None, rating=rating)
    return None if _is_client_empty(client) else client


def _extract_client_from_data_attr(soup: BeautifulSoup) -> Client | None:
    container = soup.select_one("#client_detail_information_container")
    if not container:
        return _extract_client_from_header(soup)

    raw_data = container.get("data")
    if not isinstance(raw_data, str) or not raw_data.strip():
        return _extract_client_from_header(soup)

    decoded = html_lib.unescape(raw_data)
    try:
        payload = json.loads(decoded)
    except json.JSONDecodeError:
        return _extract_client_from_header(soup)

    if not isinstance(payload, dict):
        return _extract_client_from_header(soup)

    client = Client(
        id=_to_int(payload.get("userId")),
        name=(
            payload.get("userDisplayName")
            if isinstance(payload.get("userDisplayName"), str)
            else None
        ),
        rating=_to_float(payload.get("averageScore")),
        identity_verified=_to_bool(payload.get("isIdentityVerified")),
        rule_checked=_to_bool(payload.get("isEmployerRuleCheckSucceeded")),
        jobs_posted_count=_to_int(payload.get("jobOfferAchievementCount")),
        project_finished_rate=_to_int(payload.get("projectFinishedRate")),
    )

    if _is_client_empty(client):
        return _extract_client_from_header(soup)

    return client


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

    # 0. クライアント情報
    job.client = _extract_client_from_data_attr(soup)

    # 1. カテゴリ / サブカテゴリ (パンくず)
    # 末尾の「の仕事・求人」を取り除いて保存する
    job.category = None
    job.sub_category = None
    for anchor in soup.select("ol.cw-breadcrumb li a"):
        href_attr = anchor.get("href")
        href = href_attr if isinstance(href_attr, str) else ""
        text = anchor.get_text(strip=True)
        if not text:
            continue

        normalized_text = text.removesuffix("の仕事・求人").strip()
        value = normalized_text or None

        if "/public/jobs/group/" in href and job.category is None:
            job.category = value
        elif "/public/jobs/category/" in href and job.sub_category is None:
            job.sub_category = value

    # 2. 案件タイトル
    # h1タグのテキストから後ろの余分なサブタイトル（カテゴリ情報等）を削ぎ落として取得
    title_tag = soup.find("h1")
    if title_tag:
        # 内包されているspan（サブタイトル）のテキストを除外して、メインタイトルのみを抽出
        title = title_tag.get_text(strip=True)
        if title:
            job.title = title.strip()

    # 3. 仕事の詳細 (全文)
    # <td class="confirm_outside_link"> 内に改行付きの全文が格納されています
    detail_td = soup.find("td", class_="confirm_outside_link")
    if detail_td:
        # <br>タグを実際の改行に変換しつつテキストを綺麗にする
        job.description = detail_td.get_text(separator="\n").strip()

    # 4. 報酬 / 5. 応募期限 / 6. 募集開始日（掲載日）
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

    # 7. 応募状況 (応募した人、契約した人、募集人数、気になる！リスト)
    # ラベル(th)を基準に抽出し、HTML構造変更に比較的強い実装にする
    status: dict[str, str] = {}
    for row in soup.select(
        "section.application_status table.application_status_table tr"
    ):
        th = row.find("th")
        td = row.find("td")
        if not th or not td:
            continue

        label = th.get_text(strip=True)
        value = td.get_text(strip=True)
        if label:
            status[label] = value

    job.application_count = utils.extract_number(status.get("応募した人"))
    job.contract_count = utils.extract_number(status.get("契約した人"))
    job.recruitment_count = utils.extract_number(status.get("募集人数"))
    job.favorite_count = utils.extract_number(status.get("気になる！リスト"))

    return job
