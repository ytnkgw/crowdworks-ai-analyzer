import config
from pathlib import Path
from fetcher import fetch_html
from parser import parse_jobs

def main():

    html = fetch_html(config.CROWDWORKS_URL)

    # 1. 実行ファイルから見た「1つ上の階層のdebugフォルダ」を定義
    # （__file__ はこのPythonファイル自身の場所を指します）
    current_dir = Path(__file__).resolve().parent
    debug_dir = current_dir.parent / config.DEBUG_DIR

    # 2. フォルダがなければ自動作成
    debug_dir.mkdir(parents=True, exist_ok=True)

    # 3. ファイルのパスを指定して書き込み
    file_path = debug_dir / config.HTML_FILENAME
    with open(
        # "../debug/crowdworks_ai_bpo.html",
        file_path,
        "w",
        encoding="utf-8",
    ) as f:
        f.write(html)

    # parse.pyのデバッグ
    jobs = parse_jobs(html)
    print(f"{len(jobs)}件")
    for job in jobs:
        print(job)


if __name__ == "__main__":
    main()