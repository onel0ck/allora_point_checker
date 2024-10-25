import asyncio
import aiohttp
from datetime import datetime
import random
from colorama import init, Fore, Style
from aiohttp import ClientTimeout

init(autoreset=True)

from utils import read_wallets
from config import URL_POST, URL_GET, HEADERS_POST, HEADERS_GET, CONCURRENT_TASKS

CONCURRENT_TASKS = 50
MAX_CONCURRENT_REQUESTS = 20
TOTAL_POINTS = 0
SUCCESSFUL_WALLETS = 0
FAILED_WALLETS = 0
ERROR_WALLETS = []

class WalletResult:
    def __init__(self, wallet, points=0, rank=0, error=None, status="SUCCESS"):
        self.wallet = wallet
        self.points = points
        self.rank = rank
        self.error = error
        self.status = status  # SUCCESS, ERROR, INFO
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

async def process_wallet(session, wallet, headers_post, headers_get, url_post, url_get, semaphore):
    global TOTAL_POINTS, SUCCESSFUL_WALLETS, FAILED_WALLETS, ERROR_WALLETS
    
    async with semaphore:
        result = WalletResult(wallet)
        try:
            if wallet.startswith("0x"):
                payload = {"allora_address": None, "evm_address": wallet}
            else:
                payload = {"allora_address": wallet, "evm_address": None}

            timeout = ClientTimeout(total=15)
            async with session.post(url_post, headers=headers_post, json=payload, timeout=timeout) as post_response:
                try:
                    post_response.raise_for_status()
                    post_data = await post_response.json()
                    data_id = post_data.get("data", {}).get("id")
                except aiohttp.ClientResponseError as e:
                    result.status = "ERROR"
                    result.error = f"POST Request failed: HTTP {e.status}"
                    ERROR_WALLETS.append(wallet)
                    print(f"{Fore.RED}ERROR: POST request failed for {wallet}: HTTP {e.status}")
                    return result

            if not data_id:
                result.status = "INFO"
                result.points = 0
                FAILED_WALLETS += 1
                print(f"{Fore.LIGHTBLACK_EX}INFO: {wallet} | Points: 0.00")
                return result

            await asyncio.sleep(random.uniform(0.5, 1.5))

            async with session.get(url_get.format(id=data_id), headers=headers_get, timeout=timeout) as get_response:
                try:
                    get_response.raise_for_status()
                    get_data = await get_response.json()
                except aiohttp.ClientResponseError as e:
                    result.status = "ERROR"
                    result.error = f"GET Request failed: HTTP {e.status}"
                    ERROR_WALLETS.append(wallet)
                    print(f"{Fore.RED}ERROR: GET request failed for {wallet}: HTTP {e.status}")
                    return result

            stats_key = "evm_leaderboard_stats" if wallet.startswith("0x") else "allora_leaderboard_stats"
            stats = get_data.get("data", {}).get(stats_key, {})
            
            if stats is None:
                result.points = 0
                result.rank = 0
                result.status = "INFO"
                print(f"{Fore.LIGHTBLACK_EX}INFO: {wallet} | Points: 0.00")
                FAILED_WALLETS += 1
                return result
                
            points = stats.get("total_points", 0)
            rank = stats.get("rank", 0)

            result.points = points
            result.rank = rank

            if points > 0:
                print(f"{Fore.GREEN}SUCCESS: {wallet} | Points: {points:.2f} | Rank: {rank}")
                TOTAL_POINTS += float(points)
                SUCCESSFUL_WALLETS += 1
            else:
                print(f"{Fore.LIGHTBLACK_EX}INFO: {wallet} | Points: 0.00")
                FAILED_WALLETS += 1
                result.status = "INFO"

        except asyncio.TimeoutError:
            result.status = "ERROR"
            result.error = "Request timeout"
            ERROR_WALLETS.append(wallet)
            print(f"{Fore.RED}ERROR: Timeout for {wallet}")
        except Exception as e:
            if "NoneType" in str(e):
                result.status = "INFO"
                result.points = 0
                result.rank = 0
                print(f"{Fore.LIGHTBLACK_EX}INFO: {wallet} | Points: 0.00")
                FAILED_WALLETS += 1
            else:
                result.status = "ERROR"
                result.error = str(e)
                ERROR_WALLETS.append(wallet)
                print(f"{Fore.RED}ERROR: {wallet} - {str(e)}")

        return result

def write_detailed_log(results, filename):
    with open(filename, 'w', encoding='utf-8') as f:

        f.write("=== Allora Points Checker Report ===\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("=== Summary ===\n")
        f.write(f"Total Points: {TOTAL_POINTS:.2f}\n")
        f.write(f"Successful Wallets: {SUCCESSFUL_WALLETS}\n")
        f.write(f"Zero Wallets: {FAILED_WALLETS}\n")
        f.write(f"Error Wallets: {len(ERROR_WALLETS)}\n\n")

        f.write("=== Detailed Results ===\n")
        for result in sorted(results, key=lambda x: x.points, reverse=True):
            f.write(f"Wallet: {result.wallet}\n")
            f.write(f"Status: {result.status}\n")
            f.write(f"Points: {result.points:.2f}\n")
            if result.rank > 0:
                f.write(f"Rank: {result.rank}\n")
            if result.error:
                f.write(f"Error: {result.error}\n")
            f.write(f"Timestamp: {result.timestamp}\n")
            f.write("-" * 50 + "\n")

        if ERROR_WALLETS:
            f.write("\n=== Error Wallets ===\n")
            for wallet in ERROR_WALLETS:
                f.write(f"{wallet}\n")

        f.write(f"\n=== Final Results ===\n")
        f.write(f"Total Points: {TOTAL_POINTS:.2f}\n")
        f.write(f"Successful Wallets: {SUCCESSFUL_WALLETS}\n")
        f.write(f"Zero Wallets: {FAILED_WALLETS}\n")
        f.write(f"Error Wallets: {len(ERROR_WALLETS)}\n")

async def main():
    wallets = read_wallets('wallets.txt')
    log_filename = datetime.now().strftime("detailed_result_%Y%m%d_%H%M%S.log")

    print(f"{Fore.CYAN}Starting Allora Points Checker...")
    print(f"Total wallets to check: {len(wallets)}\n")

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT_REQUESTS, ssl=False)

    async with aiohttp.ClientSession(connector=connector, trust_env=True) as session:
        tasks = [process_wallet(session, wallet, HEADERS_POST, HEADERS_GET, URL_POST, URL_GET, semaphore) 
                for wallet in wallets]
        results = await asyncio.gather(*tasks)

    write_detailed_log(results, log_filename)

    print(f"\n{Fore.CYAN}=== Final Results ===")
    print(f"Total Points: {TOTAL_POINTS:.2f}")
    print(f"Successful Wallets: {SUCCESSFUL_WALLETS}")
    print(f"Zero Wallets: {FAILED_WALLETS}")
    print(f"Error Wallets: {len(ERROR_WALLETS)}")
    print(f"\nDetailed results saved to: {log_filename}")

if __name__ == "__main__":
    asyncio.run(main())
