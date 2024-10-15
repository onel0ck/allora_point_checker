import json
import brotli
import zlib
import aiohttp
import asyncio

def read_wallets(filepath):
    with open(filepath, 'r') as file:
        return [line.strip() for line in file.readlines()]

def read_proxies(filepath):
    with open(filepath, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def log_result(wallet, data_id, points, rank, log_filename):
    with open(log_filename, 'a') as file:
        file.write(f"Wallet: {wallet} | ID: {data_id} | Points: {points} | Rank: {rank}\n")

async def decompress_response(response):
    try:
        content_encoding = response.headers.get('Content-Encoding', '')
        content_type = response.headers.get('Content-Type', '')

        if 'application/json' in content_type:
            return await response.read()

        if 'br' in content_encoding:
            return brotli.decompress(await response.read())
        elif 'gzip' in content_encoding:
            return zlib.decompress(await response.read(), 16 + zlib.MAX_WBITS)
        elif 'deflate' in content_encoding:
            return zlib.decompress(await response.read())
        else:
            print("No compression detected")
            return await response.read()
    except Exception as e:
        print(f"Error during decompression: {e}")
        return None

async def send_post_request(session, wallet, headers, url, proxy):
    if wallet.startswith("0x"):
        payload = {"allora_address": None, "evm_address": wallet}
    else:
        payload = {"allora_address": wallet, "evm_address": None}

    try:
        async with session.post(url, headers=headers, json=payload, proxy=proxy, timeout=10) as response:
            response.raise_for_status()
            if response.content_length:
                return await response.json()
            else:
                print(f"Empty response received for wallet: {wallet}")
                return None
    except asyncio.TimeoutError:
        print(f"Timeout occurred for wallet: {wallet}")
    except aiohttp.ClientResponseError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except aiohttp.ClientError as req_err:
        print(f"Request error occurred: {req_err}")
    except json.JSONDecodeError as json_err:
        print(f"JSON decode error: {json_err} for wallet: {wallet}")
    except Exception as err:
        print(f"Other error occurred: {err} for wallet: {wallet}")
    
    return None

async def send_get_request(session, data_id, headers, url, proxy):
    try:
        async with session.get(url.format(id=data_id), headers=headers, proxy=proxy, timeout=10) as response:
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                decompressed_content = await decompress_response(response)
                if decompressed_content:
                    decompressed_text = decompressed_content.decode('utf-8')
                    return json.loads(decompressed_text)
                else:
                    print(f"Failed to decompress content for ID: {data_id}")
            else:
                print(f"Unexpected content type for ID: {data_id}")
            return None
    except asyncio.TimeoutError:
        print(f"Timeout occurred for ID: {data_id}")
    except aiohttp.ClientResponseError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except json.JSONDecodeError as json_err:
        print(f"JSON decode error: {json_err} for ID: {data_id}")
    except Exception as err:
        print(f"Other error occurred: {err} for ID: {data_id}")
    
    return None