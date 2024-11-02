# utils/snipe.py

import logging
import time
import requests
from web3 import Web3
from utils.blockchain import Blockchain
from utils.wallet import buy_token
from utils.monitor import Monitoring
from modules.analyzer import analyze_token
from config import (BSC_NODE_URL, WALLET_ADDRESS, PRIVATE_KEY, MAX_INVESTMENT_AMOUNT, 
                    ETHERSCAN_API_KEY, BSCSCAN_API_KEY)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def fetch_abi_from_scan(chain, contract_address, retries=3, delay=5):
    """Fetch the ABI of a contract from Etherscan or BscScan."""
    api_key = ETHERSCAN_API_KEY if chain == "ethereum" else BSCSCAN_API_KEY
    scan_url = {
        "ethereum": f"https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}",
        "bsc": f"https://api.bscscan.com/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}"
    }.get(chain)

    if not scan_url:
        logging.error("Unsupported chain type.")
        return None

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(scan_url)
            data = response.json()
            if data.get("status") == "1":
                logging.info(f"Successfully fetched ABI for {contract_address} on {chain}.")
                return data["result"]
            else:
                logging.warning(f"Attempt {attempt}/{retries} failed: {data.get('message', 'Unknown error')}")
                time.sleep(delay)
        except Exception as e:
            logging.error(f"Error fetching ABI: {str(e)} - Attempt {attempt}/{retries}")
            time.sleep(delay)

    logging.error(f"Failed to fetch ABI for {contract_address} on {chain} after {retries} attempts.")
    return None


def connect_to_blockchain(provider_url, retries=3, delay=5):
    """Connect to a blockchain provider and return the Web3 object."""
    for attempt in range(1, retries + 1):
        provider = Web3(Web3.HTTPProvider(provider_url))
        if provider.is_connected():
            logging.info(f"Successfully connected to blockchain at {provider_url}")
            return provider
        else:
            logging.warning(f"Connection attempt {attempt}/{retries} failed.")
            time.sleep(delay)

    logging.error(f"Failed to connect to the blockchain at {provider_url} after {retries} attempts.")
    return None


def snipe_tokens(provider, router_address, chain, max_attempts=5, delay_between_attempts=10):
    """Monitor and snipe tokens based on liquidity events."""
    logging.info("Starting token sniping process...")

    router_abi = fetch_abi_from_scan(chain, router_address)
    if not router_abi:
        logging.error("Failed to fetch router ABI. Exiting.")
        return

    # Create an instance of Monitoring to use its methods
    monitor = Monitoring(
        eth_url='https://mainnet.infura.io/v3/e3664c8b17c54e7190eea5218400539d',
        bsc_url='https://bsc-dataseed.binance.org/',
        uniswap_address='0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f',
        pancakeswap_address='0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73',
        etherscan_api_key=ETHERSCAN_API_KEY,
        bscscan_api_key=BSCSCAN_API_KEY
    )

    try:
        while True:
            new_tokens = monitor.monitor_new_tokens()

            if not new_tokens:
                logging.info("No new tokens detected. Waiting for new liquidity events...")
                time.sleep(delay_between_attempts)
                continue

            for token in new_tokens:
                if analyze_token(token, provider):
                    logging.info(f"Attempting to snipe token: {token}")
                    success = False
                    attempts = 0

                    while not success and attempts < max_attempts:
                        try:
                            buy_token(token, float(MAX_INVESTMENT_AMOUNT))
                            logging.info(f"Successfully sniped token: {token}")
                            success = True
                        except Exception as e:
                            attempts += 1
                            logging.error(f"Failed to snipe token {token}: {str(e)} - Attempt {attempts}/{max_attempts}")
                            if attempts < max_attempts:
                                time.sleep(delay_between_attempts)

                    if not success:
                        logging.error(f"Max attempts reached. Could not snipe token {token}. Moving to next.")

            time.sleep(delay_between_attempts)

    except KeyboardInterrupt:
        logging.info("Sniping process interrupted. Exiting gracefully...")
    except Exception as e:
        logging.error(f"Unexpected error in sniping process: {str(e)}")


def main():
    """Main entry point for the token sniping functionality."""
    logging.info("Token sniping functionality initialized.")

    provider = connect_to_blockchain(BSC_NODE_URL)
    
    if not provider:
        logging.error("Unable to initialize sniping due to provider connection issues.")
        return

    router_address = Web3.to_checksum_address('0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73')  # PancakeSwap example
    chain = 'bsc' if 'bsc' in BSC_NODE_URL else 'ethereum'

    snipe_tokens(provider, router_address, chain)


if __name__ == "__main__":
    main()
