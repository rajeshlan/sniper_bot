# sniper.py
import os
import json
import logging
import time
from typing import List, Optional
from dotenv import load_dotenv
from utils.monitor import Monitoring
from modules.analyzer import analyze_token
from utils.wallet import buy_token
from config import WALLET_ADDRESS, PRIVATE_KEY, MAX_INVESTMENT_AMOUNT, INFURA_PROJECT_ID, BSC_NODE_URL

# Configure logging
logging.basicConfig(
    filename='sniper_bot.log', 
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# Load environment variables
load_dotenv()

def load_abi(file_path: str) -> dict:
    """Load and return ABI from the specified JSON file."""
    logging.info(f"Loading ABI from {file_path}")
    try:
        with open(file_path, 'r') as abi_file:
            abi = json.load(abi_file)
        logging.info("ABI successfully loaded.")
        return abi
    except Exception as e:
        logging.error(f"Failed to load ABI from {file_path}: {str(e)}")
        raise

def determine_blockchain(token: str, eth_tokens: List[str], bsc_tokens: List[str], sol_tokens: List[str]) -> Optional[str]:
    """Determine the blockchain based on the token."""
    if token in eth_tokens:
        return 'ETH'
    elif token in bsc_tokens:
        return 'BSC'
    elif token in sol_tokens:
        return 'SOL'
    logging.error(f"Unknown blockchain for token: {token}")
    return None

def initialize_monitoring() -> Monitoring:
    """Initialize and return a Monitoring instance with blockchain URLs and factory addresses."""
    return Monitoring(
        eth_url=f"https://mainnet.infura.io/v3/{INFURA_PROJECT_ID}",
        bsc_url=BSC_NODE_URL,
        uniswap_address="0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
        pancakeswap_address="0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"
    )

def process_token(token: str, eth_tokens: List[str], bsc_tokens: List[str], sol_tokens: List[str]) -> None:
    """Analyze and buy the token if analysis is successful."""
    blockchain = determine_blockchain(token, eth_tokens, bsc_tokens, sol_tokens)
    if not blockchain:
        logging.warning(f"Skipping token {token}: Blockchain could not be determined.")
        return

    if analyze_token(token):
        try:
            buy_token(token, MAX_INVESTMENT_AMOUNT, blockchain)
            logging.info(f"Purchased {token} on {blockchain}.")
        except Exception as e:
            logging.error(f"Failed to buy {token} on {blockchain}: {e}")
    else:
        logging.info(f"Token {token} did not pass analysis.")

def main() -> None:
    logging.info("Sniper bot initiated.")
    monitor = initialize_monitoring()

    eth_tokens, bsc_tokens, sol_tokens = [], [], []  # Initialize blockchain-specific token lists

    while True:
        try:
            new_tokens = monitor.monitor_new_tokens()
            for token in new_tokens:
                process_token(token, eth_tokens, bsc_tokens, sol_tokens)
            time.sleep(10)
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            time.sleep(60)  # Retry after delay on failure

if __name__ == "__main__":
    main()
