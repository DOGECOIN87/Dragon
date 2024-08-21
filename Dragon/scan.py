import tls_client
import cloudscraper
import concurrent.futures
from fake_useragent import UserAgent
from threading import Lock

ua = UserAgent(os='linux', browsers=['firefox'])

class ScanAllTx:

    def __init__(self):
        self.sendRequest = tls_client.Session(client_identifier='chrome_103')
        self.cloudScraper = cloudscraper.create_scraper()
        self.shorten = lambda s: f"{s[:4]}...{s[-5:]}" if len(s) >= 9 else s
        self.lock = Lock()

    def request(self, url: str):
        headers = {
            "User-Agent": ua.random
        }
        try:
            response = self.sendRequest.get(url, headers=headers).json()
            data = response['data']['history']
            paginator = response['data'].get('next')
            return data, paginator
        except Exception:
            print(f"[🐲] Error fetching data, trying backup..")
        finally:
            response = self.cloudScraper.get(url, headers=headers).json()
            data = response['data']['history']
            paginator = response['data'].get('next')
            return data, paginator
            

    def getAllTxMakers(self, contractAddress: str, threads: int):
        base_url = f"https://gmgn.ai/defi/quotation/v1/trades/sol/{contractAddress}?limit=100"
        paginator = None
        urls = []

        headers = {
            "User-Agent": ua.random
        }
        
        print(f"[🐲] Starting... please wait.\n")

        while True:
            url = f"{base_url}&cursor={paginator}" if paginator else base_url
            urls.append(url)
            
            try:
                response = self.sendRequest.get(url, headers=headers).json()
            except Exception:
                print(f"[🐲] Error fetching data, trying backup..")
            finally:
                response = self.cloudScraper.get(url, headers=headers).json()
            paginator = response['data'].get('next')

            if not paginator:
                break

        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_url = {executor.submit(self.request, url): url for url in urls}
            all_makers = set()

            for future in concurrent.futures.as_completed(future_to_url):
                history, _ = future.result()
                with self.lock: 
                    for maker in history:
                        event = maker['event']
                        if event == "buy":
                            print(f"[🐲] Wallet: {maker['maker']} | Hash: {maker['tx_hash']} | Type: {event}")
                            all_makers.add(maker['maker'])
                        else:
                            pass
        
        filename = f"wallets_{self.shorten(contractAddress)}.txt"
        
        with open(f"Dragon/data/ScanAllTx/{filename}", "w") as file:
            for maker in sorted(all_makers):  
                file.write(f"{maker}\n")
        print(f"[🐲] Found and wrote {len(all_makers)} wallets from {contractAddress} to {filename}")
