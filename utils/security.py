# utils/security.py
import os
import logging
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def validate_private_key(private_key):
    """Validate the format of a private key."""
    if len(private_key) == 64 and all(c in '0123456789abcdef' for c in private_key):
        logging.info("Private key is valid.")
        return True
    logging.error("Invalid private key provided.")
    return False

def check_address_format(address):
    """Check if the provided address is in a valid format."""
    if address.startswith("0x") and len(address) == 42:
        logging.info("Address format is valid.")
        return True
    logging.error("Invalid address format provided.")
    return False 

def get_wallet_details():
    """Retrieve and display wallet address and private key details."""
    wallet_address = os.getenv("WALLET_ADDRESS")
    private_key = os.getenv("PRIVATE_KEY")
    
    if wallet_address:
        print(f"Wallet Address: {wallet_address}")
    else:
        print("Wallet Address not found.")
    
    if private_key:
        # Mask the private key for security reasons
        masked_key = private_key[:4] + "*" * (len(private_key) - 8) + private_key[-4:]
        print(f"Private Key: {masked_key}")
    else:
        print("Private Key not found.")
    
    return wallet_address, private_key

def check_env_variables():
    """Check the presence of all required environment variables."""
    required_env_vars = [
        "INFURA_PROJECT_ID",
        "PRIVATE_KEY",
        "WALLET_ADDRESS",
        "BSC_NODE_URL",
        "MAX_INVESTMENT_AMOUNT",
        "STOP_LOSS_PERCENTAGE",
        "MAX_TOKENS",
        "ETHERSCAN_API_KEY",
        "BSCSCAN_API_KEY",
        "INFURA_URL"
    ]
    
    for var in required_env_vars:
        value = os.getenv(var)
        if value:
            if var == "PRIVATE_KEY":
                # Mask the private key for display
                masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:]
                print(f"{var}: {masked_value}")
            else:
                print(f"{var}: {value}")
        else:
            print(f"{var} not found. Please check your .env file.")

# Execute the functions to verify the output
if __name__ == "__main__":
    get_wallet_details()
    check_env_variables()
