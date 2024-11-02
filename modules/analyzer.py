import logging
import json
import requests
from web3 import Web3
from web3.middleware import geth_poa_middleware
from solana.rpc.api import Client

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_abi_from_blockchain_scan(contract_address, api_key, network='bsc'):
    """Load ABI from BscScan or Etherscan using their API."""
    base_urls = {
        'bsc': "https://api.bscscan.com/api",
        'eth': "https://api.etherscan.io/api"
    }
    
    if network not in base_urls:
        raise ValueError("Invalid network specified. Use 'bsc' for BscScan or 'eth' for Etherscan.")

    url = f"{base_urls[network]}?module=contract&action=getabi&address={contract_address}&apikey={api_key}"
    logging.info(f"Loading ABI from {url}...")

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request fails
        data = response.json()

        if data['status'] == "1":  # Check if the response status is success
            abi = json.loads(data['result'])
            logging.info(f"Successfully loaded ABI for contract {contract_address}. ABI: {abi[:2]}...")
            return abi
        else:
            logging.error(f"Failed to retrieve ABI: {data['result']}")
            raise Exception(f"Failed to retrieve ABI: {data['result']}")

    except requests.RequestException as e:
        logging.error(f"Failed to load ABI from {url}: {str(e)}")
        raise

def analyze_token(token_address, provider, contract_address, api_key, network):
    """Analyze a token by checking its liquidity based on the network."""
    logging.info(f"Starting analysis for {network.upper()} token: {token_address}")

    try:
        # Load the ABI
        abi = load_abi_from_blockchain_scan(contract_address, api_key, network)
        
        # Create token contract instance
        token_contract = provider.eth.contract(address=token_address, abi=abi)
        liquidity = token_contract.functions.balanceOf(token_address).call()
        logging.info(f"Liquidity for {network.upper()} token {token_address}: {liquidity} wei")
        
        if liquidity > 1 * 10**18:  # Check for liquidity
            logging.info(f"Promising {network.upper()} token found: {token_address} with liquidity: {liquidity} wei")
            return True
        
        logging.warning(f"{network.upper()} Token {token_address} does not meet liquidity requirements: {liquidity} wei")
    except Exception as e:
        logging.error(f"Error analyzing {network.upper()} token {token_address}: {str(e)}")

    return False

def analyze_solana_token(token_address, provider):
    """Analyze a token on the Solana network."""
    logging.info(f"Starting analysis for Solana token: {token_address}")

    try:
        # Fetch the token balance
        balance_info = provider.get_token_account_balance(token_address)
        balance = balance_info['result']['value']['amount']  # Adjust based on actual response structure
        logging.info(f"Liquidity for Solana token {token_address}: {balance} lamports")

        if int(balance) > 1_000_000_000:  # 1 SOL in lamports
            logging.info(f"Promising Solana token found: {token_address} with liquidity: {balance} lamports")
            return True

        logging.warning(f"Solana Token {token_address} does not meet liquidity requirements: {balance} lamports")
    except Exception as e:
        logging.error(f"Error analyzing Solana token {token_address}: {str(e)}")

    return False

def initialize_bsc_provider():
    """Initialize Web3 provider for Binance Smart Chain."""
    provider_url = "https://bsc-dataseed.binance.org/"
    provider = Web3(Web3.HTTPProvider(provider_url))
    provider.middleware_onion.inject(geth_poa_middleware, layer=0)

    if provider.is_connected():
        logging.info("Successfully connected to BSC network.")
    else:
        logging.error("Failed to connect to BSC network.")
    
    return provider

def initialize_eth_provider():
    """Initialize Web3 provider for Ethereum."""
    provider_url = "https://mainnet.infura.io/v3/e3664c8b17c54e7190eea5218400539d"  # Replace with your Infura project ID
    provider = Web3(Web3.HTTPProvider(provider_url))
    provider.middleware_onion.inject(geth_poa_middleware, layer=0)

    if provider.is_connected():
        logging.info("Successfully connected to Ethereum network.")
    else:
        logging.error("Failed to connect to Ethereum network.")
    
    return provider

def initialize_solana_provider():
    """Initialize Solana provider."""
    provider = Client("https://api.mainnet-beta.solana.com")
    
    if provider.is_connected():
        logging.info("Successfully connected to Solana network.")
    else:
        logging.error("Failed to connect to Solana network.")
    
    return provider

# Usage Example
if __name__ == "__main__":
    # Define token addresses and contract address for analysis
    bsc_token_address = "0xb3Ed0A426155B79B898849803E3B36552f7ED507" #pendle address
    eth_token_address = "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE"  # SHIBAINU Replace with a valid ETH token address
    solana_token_address = "skynetDj29GH6o6bAqoixCpDuYtWqi1rm8ZNx1hB3vq"  # Replace with a valid Solana token address
    contract_address = "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"  # Example contract address
    api_key = "94QFVKT1T9PGFI6RN6CBC6BNUBUVY43ISS"

    # Initialize providers
    bsc_provider = initialize_bsc_provider()
    eth_provider = initialize_eth_provider()
    solana_provider = initialize_solana_provider()
    
    # Analyze tokens on BSC, ETH, and Solana
    analyze_token(bsc_token_address, bsc_provider, contract_address, api_key, 'bsc')
    analyze_token(eth_token_address, eth_provider, contract_address, api_key, 'eth')
    analyze_solana_token(solana_token_address, solana_provider)
