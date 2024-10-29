import logging
import json
import os
import time
from dotenv import load_dotenv
from ape_hardhat import providers
from utils.monitor import Monitoring  # Import the Monitoring class
from modules.analyzer import analyze_token
from utils.wallet import buy_token
from config import WALLET_ADDRESS, PRIVATE_KEY, MAX_INVESTMENT_AMOUNT

# Configure logging
logging.basicConfig(
    filename='sniper_bot.log', 
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

def load_abi(file_path):
    """Load ABI from a JSON file."""
    logging.info(f"Loading ABI from {file_path}...")
    try:
        with open(file_path, 'r') as abi_file:
            abi = json.load(abi_file)
        logging.info(f"Successfully loaded ABI from {file_path}.")
        return abi
    except Exception as e:
        logging.error(f"Failed to load ABI from {file_path}: {str(e)}")
        raise

def determine_blockchain(token, eth_tokens, bsc_tokens, sol_tokens):
    """Determine the blockchain of the token."""
    if token in eth_tokens:  # Assume eth_tokens is a list of known ETH tokens
        return 'ETH'
    elif token in bsc_tokens:  # Assume bsc_tokens is a list of known BSC tokens
        return 'BSC'
    elif token in sol_tokens:  # Assume sol_tokens is a list of known SOL tokens
        return 'SOL'
    else:
        logging.error("Unknown token blockchain")
        return None

def main():
    logging.info("Sniper bot started.")

    # Load environment variables
    load_dotenv()

    # Connect to the blockchain
    eth_url = f"https://mainnet.infura.io/v3/{os.getenv('INFURA_PROJECT_ID')}"
    bsc_url = os.getenv('BSC_NODE_URL')
    uniswap_address = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"  # Uniswap V2 Factory
    pancakeswap_address = "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"  # PancakeSwap V2 Factory
    etherscan_api_key = os.getenv('ETHERSCAN_API_KEY')
    bscscan_api_key = os.getenv('BSCSCAN_API_KEY')

    monitor = Monitoring(
        eth_url=eth_url,
        bsc_url=bsc_url,
        uniswap_address=uniswap_address,
        pancakeswap_address=pancakeswap_address,
        etherscan_api_key=etherscan_api_key,
        bscscan_api_key=bscscan_api_key
    )

    # Start monitoring for new tokens
    logging.info("Sniper bot is running...")
    
    while True:
        new_tokens = monitor.monitor_new_tokens()  # Call the method
        for token in new_tokens:
            # Add logic to determine the blockchain of the token
            blockchain = determine_blockchain(token, eth_tokens, bsc_tokens, sol_tokens)  # Implement eth_tokens, bsc_tokens, sol_tokens lists

            if analyze_token(token, providers):
                buy_token(token, float(MAX_INVESTMENT_AMOUNT), blockchain)  # Pass blockchain info
                logging.info(f"Bought token: {token} on {blockchain}")

        time.sleep(10)  # Adjust delay to manage API call frequency

if __name__ == "__main__":
    main()
