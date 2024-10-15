import asyncio
import aiohttp
from datetime import datetime
import random
from colorama import init, Fore, Style

init(autoreset=True)

from utils import read_wallets
from config import URL_POST, URL_GET, HEADERS_POST, HEADERS_GET

CONCURRENT_TASKS = 50
MAX_CONCURRENT_REQUESTS = 20
SUMM = 0

async def process_wallet(session, wallet, headers_post, headers_get, url_post, url_get, semaphore):
    global SUMM
    async with semaphore:
        try:
            if wallet.startswith("0x"):
                payload = {"allora_address": None, "evm_address": wallet}
            else:
                payload = {"allora_address": wallet, "evm_address": None}

            async with session.post(url_post, headers=headers_post, json=payload) as post_response:
                post_data = await post_response.json()
                data_id = post_data.get("data", {}).get("id")

            if not data_id:
                print(f"{Fore.LIGHTBLACK_EX}INFO: ADDRESS:{wallet} POINT:0.0")
                return f"ADDRESS:{wallet} POINT:0.0"

            async with session.get(url_get.format(id=data_id), headers=headers_get) as get_response:
                get_data = await get_response.json()

            stats_key = "evm_leaderboard_stats" if wallet.startswith("0x") else "allora_leaderboard_stats"
            points = get_data.get("data", {}).get(stats_key, {}).get("total_points", 0)

            if points > 0:
                print(f"{Fore.GREEN}SUCCESS: ADDRESS:{wallet} POINT:{points}")
                SUMM += float(points)
            else:
                print(f"{Fore.LIGHTBLACK_EX}INFO: ADDRESS:{wallet} POINT:0.0")

            return f"ADDRESS:{wallet} POINT:{points}"

        except AttributeError:
            print(f"{Fore.LIGHTBLACK_EX}INFO: ADDRESS:{wallet} POINT:0.0")
            return f"ADDRESS:{wallet} POINT:0.0"
        except Exception as e:
            print(f"{Fore.RED}ERROR: ADDRESS:{wallet} - {str(e)}")
            return f"ADDRESS:{wallet} POINT:ERROR"

async def main():
    wallets = read_wallets('wallets.txt')
    log_filename = datetime.now().strftime("result_%H%M-%d-%m-%y.log")

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=MAX_CONCURRENT_REQUESTS, keepalive_timeout=60)) as session:
        tasks = [process_wallet(session, wallet, HEADERS_POST, HEADERS_GET, URL_POST, URL_GET, semaphore) for wallet in wallets]
        results = await asyncio.gather(*tasks)

    with open(log_filename, 'w') as f:
        for result in results:
            f.write(f"{result}\n")

    print(f"\nTOTAL POINT: {SUMM}\nRESULT: {log_filename}")

if __name__ == "__main__":
    asyncio.run(main())