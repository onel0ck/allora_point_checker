URL_POST = "https://api.upshot.xyz/v2/allora/users/connect"
URL_GET = "https://api.upshot.xyz/v2/allora/points/{id}"

HEADERS_POST = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "content-type": "application/json",
    "dnt": "1",
    "origin": "https://app.allora.network",
    "priority": "u=1, i",
    "referer": "https://app.allora.network/",
    "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "macOS",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "x-api-key": "UP-0d9ed54694abdac60fd23b74"
}

HEADERS_GET = HEADERS_POST.copy()
HEADERS_GET["if-none-match"] = 'W/"180-wWc9Nj5jKOz4m2gZtCQbgGkX8dg"'

CONCURRENT_TASKS = 10
THREAD_POOL_SIZE = 4