import config
from pathlib import Path
from fetcher import fetch_html
from models import Job
from parser import parse_jobs
from parser import parse_job_detail


def main():

    html = fetch_html(config.CW_JOB_LIST_URL)

    jobs = parse_jobs(html)

    for job in jobs:
        detail_html = fetch_html(job.url)
        parse_job_detail(job, detail_html)

    # 確認
    for job in jobs:
        print(job)

    # # 1. 実行ファイルから見た「1つ上の階層のdebugフォルダ」を定義
    # # （__file__ はこのPythonファイル自身の場所を指します）
    # current_dir = Path(__file__).resolve().parent
    # debug_dir = current_dir.parent / config.DEBUG_DIR

    # # 2. フォルダがなければ自動作成
    # debug_dir.mkdir(parents=True, exist_ok=True)

    # # 3. ファイルのパスを指定して書き込み
    # file_path = debug_dir / config.HTML_FILENAME
    # with open(
    #     # "../debug/crowdworks_ai_bpo.html",
    #     file_path,
    #     "w",
    #     encoding="utf-8",
    # ) as f:
    #     f.write(html)

    # parse.pyのデバッグ
    # jobs = parse_jobs(html)
    # print(f"{len(jobs)}件")
    # for job in jobs:
    #     print(job)
    # html = read_debug_html("cw_job_detail.html")
    # job = Job(id=0, title="テスト案件", url="")
    # job = parse_job_detail(job, html)
    # print(job)


def read_debug_html(filename: str) -> str:
    """debug フォルダから HTML ファイルを読み込みます。"""
    current_dir = Path(__file__).resolve().parent
    debug_path = current_dir.parent / config.DEBUG_DIR / filename
    with open(debug_path, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    main()
