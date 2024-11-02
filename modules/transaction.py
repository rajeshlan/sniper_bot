# modules/transaction.py
import logging
from utils.blockchain import Blockchain
from utils.wallet import buy_token, sell_token # Assuming sell_token function exists
from config import BSC_NODE_URL, SOLANA_RPC_URL

def buy(token, amount, blockchain):
    logging.info(f"Initiating buy for token: {token} with amount: {amount} on {blockchain}")
    try:
        if blockchain == 'ETH':
            blockchain_instance = Blockchain(BSC_NODE_URL, 'ETH')
        elif blockchain == 'BSC':
            blockchain_instance = Blockchain(BSC_NODE_URL, 'BSC')
        elif blockchain == 'SOL':
            blockchain_instance = Blockchain(SOLANA_RPC_URL, 'SOL')
        
        # Call buy_token from wallet.py
        buy_token(token, amount, blockchain_instance)
        logging.info(f"Successfully bought {amount} of {token} on {blockchain}.")
    except Exception as e:
        logging.error(f"Error buying token: {str(e)}")

def sell(token, amount, blockchain):
    logging.info(f"Initiating sell for token: {token} with amount: {amount} on {blockchain}")
    try:
        if blockchain == 'ETH':
            blockchain_instance = Blockchain(BSC_NODE_URL, 'ETH')
        elif blockchain == 'BSC':
            blockchain_instance = Blockchain(BSC_NODE_URL, 'BSC')
        elif blockchain == 'SOL':
            blockchain_instance = Blockchain(SOLANA_RPC_URL, 'SOL')

        # Call sell_token from wallet.py
        sell_token(token, amount, blockchain_instance)
        logging.info(f"Successfully sold {amount} of {token} on {blockchain}.")
    except Exception as e:
        logging.error(f"Error selling token: {str(e)}")
