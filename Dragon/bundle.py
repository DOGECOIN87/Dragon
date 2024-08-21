import json
import tls_client
import cloudscraper
from fake_useragent import UserAgent

ua = UserAgent(os='linux', browsers=['firefox'])

class BundleFinder:

    def __init__(self):
        self.txHashes = set()
        self.formatTokens = lambda x: float(x) / 1_000_000
        self.sendRequest = tls_client.Session(client_identifier='chrome_103')
        self.cloudScraper = cloudscraper.create_scraper()
        self.shorten = lambda s: f"{s[:4]}...{s[-5:]}" if len(s) >= 9 else "?"
    
    def prettyPrint(self, bundleData: dict, contractAddress: str):

        isBundled = bundleData['bundleDetected']
        developerInformation = bundleData['developerInfo']
        transactions = bundleData['transactions']
        #transactionDetails = bundleData['transactionDetails']

        bundledAmount = developerInformation['bundledAmount']
        bundledPercentage = developerInformation['percentageOfSupply']

        text = (
            f"[🐲] Bundled: ✅\n" if isBundled else f"[🐲] Bundled: ❌\n"
            f"[🐲] Transactions: {transactions:,}"
        )

        # for transactionHash, transaction in transactionDetails.items():
        #     amounts = transaction['amounts']
        #     percentages = transaction['amountsPercentages']

        #     amounts_percentages_str = " | ".join(
        #         f"{amount:,} ({percentage:.4f}%)" for amount, percentage in zip(amounts, percentages)
        #     )3
        #     text += f"[🐲] Transaction: {transactionHash} - {amounts_percentages_str}\n"

        text += f"\n[🐲] Total Amount: {bundledAmount:,.2f}\n[🐲] Total Percentage: {bundledPercentage * 100:,.2f}%"

        filename = f"bundle_{self.shorten(contractAddress)}.json"

        with open(f'Dragon/data/bundleData/{filename}', 'w') as f:
            json.dump(bundleData, f, indent=4)

        text += f"\n[🐲] Saved data to {filename}\n"

        return text
        
    def teamTrades(self, contractAddress):
        url = f"https://gmgn.ai/defi/quotation/v1/trades/sol/{contractAddress}?limit=100&maker=&tag%5B%5D=creator&tag%5B%5D=dev_team"
        
        headers = {
            "User-Agent": ua.random
        }

        try:
            info = self.sendRequest.get(f"https://gmgn.ai/defi/quotation/v1/tokens/sol/{contractAddress}", headers=headers).json()['data']['token']
        except Exception:
            print("[🐲] Error fetching data, trying backup..")
        finally:
            info = self.cloudScraper.get(f"https://gmgn.ai/defi/quotation/v1/tokens/sol/{contractAddress}", headers=headers).json()['data']['token']


        if info['launchpad'].lower() == "pump.fun":
            totalSupply = 1000000000
        else:
            totalSupply = info['total_supply']
        
        try:
            response = self.sendRequest.get(url, headers=headers).json()['data']['history']
        except Exception as e:
            print(f"Error fetching trades: {e}")
            return self.txHashes

        for buy in response:
            if buy['event'] == "buy":
                self.txHashes.add(buy['tx_hash'])
        return self.txHashes, totalSupply

    def checkBundle(self, txHashes: set, totalSupply: int):
        total_amount = 0.00
        transactions = 0

        data = {
            "transactions": 0,
            "totalAmount": 0.00,
            "bundleDetected": False,
            "transactionDetails": {}
        }

        for txHash in self.txHashes:
            url = f"https://api.solana.fm/v0/transfers/{txHash}"
        
            try:
                response = self.sendRequest.get(url).json().get('result', {}).get('data', [])
            except Exception as e:
                print(f"[🐲] Error fetching transaction data for {txHash}")
                continue

            if isinstance(response, list):
                for action in response:
                    if action.get('action') == "transfer" and action.get("token") != "":
                        amount = self.formatTokens(action.get('amount'))
                        total_amount += amount
                        transactions += 1

        data['transactions'] = transactions
        data['totalAmount'] = total_amount

        if transactions == 1:
            data['bundleDetected'] = False
        else:
            data['bundleDetected'] = True

        transactionsDetails = {}

        for txHash in txHashes:
            url = f"https://api.solana.fm/v0/transfers/{txHash}"
            
            try:
                response = self.sendRequest.get(url).json().get('result', {}).get('data', [])
            except Exception as e:
                print(f"Error fetching transaction data for {txHash}: {e}")
                continue

            if isinstance(response, list):
                amounts = []
                for action in response:    
                    if action.get('action') == "transfer" and action.get("token") != "":
                        amount = self.formatTokens(action.get('amount'))
                        amounts.append(amount)
                if amounts:
                    amountsPercentages = [(amount / totalSupply * 100) for amount in amounts]
                    
                    transactionsDetails[txHash] = {
                        "amounts": amounts,
                        "amountsPercentages": amountsPercentages
                    }
        data['transactionDetails'] = transactionsDetails

        developerInfo = {
            "bundledAmount": total_amount,
            "percentageOfSupply": total_amount / totalSupply
        }

        data['developerInfo'] = developerInfo

        return data