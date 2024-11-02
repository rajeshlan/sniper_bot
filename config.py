# config.py

import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Load and validate configuration variables
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
MAX_INVESTMENT_AMOUNT = float(os.getenv("MAX_INVESTMENT_AMOUNT", 0.01))
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL")
INFURA_PROJECT_ID = os.getenv("INFURA_PROJECT_ID")
BSC_NODE_URL = os.getenv("BSC_NODE_URL")

# Check for missing required variables
required_vars = ["WALLET_ADDRESS", "PRIVATE_KEY", "ETHERSCAN_API_KEY", "BSCSCAN_API_KEY", "SOLANA_RPC_URL"]
missing_vars = [var for var in required_vars if not locals().get(var)]

if missing_vars:
    logging.error(f"Missing required environment variables: {', '.join(missing_vars)}")
else:
    logging.info("Environment variables loaded successfully.")
