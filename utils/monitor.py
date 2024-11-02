# utils/monitor.py
import logging
import time
import requests
from web3 import Web3
import os
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

class Monitoring:
    def __init__(self, eth_url, bsc_url, uniswap_address, pancakeswap_address, etherscan_api_key, bscscan_api_key):
        self.eth_web3 = Web3(Web3.HTTPProvider(eth_url))
        self.bsc_web3 = Web3(Web3.HTTPProvider(bsc_url))
        self.uniswap_address = uniswap_address
        self.pancakeswap_address = pancakeswap_address
        self.etherscan_api_key = etherscan_api_key
        self.bscscan_api_key = bscscan_api_key

        # Check connection to both networks
        self.check_connection()

    def check_connection(self):
        if not self.eth_web3.is_connected():
            logging.error("Failed to connect to Ethereum. Please check the ETH node URL.")
        else:
            logging.info("Successfully connected to Ethereum!")

        if not self.bsc_web3.is_connected():
            logging.error("Failed to connect to Binance Smart Chain. Please check the BSC node URL.")
        else:
            logging.info("Successfully connected to Binance Smart Chain!")

    def monitor_new_tokens(self):
        logging.info("Starting to monitor Uniswap (Ethereum) and PancakeSwap (BSC)...")

        # Fetch ABIs for Uniswap and PancakeSwap
        uniswap_abi = self.get_abi(self.uniswap_address, network='ethereum')
        pancakeswap_abi = self.get_abi(self.pancakeswap_address, network='bsc')

        # Subscribe to PairCreated events
        if uniswap_abi:
            self.subscribe_to_event(uniswap_abi, self.uniswap_address, self.eth_web3, 'Uniswap')

        if pancakeswap_abi:
            self.subscribe_to_event(pancakeswap_abi, self.pancakeswap_address, self.bsc_web3, 'PancakeSwap')

    def get_abi(self, contract_address, network):
        if network == 'ethereum':
            url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={self.etherscan_api_key}"
        elif network == 'bsc':
            url = f"https://api.bscscan.com/api?module=contract&action=getabi&address={contract_address}&apikey={self.bscscan_api_key}"
        else:
            logging.error(f"Unsupported network: {network}")
            return None

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()

            if data.get('status') == '1':
                return json.loads(data['result'])
            else:
                logging.error(f"Failed to fetch ABI for {contract_address} on {network}: {data.get('message')}")
                return None
        except requests.RequestException as e:
            logging.error(f"Error while fetching ABI for {contract_address}: {e}")
            return None

    def subscribe_to_event(self, abi, contract_address, web3_instance, dex_name):
        try:
            contract = web3_instance.eth.contract(address=contract_address, abi=abi)
            pair_created_event = contract.events.PairCreated.create_filter(fromBlock='latest')

            logging.info(f"Subscribed to PairCreated event on {dex_name}. Monitoring for new pairs...")

            # Continuously poll for new events
            while True:
                try:
                    new_events = pair_created_event.get_new_entries()
                    for event in new_events:
                        self.process_event(event, dex_name)
                    time.sleep(5)  # Adjust the sleep duration if necessary
                except Exception as poll_error:
                    logging.error(f"Error while fetching new events from {dex_name}: {poll_error}")
                    time.sleep(10)  # Retry after delay if error occurs
        except Exception as e:
            logging.error(f"Failed to set up subscription for {dex_name}: {e}")

    def process_event(self, event, dex_name):
        try:
            args = event.get('args', {})
            token0 = args.get('token0')
            token1 = args.get('token1')
            pair_address = args.get('pair')
            logging.info(
                f"[{dex_name}] New Pair Created: Token0: {token0}, Token1: {token1}, Pair Address: {pair_address}"
            )
        except Exception as e:
            logging.error(f"Failed to process event from {dex_name}: {e}")

if __name__ == "__main__":
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
    monitor.monitor_new_tokens()  # Call the method directly
