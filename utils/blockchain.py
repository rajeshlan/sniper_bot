from web3 import Web3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ethereum and Binance Smart Chain providers
ETH_INFURA_URL = f"https://mainnet.infura.io/v3/{os.getenv('INFURA_PROJECT_ID')}"
eth_provider = Web3(Web3.HTTPProvider(ETH_INFURA_URL))

BSC_NODE_URL = os.getenv("BSC_NODE_URL")
bsc_provider = Web3(Web3.HTTPProvider(BSC_NODE_URL))

# Check Connection
def check_connection(provider, name):
    if provider.is_connected():
        print(f"Successfully connected to {name}!")
    else:
        print(f"Failed to connect to {name}.")

check_connection(eth_provider, "Ethereum")
check_connection(bsc_provider, "Binance Smart Chain")
