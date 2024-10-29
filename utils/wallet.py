import os
import sys
import time
import logging
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.rpc.types import TxOpts
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.system_program import transfer as transfer_instruction
from web3 import Web3
from dotenv import load_dotenv
from config import WALLET_ADDRESS, PRIVATE_KEY
from utils.security import get_wallet_details
from utils.blockchain import eth_provider, bsc_provider

# Load environment variables
load_dotenv()

# Initialize Solana RPC Client
SOLANA_RPC_URL = os.getenv('SOLANA_RPC_URL')
solana_client = Client(SOLANA_RPC_URL)

# Initialize Ethereum and BSC providers
infura_url = os.getenv('INFURA_URL')
if infura_url is None:
    logging.error("Infura URL not found. Please check your .env file.")
    sys.exit(1)

eth_provider = Web3(Web3.HTTPProvider(infura_url))
bsc_provider = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))

# Wallet Initialization
def initialize_wallet():
    """Connect to the wallet using the provided address and private key."""
    try:
        wallet_address = Web3.to_checksum_address(WALLET_ADDRESS)
        private_key = PRIVATE_KEY
        return wallet_address, private_key
    except Exception as e:
        logging.error(f"Failed to initialize wallet: {e}")
        return None, None

# Balance Fetching Functions
def get_balance(provider, wallet_address):
    """Fetch balance of the wallet on the specified blockchain provider."""
    try:
        balance = provider.eth.get_balance(wallet_address)
        return Web3.from_wei(balance, 'ether')
    except Exception as e:
        logging.error(f"Failed to get balance: {e}")
        return None

def get_eth_balance():
    """Fetch Ethereum balance of the configured wallet."""
    return get_balance(eth_provider, WALLET_ADDRESS)

def get_bsc_balance():
    """Fetch Binance Smart Chain (BNB) balance of the configured wallet."""
    return get_balance(bsc_provider, WALLET_ADDRESS)

# Transaction Functions
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

# Token Purchase Functions
def buy_token(provider, router_address, token_address, amount_in_ether):
    """
    Buy a token on the specified provider (ETH or BSC).
    Args:
        provider (Web3): Blockchain provider (e.g., eth_provider or bsc_provider)
        router_address (str): Address of the swap router
        token_address (str): Address of the token to purchase
        amount_in_ether (float): Amount to spend
    Returns:
        str: Transaction hash, if successful
    """
    try:
        wallet_address, private_key = get_wallet_details()
        router_contract = provider.eth.contract(address=router_address, abi=[...])  # Replace with actual ABI

        txn = router_contract.functions.swapExactETHForTokens(
            0,  # Minimum tokens to receive
            [provider.eth.defaultAccount, token_address],  # Path from ETH to token
            wallet_address,
            int(time.time()) + 60  # Deadline (60 seconds)
        ).buildTransaction({
            'from': wallet_address,
            'value': Web3.to_wei(amount_in_ether, 'ether'),
            'gas': 200000,
            'gasPrice': provider.eth.gas_price,
            'nonce': provider.eth.get_transaction_count(wallet_address)
        })

        signed_txn = provider.eth.account.sign_transaction(txn, private_key)
        tx_hash = provider.eth.send_raw_transaction(signed_txn.rawTransaction)

        logging.info(f"Token purchase transaction sent! TX Hash: {Web3.to_hex(tx_hash)}")
        return Web3.to_hex(tx_hash)
    except Exception as e:
        logging.error(f"Failed to buy token: {e}")
        return None

# Solana Token Purchase Function
def buy_token_sol(token_address, amount_in_sol):
    """Buy a token on Solana."""
    try:
        from_wallet = Keypair.from_secret_key(bytes.fromhex(PRIVATE_KEY))
        transaction = Transaction()
        transaction.add(transfer_instruction(
            from_pubkey=from_wallet.public_key,
            to_pubkey=PublicKey(token_address),
            lamports=int(amount_in_sol * 1_000_000_000)
        ))
        response = solana_client.send_transaction(transaction, from_wallet, opts=TxOpts(skip_preflight=True))
        return response
    except Exception as e:
        logging.error(f"Failed to buy token on Solana: {e}")
        return None

# Entry Point
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Check provider connections
    if eth_provider.is_connected():
        logging.info("Connected to Ethereum!")
    else:
        logging.error("Failed to connect to Ethereum.")

    if bsc_provider.is_connected():
        logging.info("Connected to Binance Smart Chain!")
    else:
        logging.error("Failed to connect to Binance Smart Chain.")

    # Fetch and log wallet balances
    eth_balance = get_eth_balance()
    bnb_balance = get_bsc_balance()

    if eth_balance is not None:
        logging.info(f"Ethereum balance: {eth_balance} ETH")
    else:
        logging.error("Could not fetch Ethereum balance.")

    if bnb_balance is not None:
        logging.info(f"Binance Smart Chain balance: {bnb_balance} BNB")
    else:
        logging.error("Could not fetch Binance Smart Chain balance.")
