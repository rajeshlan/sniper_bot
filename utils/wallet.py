# utils/wallet.py

import logging
import os
import sys
import requests
from solana.rpc.api import Client
from web3 import Web3
from dotenv import load_dotenv
from config import (
    WALLET_ADDRESS,
    PRIVATE_KEY,
    ETHERSCAN_API_KEY,
    BSCSCAN_API_KEY,
    SOLANA_RPC_URL,
)
from utils.security import get_wallet_details
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import get_associated_token_address, create_associated_token_account, transfer as spl_transfer
from spl.token import Token
from solana.rpc.types import TxOpts

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize Blockchain Clients
solana_client = Client(SOLANA_RPC_URL)

infura_url = os.getenv('INFURA_URL')
if infura_url is None:
    logging.error("Infura URL not found. Please check your .env file.")
    sys.exit(1)

eth_provider = Web3(Web3.HTTPProvider(infura_url))
bsc_provider = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))

def initialize_wallet():
    """Connect to the wallet using the provided address and private key."""
    try:
        wallet_address = Web3.to_checksum_address(WALLET_ADDRESS.strip())
        private_key = PRIVATE_KEY.strip()
        return wallet_address, private_key
    except Exception as e:
        logging.error(f"Failed to initialize wallet: {e}")
        return None, None

def fetch_balance(url):
    """Fetch balance from a given API URL."""
    response = requests.get(url)
    data = response.json()
    
    if data["status"] == "1":
        return int(data["result"]) / 10**18  # Convert from Wei to respective cryptocurrency
    else:
        raise ValueError("Error fetching balance: " + data["message"])

def get_eth_balance():
    """Fetch Ethereum balance of the configured wallet."""
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={WALLET_ADDRESS}&tag=latest&apikey={ETHERSCAN_API_KEY}"
    return fetch_balance(url)

def get_bsc_balance():
    """Fetch Binance Smart Chain (BNB) balance of the configured wallet."""
    url = f"https://api.bscscan.com/api?module=account&action=balance&address={WALLET_ADDRESS}&tag=latest&apikey={BSCSCAN_API_KEY}"
    return fetch_balance(url)

def get_sol_balance():
    """Fetch Solana balance of the configured wallet."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [WALLET_ADDRESS],
    }
    response = requests.post(SOLANA_RPC_URL, json=payload, headers={"Content-Type": "application/json"})
    data = response.json()
    
    if "result" in data:
        return data["result"]["value"] / 10**9  # Convert Lamports to SOL
    else:
        raise ValueError("Error fetching Solana balance: " + str(data))

def get_or_create_associated_token_account(wallet_address, token_address):
    """Get or create an associated token account for a specific token."""
    try:
        token = Token(solana_client, token_address, TOKEN_PROGRAM_ID, wallet_address)
        ata = get_associated_token_address(wallet_address, token_address)

        # Check if the associated token account exists
        account_info = solana_client.get_account_info(ata)
        if account_info['result']['value'] is None:
            logging.info(f"Creating associated token account for {token_address}...")
            transaction = Transaction().add(create_associated_token_account(wallet_address, token_address))
            solana_client.send_transaction(transaction, wallet_address)
            logging.info(f"Created associated token account: {ata}")
        else:
            logging.info(f"Associated token account already exists: {ata}")

        return ata
    except Exception as e:
        logging.error(f"Failed to get or create associated token account: {e}")
        return None

def trade_token(action, token, amount, blockchain_instance):
    """Buy or sell a token on the specified blockchain."""
    try:
        if blockchain_instance.network in ['ETH', 'BSC']:
            token_contract = blockchain_instance.w3.eth.contract(address=token, abi=TOKEN_ABI)  # Replace <TOKEN_ABI> with actual ABI
            value_in_ether = amount * token_contract.functions.price().call()  # Adapt to your token's contract
            tx_hash = send_transaction(blockchain_instance.provider, token, value_in_ether)
            return tx_hash

        elif blockchain_instance.network == 'SOL':
            logging.info(f"Trading {action} {amount} of token {token} on Solana...")

            # Get or create the associated token account for the token
            ata = get_or_create_associated_token_account(WALLET_ADDRESS, token)
            if ata is None:
                return None

            # Create the instruction for the transfer
            if action == 'buy':
                # Placeholder: Implement buying logic here (you might need a swap instruction)
                logging.info(f"Buying {amount} of token {token}...")  # Replace with actual swap logic
                # Example: Add swap logic here using Serum DEX or similar

            elif action == 'sell':
                logging.info(f"Selling {amount} of token {token}...")
                transaction = Transaction().add(
                    spl_transfer(
                        amount=amount,
                        source=ata,
                        dest=WALLET_ADDRESS,  # Or destination address for selling
                        owner=WALLET_ADDRESS,
                        token_program=TOKEN_PROGRAM_ID,
                    )
                )

                # Send the transaction
                tx_hash = solana_client.send_transaction(transaction, WALLET_ADDRESS, opts=TxOpts(skip_preflight=True))
                logging.info(f"Transaction sent! TX Hash: {tx_hash['result']}")
                return tx_hash['result']

    except Exception as e:
        logging.error(f"Failed to {action} token {token}: {str(e)}")
        raise

def send_transaction(provider, to_address, value_in_ether, gas_limit=21000, gas_price_wei=None):
    """
    Send a transaction on the specified provider (ETH or BSC).
    
    Args:
        provider (Web3): Blockchain provider (e.g., eth_provider or bsc_provider)
        to_address (str): Recipient address
        value_in_ether (float): Amount to send
        gas_limit (int): Gas limit for the transaction
        gas_price_wei (int, optional): Custom gas price in wei; defaults to current network gas price

    Returns:
        str: Transaction hash, if successful
    """
    try:
        wallet_address, private_key = get_wallet_details()
        tx = {
            'from': wallet_address,
            'to': to_address,
            'value': Web3.to_wei(value_in_ether, 'ether'),
            'gas': gas_limit,
            'gasPrice': gas_price_wei or provider.eth.gas_price,
            'nonce': provider.eth.get_transaction_count(wallet_address),
        }

        signed_tx = provider.eth.account.sign_transaction(tx, private_key)
        tx_hash = provider.eth.send_raw_transaction(signed_tx.rawTransaction)

        logging.info(f"Transaction sent! TX Hash: {Web3.to_hex(tx_hash)}")
        return Web3.to_hex(tx_hash)
    except Exception as e:
        logging.error(f"Failed to send transaction: {e}")
        return None

def log_wallet_balances():
    """Fetch and log wallet balances for ETH, BSC, and Solana."""
    try:
        eth_balance = get_eth_balance()
        logging.info(f"Ethereum balance: {eth_balance} ETH")
    except Exception as e:
        logging.error("Could not fetch Ethereum balance: " + str(e))

    try:
        bnb_balance = get_bsc_balance()
        logging.info(f"Binance Smart Chain balance: {bnb_balance} BNB")
    except Exception as e:
        logging.error("Could not fetch Binance Smart Chain balance: " + str(e))

    try:
        sol_balance = get_sol_balance()
        logging.info(f"Solana balance: {sol_balance} SOL")
    except Exception as e:
        logging.error("Could not fetch Solana balance: " + str(e))

# Entry Point
if __name__ == "__main__":
    # Check provider connections
    if eth_provider.is_connected():
        logging.info("Connected to Ethereum!")
    else:
        logging.error("Failed to connect to Ethereum.")

    if bsc_provider.is_connected():
        logging.info("Connected to Binance Smart Chain!")
    else:
        logging.error("Failed to connect to Binance Smart Chain.")

    log_wallet_balances()
