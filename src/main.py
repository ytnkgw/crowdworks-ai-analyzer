from fetcher import fetch_html


URL = "https://crowdworks.jp/public/jobs/group/ai_bpo"


def main():

    html = fetch_html(URL)

    print(html[:500])


if __name__ == "__main__":
    main()