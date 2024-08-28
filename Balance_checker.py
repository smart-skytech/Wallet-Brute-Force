import random
import requests
import time
from mnemonic import Mnemonic
import bip32utils
from tronpy import Tron
from config import BNB_API_KEY, ETH_API_KEY

# Load Wordlist
def load_wordlist(filepath):
    with open(filepath, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Get Random Address
def get_random_address(wordlist):
    return random.choice(wordlist)

# Check Balance on BNB Chain
def check_balance_bnb(address):
    api_url = f"https://api.bscscan.com/api?module=account&action=balance&address={address}&apikey={BNB_API_KEY}"
    response = requests.get(api_url)
    if response.status_code == 200:
        balance_data = response.json()
        balance = int(balance_data.get("result", 0)) / 10**18  # Convert from Wei to BNB
        return balance
    else:
        return 0

# Check Balance on Ethereum Chain
def check_balance_eth(address):
    api_url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&apikey={ETH_API_KEY}"
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
        log_file.write(f"Chain: {chain}, Address: {address}, Balance: {balance}\n")
    print(f"Non-Zero Balance Found - Chain: {chain}, Address: {address}, Balance: {balance}")

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
                match_file.write(f"Chain: {chain}, Address: {address}, Seed Phrase: {seed_phrase}\n")
            print(f"Matched Seed Phrase Found! Chain: {chain}, Address: {address}, Seed Phrase: {seed_phrase}")
            break

if __name__ == "__main__":
    main()
