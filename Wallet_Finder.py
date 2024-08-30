# ==============================================================================
#  _    _ _    _       _       _   _    _______          _     
# | |  | | |  | |     | |     | | | |  |__   __|        | |    
# | |  | | |__| |_   _| |__   | |_| | ___ | | ___   ___ | |___ 
# | |  | |  __  | | | | '_ \  |  _  |/ _ \| |/ _ \ / _ \| / __|
# | |__| | |  | | |_| | | | | | | | | (_) | | (_) | (_) | \__ \
#  \____/|_|  |_|\__, |_| |_| |_| |_|\___/|_|\___/ \___/|_|___/
#                __/ |                                         
#               |___/                                          
# 
#                        Ahmad Tech version 1
# ==============================================================================

"""
Agreement License:

This software is licensed under the Ahmad Tech License Agreement (ATLA).

- The software is provided "as-is", without warranty of any kind, express or implied.
- You are free to use, modify, and distribute the software, provided that you include
  this license notice in any copy or substantial portion of the software.
- The author shall not be held liable for any damages arising from the use of this software.

By using this software, you agree to these terms.
"""

import sys
import random
import requests
import time
from mnemonic import Mnemonic
import bip32utils
from config import BNB_API_KEY, ETH_API_KEY

# License Key Check
REQUIRED_LICENSE_KEY = "1A47414637737494DCD513B767CE7"

def check_license():
    user_key = input("Please enter your license key: ")
    if user_key != REQUIRED_LICENSE_KEY:
        print("Invalid license key. Access denied.")
        sys.exit(1)  # Exit the script with an error code

check_license()

# The rest of the script continues only if the correct license key is provided
# Load Wordlist
def load_wordlist(filepath):
    with open(filepath, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Get Random Address
def get_random_address(wordlist):
    return random.choice(wordlist)

# Check Balance on BNB Chain
def check_balance_bnb(address):
    api_url = "https://api.bscscan.com/api?module=account&action=balance&address={}&apikey={}".format(address, BNB_API_KEY)
    response = requests.get(api_url)
    
    if response.status_code == 200:
        balance_data = response.json()
        if balance_data.get("status") == "1":  # Check if the status is OK
            try:
                balance = int(balance_data.get("result", 0)) / 10**18  # Convert from Wei to BNB
                return balance
            except ValueError:
                print(f"Could not convert balance for address {address}. Invalid response.")
                return 0
        else:
            print(f"Error checking balance for address {address}: {balance_data.get('message', 'Unknown error')}")
            return 0
    else:
        print(f"Failed to retrieve balance for address {address}. HTTP status code: {response.status_code}")
        return 0


# Check Balance on Ethereum Chain
def check_balance_eth(address):
    api_url = "https://api.etherscan.io/api?module=account&action=balance&address={}&apikey={}".format(address, ETH_API_KEY)
    response = requests.get(api_url)
    if response.status_code == 200:
        balance_data = response.json()
        balance = int(balance_data.get("result", 0)) / 10**18  # Convert from Wei to ETH
        return balance
    else:
        return 0

# Check Balance on Tron Chain
def check_balance_tron(address):
    client = Tron()
    balance = client.get_account_balance(address)
    return balance / 10**6  # Convert from Sun to TRX

# Log Non-Zero Balance
def log_non_zero_balance(address, balance, chain):
    with open('results.txt', 'a') as log_file:
        log_file.write("Chain: {}, Address: {}, Balance: {}\n".format(chain, address, balance))
    print("Non-Zero Balance Found - Chain: {}, Address: {}, Balance: {}".format(chain, address, balance))

# Generate Seed Phrase
def generate_seed_phrase():
    mnemo = Mnemonic("english")
    seed_phrase = mnemo.generate(strength=128)  # 128 bits for a 12-word phrase
    return seed_phrase

# Derive Address from Seed Phrase
def derive_address_from_seed(seed_phrase, chain):
    seed = Mnemonic.to_seed(seed_phrase)
    root_key = bip32utils.BIP32Key.fromEntropy(seed)
    if chain == 'BNB' or chain == 'ETH':
        derived_key = root_key.ChildKey(44 + bip32utils.BIP32_HARDEN).ChildKey(60 + bip32utils.BIP32_HARDEN).ChildKey(0 + bip32utils.BIP32_HARDEN).ChildKey(0).ChildKey(0)
        return derived_key.Address()
    elif chain == 'TRX':
        client = Tron()
        derived_key = client.get_account_by_mnemonic(seed_phrase)
        return derived_key.address.base58

# Main Loop
def main():
    wordlist = load_wordlist('wordlist.txt')
    while True:
        address = get_random_address(wordlist)
        balance_bnb = check_balance_bnb(address)
        if balance_bnb > 0:
            log_non_zero_balance(address, balance_bnb, 'BNB')
            match_seed_phrase(address, 'BNB')
        balance_eth = check_balance_eth(address)
        if balance_eth > 0:
            log_non_zero_balance(address, balance_eth, 'ETH')
            match_seed_phrase(address, 'ETH')
        balance_trx = check_balance_tron(address)
        if balance_trx > 0:
            log_non_zero_balance(address, balance_trx, 'TRX')
            match_seed_phrase(address, 'TRX')
        time.sleep(1)

def match_seed_phrase(address, chain):
    for _ in range(1000000):  # Brute-force attempts
        seed_phrase = generate_seed_phrase()
        derived_address = derive_address_from_seed(seed_phrase, chain)
        if derived_address == address:
            with open('matched_seed_phrases.txt', 'a') as match_file:
                match_file.write("Chain: {}, Address: {}, Seed Phrase: {}\n".format(chain, address, seed_phrase))
            print("Matched Seed Phrase Found! Chain: {}, Address: {}, Seed Phrase: {}".format(chain, address, seed_phrase))
            break

if __name__ == "__main__":
    main()
