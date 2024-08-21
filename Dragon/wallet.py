import csv
import tls_client
import cloudscraper
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed

ua = UserAgent(os='linux', browsers=['firefox'])

class BulkWalletChecker:

    def __init__(self):
        self.sendRequest = tls_client.Session(client_identifier='chrome_103')
        self.cloudScraper = cloudscraper.create_scraper()
        self.shorten = lambda s: f"{s[:4]}...{s[-5:]}" if len(s) >= 9 else s
        self.skippedWallets = 0
        self.results = []
    
    def getWalletData(self, wallet: str, skipWallets: bool):
        url = f"https://gmgn.ai/defi/quotation/v1/smartmoney/sol/walletNew/{wallet}?period=7d"
        headers = {
            "User-Agent": ua.random
        }
        try:
            response = self.sendRequest.get(url, headers=headers)
        except Exception as e:
            print(f"[🐲] Error fetching data, trying backup..")
        finally:
            response = self.cloudScraper.get(url, headers=headers)


        if response.status_code == 200:
            data = response.json()
            
            if data['msg'] == "success":
                data = data['data']
                try:
                    if data['pnl_7d'] != 0 or data['pnl_30d'] != 0:
                        direct_link = f"https://gmgn.ai/sol/address/{wallet}"
                        total_profit_percent = f"{data['total_profit_pnl'] * 100:.2f}%"
                        realized_profit_7d_usd = f"${data['realized_profit_7d']:,.2f}"
                        realized_profit_30d_usd = f"${data['realized_profit_30d']:,.2f}"
                        winrate_7d = f"{data['winrate'] * 100:.2f}%" if data['winrate'] is not None else "?"
                        
                        try:
                            winrate_30data = self.sendRequest.get(f"https://gmgn.ai/defi/quotation/v1/smartmoney/sol/walletNew/{wallet}?period=30d", headers=headers).json()['data']
                            winrate_30d = f"{winrate_30data['winrate'] * 100:.2f}%" if winrate_30data['winrate'] is not None else "?"
                        except Exception as e:
                            print(f"[🐲] Error fetching data, trying backup..")
                        finally:
                            winrate_30data = self.cloudScraper.get(f"https://gmgn.ai/defi/quotation/v1/smartmoney/sol/walletNew/{wallet}?period=30d", headers=headers).json()['data']
                            winrate_30d = f"{winrate_30data['winrate'] * 100:.2f}%" if winrate_30data['winrate'] is not None else "?"


                        try:
                            tags = data['tags'] 
                        except Exception:
                            tags = "?"
                        
                        return {
                            "wallet": wallet,
                            "totalProfitPercent": total_profit_percent,
                            "7dUSDProfit": realized_profit_7d_usd,
                            "30dUSDProfit": realized_profit_30d_usd,
                            "winrate_7d": winrate_7d,
                            "winrate_30d": winrate_30d,
                            "tags": tags,
                            "directLink": direct_link
                        }
                    else:
                        if skipWallets:
                            self.skippedWallets += 1
                            print(f"[🐲] Skipped {self.skippedWallets} wallets", end="\r")
                            return None
                        else:
                            direct_link = f"https://gmgn.ai/sol/address/{wallet}"
                            return {
                                "wallet": wallet,
                                "directLink": direct_link,
                                "tags": ["Skipped"]
                            }
                except Exception as e:
                    print(f"{e} - {wallet}")
        return None
    
    def fetchWalletData(self, wallets, threads, skipWallets):

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(self.getWalletData, wallet.strip(), skipWallets): wallet for wallet in wallets}
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    self.results.append(result)
        
        result_dict = {result.pop('wallet'): result for result in self.results}

        identifier = self.shorten(list(result_dict)[0])
        filename = f"{identifier}.csv"

        path = f"Dragon/data/BulkWallet/wallets_{filename}"

        with open(path, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            header = ['Identifier'] + list(next(iter(result_dict.values())).keys())
            writer.writerow(header)
            
            for key, value in result_dict.items():
                writer.writerow([key] + list(value.values()))
        print(f"[🐲] Saved data for {len(result_dict.items())} wallets to {filename}")