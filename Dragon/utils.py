import os
import glob

from colorama import Fore, init

def clear():
    os.system("cls||clear")

def banner():
    banner = f"""{Fore.RED}
WELCOME TO..

   (  )   /\   _                 (     
    \ |  (  \ ( \.(               )                      _____
  \  \ \  `  `   ) \             (  ___                 / _   \\
 (_`    \+   . x  ( .\            \\/   \____-----------/ (o)   \\_
- .-               \+  ;          (  O                           \\____
        DRAGON           )        \_____________  `              \\  /
(__                +- .( -'.- <. - _  VVVVVVV VV V\\                 \\/
(_____            ._._: <_ - <- _  (--  _AAAAAAA__A_/                  |
  .    /./.+-  . .- /  +--  - .     \______________//_              \\_______
  (__ ' /x  / x _/ (                                  \___'          \\     /
 , x / ( '  . / .  /                                      |           \\   /
    /  /  _/ /    +                                      /              \\/
   '  (__/                                             /                  \\
{Fore.WHITE}"""
    return banner

def choices():
    options: list = ["Bundle Checker", "Bulk Wallet Checker", "Top Traders Scraper", "All Transaction Scan", "Quit"]
    optionsChoice = "\n".join([f"[{Fore.RED}{index + 1}{Fore.WHITE}] {option}" for index, option in enumerate(options)])

    return options, optionsChoice

def searchForTxt():
    directory = os.getcwd()
    txtFiles = glob.glob(os.path.join(directory, '**', '*.txt'), recursive=True)
    files = [os.path.relpath(file, directory) for file in txtFiles]
    files.append("Select Own File")

    filesChoice = "\n".join([f"[{Fore.RED}{index + 1}{Fore.WHITE}] {file}" for index, file in enumerate(files)])

    return filesChoice, files
    

init(autoreset=True)
