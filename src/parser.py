import json
from pathlib import Path
from typing import List
from bs4 import BeautifulSoup
import config
from models import Job


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


def parse_job_detail(html: str):
    soup = BeautifulSoup(html, "html.parser")

    print("=== 抽出結果 ===")

    # 1. 案件タイトル
    # h1タグのテキストから後ろの余分なサブタイトル（カテゴリ情報等）を削ぎ落として取得
    title_tag = soup.find("h1")
    if title_tag:
        # 内包されているspan（サブタイトル）のテキストを除外して、メインタイトルのみを抽出
        main_title = str(title_tag.find(text=True, recursive=False)).strip()
        print(f"■ 案件タイトル:\n{main_title}\n")

    # 2. 仕事の詳細 (全文)
    # <td class="confirm_outside_link"> 内に改行付きの全文が格納されています
    detail_td = soup.find("td", class_="confirm_outside_link")
    if detail_td:
        # <br>タグを実際の改行に変換しつつテキストを綺麗にする
        detail_text = detail_td.get_text(separator="\n").strip()
        print(f"■ 仕事の詳細 (全文):\n{detail_text}\n")

    # 3. 報酬 / 4. 応募期限 / 5. 募集開始日（掲載日）
    # これらは「仕事の概要」テーブル（class="cw-table summary"）から抽出するのが確実です
    summary_table = soup.find("table", class_="summary")
    if summary_table:
        for row in summary_table.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if th and td:
                th_text = th.get_text(strip=True)
                td_text = td.get_text(strip=True)

            if "固定報酬" in th_text:
                print(f"■ 報酬: {td_text}")
            elif "掲載日" in th_text:
                print(f"■ 募集開始日: {td_text}")
            elif "応募期限" in th_text:
                print(f"■ 応募期限: {td_text}")

    # 6. 応募状況 (応募した人、募集人数)
    # class="application_status_table" のテーブルから抽出します
    status_table = soup.find("table", class_="application_status_table")
    if status_table:
        print("\n■ 応募状況:")
        for row in status_table.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if th and td:
                label = th.get_text(strip=True)
                value = td.get_text(strip=True)
                if label in ["応募した人", "募集人数"]:
                    print(f"  ・{label}: {value}")

    print("================")
