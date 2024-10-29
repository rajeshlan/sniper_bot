import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
    env_vars = {
        "INFURA_PROJECT_ID": os.getenv("INFURA_PROJECT_ID"),
        "PRIVATE_KEY": os.getenv("PRIVATE_KEY"),
        "WALLET_ADDRESS": os.getenv("WALLET_ADDRESS"),
        "BSC_NODE_URL": os.getenv("BSC_NODE_URL"),
        "MAX_INVESTMENT_AMOUNT": os.getenv("MAX_INVESTMENT_AMOUNT"),
        "STOP_LOSS_PERCENTAGE": os.getenv("STOP_LOSS_PERCENTAGE"),
        "MAX_TOKENS": os.getenv("MAX_TOKENS"),
        "ETHERSCAN_API_KEY": os.getenv("ETHERSCAN_API_KEY"),
        "BSCSCAN_API_KEY": os.getenv("BSCSCAN_API_KEY"),
        "INFURA_URL": os.getenv("INFURA_URL")
    }
    
    # Check each environment variable and print its status
    for key, value in env_vars.items():
        if value:
            if key == "PRIVATE_KEY":
                # Mask the private key for display
                masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:]
                print(f"{key}: {masked_value}")
            else:
                print(f"{key}: {value}")
        else:
            print(f"{key} not found. Please check your .env file.")

# Execute the functions to verify the output
get_wallet_details()
check_env_variables()
