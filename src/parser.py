import json
from pathlib import Path
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
            json_data = json.loads(container["data"])
            job_offers = (
                json_data.get("searchResult", {}).get("job_offers", [])
            )

            for item in job_offers:
                job_offer = item.get("job_offer")

    
                if not job_offer or "id" not in job_offer or "title" not in job_offer:
                    continue
                jobs.append(Job(id=job_offer.get("id"), title=job_offer.get("title")))

            return jobs

        except json.JSONDecodeError:
            raise KeyError("JSONのパースに失敗しました。")
        except KeyError as e:
            raise KeyError(f"JSONの構造が想定と異なります。不足しているキー: {e}")
    else:
        raise KeyError("対象の要素が見つかりませんでした。")