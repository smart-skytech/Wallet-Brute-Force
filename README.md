# Multi-Chain Balance Checker

This script scans BNB, Ethereum, and Tron addresses for balances and attempts to brute-force a matching 12-word seed phrase for addresses with non-zero balances.

## Setup

1. **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd multi_chain_balance_checker
    ```

2. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Configure API Keys:**
    - Open `config.py` and enter your API keys for BscScan, Etherscan, and Tron.

4. **Run the Script:**
    ```bash
    python balance_checker.py
    ```

## Configuration

- **`wordlist.txt`**: Replace this file with your own list of wallet addresses.
- **`config.py`**: Add your API keys here.

## Note

Use this script responsibly. Unauthorized access to wallets is illegal and unethical.
