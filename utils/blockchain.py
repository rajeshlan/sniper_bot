# utils/blockchain.py

import logging
import os
from web3 import Web3
from solana.rpc.api import Client as SolanaClient  # Import Solana Client
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class Blockchain:
    def __init__(self, url, blockchain_type='ETH'):
        """Initialize the blockchain connection."""
        self.blockchain_type = blockchain_type
        if blockchain_type in ['ETH', 'BSC']:
            self.web3 = Web3(Web3.HTTPProvider(url))
            logging.info(f"Connected to {blockchain_type} blockchain at {url}")
        elif blockchain_type == 'SOL':
            self.client = SolanaClient(url)
            logging.info(f"Connected to Solana blockchain at {url}")

    def get_balance(self, address):
        """Fetch the balance for a given address based on the blockchain type."""
        try:
            if self.blockchain_type in ['ETH', 'BSC']:
                balance = self.web3.eth.get_balance(address)
                balance_in_ether = self.web3.fromWei(balance, 'ether')
                logging.info(f"Balance for {address}: {balance_in_ether} {self.blockchain_type}")
                return balance_in_ether
            elif self.blockchain_type == 'SOL':
                balance = self.client.get_balance(address)['result']['value'] / 1_000_000_000  # Convert lamports to SOL
                logging.info(f"Balance for {address}: {balance} SOL")
                return balance
        except Exception as e:
            logging.error(f"Error fetching balance for {address}: {str(e)}")
            return None

    def send_transaction(self, transaction):
        """Send a transaction to the blockchain."""
        try:
            if self.blockchain_type in ['ETH', 'BSC']:
                tx_hash = self.web3.eth.sendTransaction(transaction)
                logging.info(f"Transaction sent: {tx_hash.hex()}")
                return tx_hash
            elif self.blockchain_type == 'SOL':
                # Implement Solana transaction sending logic here
                logging.info("Transaction sent on Solana (logic not implemented)")
                pass
        except Exception as e:
            logging.error(f"Error sending transaction: {str(e)}")
            return None


def create_providers():
    """Create and return Ethereum and Binance Smart Chain providers."""
    eth_infura_url = f"https://mainnet.infura.io/v3/{os.getenv('INFURA_PROJECT_ID')}"
    bsc_node_url = os.getenv("BSC_NODE_URL")
    
    eth_provider = Web3(Web3.HTTPProvider(eth_infura_url))
    bsc_provider = Web3(Web3.HTTPProvider(bsc_node_url))
    
    return eth_provider, bsc_provider


def check_connection(provider, name):
    """Check if the provider is connected to the blockchain."""
    if provider.is_connected():
        logging.info(f"Successfully connected to {name}!")
    else:
        logging.error(f"Failed to connect to {name}.")


# Initialize blockchain providers and check connections
if __name__ == "__main__":
    eth_provider, bsc_provider = create_providers()
    check_connection(eth_provider, "Ethereum")
    check_connection(bsc_provider, "Binance Smart Chain")
