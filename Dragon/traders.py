import csv
import tls_client
import cloudscraper
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

ua = UserAgent(os='linux', browsers=['firefox'])

class TopTraders:

    def __init__(self):
        self.sendRequest = tls_client.Session(client_identifier='chrome_103')
        self.cloudScraper = cloudscraper.create_scraper()
        self.shorten = lambda s: f"{s[:4]}...{s[-5:]}" if len(s) >= 9 else s
        self.allData = {}
        self.allAddresses = set()
        self.addressFrequency = defaultdict(int)
        self.totalTraders = 0

    def fetchTopTraders(self, contractAddress: str):
        print(ua.random)
        headers = {
            "User-Agent": ua.random
        }
        url = f"https://gmgn.ai/defi/quotation/v1/tokens/top_traders/sol/{contractAddress}?orderby=profit&direction=desc"
        try:
            response = self.sendRequest.get(url, headers=headers)
            return response.json().get('data', [])
        except Exception:
            print(f"[🐲] Error fetching data, trying backup..")
        finally:
            response = self.cloudScraper.get(url, headers=headers)
            return response.json().get('data', [])
                   
    def topTraderData(self, contractAddresses, threads):
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(self.fetchTopTraders, address): address for address in contractAddresses}
            
            for future in as_completed(futures):
                contract_address = futures[future]
                response = future.result()

                
                self.allData[contract_address] = {}
                self.totalTraders += len(response)

                for top_trader in response:
                    address = top_trader['address']
                    self.addressFrequency[address] += 1 
                    self.allAddresses.add(address)
                    
                    bought_usd = f"${top_trader['total_cost']:,.2f}"
                    total_profit = f"${top_trader['realized_profit']:,.2f}"
                    unrealized_profit = f"${top_trader['unrealized_profit']:,.2f}"
                    multiplier = f"{top_trader['profit_change']:.2f}x" if top_trader['profit_change'] is not None else "?"
                    buys = f"{top_trader['buy_tx_count_cur']}"
                    sells = f"{top_trader['sell_tx_count_cur']}"
                    
                    self.allData[contract_address][address] = {
                        "boughtUsd": bought_usd,
                        "totalProfit": total_profit,
                        "unrealizedProfit": unrealized_profit,
                        "multiplier": multiplier,
                        "buys": buys,
                        "sells": sells
                    }
        repeatedAddresses = [address for address, count in self.addressFrequency.items() if count > 1]
        
        identifier = self.shorten(list(self.allAddresses)[0])
        
        with open(f'Dragon/data/TopTraders/allTopAddresses_{identifier}.txt', 'w') as av:
            for address in self.allAddresses:
                av.write(f"{address}\n")

        with open(f'Dragon/data/TopTraders/repeatedTopTraders_{identifier}.txt', 'w') as ra:
            for address in repeatedAddresses:
                ra.write(f"{address}\n")

        with open(f'Dragon/data/TopTraders/topTraders_{identifier}.csv', 'w', newline='') as outfile:
            writer = csv.writer(outfile)

            header = ['Identifier'] + list(next(iter(self.allData.values())).keys())
            writer.writerow(header)
        
            for key, value in self.allData.items():
                writer.writerow([key] + list(value.values()))

        print(f"[🐲] Saved {self.totalTraders} top traders for {len(contractAddresses)} tokens")
        print(f"[🐲] Saved {len(self.allAddresses)} top trader addresses to topTraders_{identifier}.csv")
        print(f"[🐲] Saved {len(repeatedAddresses)} repeated addresses to repeatedTopTraders_{identifier}.txt")

        return