from Dragon import utils, BundleFinder, ScanAllTx, BulkWalletChecker, TopTraders

banner = utils.banner()
print(banner)

options = utils.choices()[0]
optionsChoice = utils.choices()[1]

getTxtFiles = utils.searchForTxt()

print(f"{optionsChoice}\n")

bundle = BundleFinder()
scan = ScanAllTx()
walletCheck = BulkWalletChecker()
topTraders = TopTraders()

while True:
    try:
        while True:
            optionsInput = int(input("[❓] Choice > "))
            if optionsInput in [1, 2, 3, 4]:
                print(f"[🐲] Selected {options[optionsInput - 1]}")
                break 
            else:
                print("[🐲] Invalid choice.")
    
        if optionsInput == 1:
            while True:
                contractAddress = input("[❓] Contract Address > ")
                
                if len(contractAddress) not in [43, 44]:
                    print(f"[🐲] Invalid length.")
                else:
                    transactionHashes = bundle.teamTrades(contractAddress)
                    bundleData = bundle.checkBundle(transactionHashes[0], transactionHashes[1])
                    formatData = bundle.prettyPrint(bundleData, contractAddress)
                    print(f"\n{formatData}")
                    print(f"\n{utils.choices()[1]}\n")
                    break
        elif optionsInput == 2:
            if len(getTxtFiles) < 2:
                print("[🐲] No files available.")
                continue 

            print(f"\n{getTxtFiles[0]}\n")

            try:
                while True:
                    fileSelectionOption = int(input("[❓] File Choice > "))

                    if fileSelectionOption > len(getTxtFiles[1]):
                        print("[🐲] Invalid input.")
                    elif getTxtFiles[1][fileSelectionOption - 1] == "Select Own File":
                        print(f"[🐲] Selected {getTxtFiles[1][fileSelectionOption - 1]}")
                        while True:
                            fileDirectory = input("[🐲] Enter filename/path > ")
                            try:
                                with open(fileDirectory, 'r') as f:
                                    wallets = f.read().splitlines()
                                if wallets and wallets != []:
                                    print(f"[🐲] Loaded {len(wallets)}")
                                    break 
                                else:
                                    print(f"[🐲] Error occurred, file may be empty.")
                                    continue
                            except Exception as e:
                                print(f"[🐲] File directory not found.")
                                continue
                    else:
                        print(f"[🐲] Selected {getTxtFiles[1][fileSelectionOption - 1]}")
                        fileDirectory = getTxtFiles[1][fileSelectionOption - 1]

                        with open(fileDirectory, 'r') as f:
                            wallets = f.read().splitlines()
                        if wallets and wallets != []:
                            print(f"[🐲] Loaded {len(wallets)} wallets")
                            break 
                        else:
                            print(f"[🐲] Error occurred, file may be empty.")
                            continue 

                while True:
                    threads = input("[❓] Threads > ")
                    try:
                        threads = int(threads)
                        if threads > 100:
                            print(f"[🐲] Do not use more than 100 threads. Automatically set threads to 40.")
                            threads = 40
                    except ValueError:
                        threads = 40
                        print(f"[🐲] Invalid input. Defaulting to 40 threads.")
                        break
                    break

                while True:
                    skipWallets = False
                    skipWalletsInput = input("[❓] Skip wallets with no 7d or 30d PnL data? (Y/N) > ")

                    if skipWalletsInput.upper() not in ["Y", "N"]:
                        print("[🐲] Invalid input.")
                        continue 
                    if skipWalletsInput.upper() == "N":
                        skipWallets = False
                    else:
                        skipWallets = True
                    walletData = walletCheck.fetchWalletData(wallets, threads=threads, skipWallets=skipWallets)
                    break  

            except IndexError:
                print("[🐲] File choice out of range.")
            except ValueError:
                print("[🐲] Invalid input.")
            continue 
        elif optionsInput == 3:
            while True:
                threads = input("[❓] Threads > ")
                try:
                    threads = int(threads)
                    if threads > 100:
                        print(f"[🐲] Do not use more than 100 threads. Automatically set threads to 40.")
                        threads = 40
                except ValueError:
                    threads = 40
                    print(f"[🐲] Invalid input. Defaulting to 40 threads.")
                break
            with open('Dragon/data/TopTraders/tokens.txt', 'r') as fp:
                contractAddresses = fp.read().splitlines()
                if contractAddresses and contractAddresses != []:
                    print(f"[🐲] Loaded {len(contractAddresses)} contract addresses")
                else:
                    print(f"[🐲] Error occurred, file may be empty.")
                    print(f"\n{optionsChoice}\n")
                    continue
                    
                data = topTraders.topTraderData(contractAddresses, threads)
                break

        elif optionsInput == 4:
            while True:
                contractAddress = input("[❓] Contract Address > ")

                if len(contractAddress) not in [43, 44]:
                    print(f"[🐲] Invalid length.")
                else:
                    break

            while True:
                threads = input("[❓] Threads > ")

                try:
                    threads = int(threads)
                    if threads > 100:
                        print(f"[🐲] Do not use more than 100 threads. Automatically set threads to 40.")
                        threads = 40
                except ValueError:
                    threads = 40 
                    print(f"[🐲] Invalid input. Defaulting to 40 threads.")
                    break
                break

            go = scan.getAllTxMakers(contractAddress, threads)
            print(f"\n{utils.choices()[1]}\n")


        elif optionsInput == 5:
            print(f"[🐲] Thank you for using Dragon.")
            break

    except ValueError as e:
        print("[🐲] Invalid input.")


