import config
import requests


def fetch_html(url: str) -> str:
    """
    指定されたURLからHTMLを取得する。

    Args:
        url (str): 取得対象のURL

    Returns:
        str: 取得したHTML
    """
    response = requests.get(
        url,
        timeout=config.REQUEST_TIMEOUT,
        )

    response.raise_for_status()

    return response.text