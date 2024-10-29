import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Load configuration variables from environment
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
MAX_INVESTMENT_AMOUNT = os.getenv("MAX_INVESTMENT_AMOUNT")  # Maximum investment amount
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")          # Etherscan API key
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")              # BscScan API key
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL")                # Solana RPC URL

# Log the results
if all([WALLET_ADDRESS, PRIVATE_KEY, MAX_INVESTMENT_AMOUNT, ETHERSCAN_API_KEY, BSCSCAN_API_KEY]):
    logging.info("Environment variables loaded successfully.")
else:
    logging.error("Failed to load environment variables. Check your .env file.")
