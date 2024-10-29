import logging
import json
import requests
from web3 import Web3
from web3.middleware import geth_poa_middleware

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_abi_from_blockchain_scan(contract_address, api_key, network='bsc'):
    """Load ABI from BscScan or Etherscan using their API."""
    if network == 'bsc':
        url = f"https://api.bscscan.com/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}"
    elif network == 'eth':
        url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}"
    else:
        raise ValueError("Invalid network specified. Use 'bsc' for BscScan or 'eth' for Etherscan.")
    
    logging.info(f"Loading ABI from {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request fails
        data = response.json()
        
        if data['status'] == "1":  # Check if the response status is success
            abi = json.loads(data['result'])
            # Log the first few lines of the ABI to confirm it's loaded correctly
            logging.info(f"Successfully loaded ABI for contract {contract_address}. ABI: {abi[:2]}...")  # Show only first two items for brevity
            return abi
        else:
            logging.error(f"Failed to retrieve ABI: {data['result']}")
            raise Exception(f"Failed to retrieve ABI: {data['result']}")
        
    except requests.RequestException as e:
        logging.error(f"Failed to load ABI from {url}: {str(e)}")
        raise

def analyze_token(token_address, provider, contract_address, api_key, network='bsc'):
    logging.info(f"Starting analysis for token: {token_address}")
    
    try:
        # Load the ABI from the BscScan or Etherscan API
        abi = load_abi_from_blockchain_scan(contract_address, api_key, network)
        
        # Create token contract instance
        token_contract = provider.eth.contract(address=token_address, abi=abi)
        logging.info(f"Token contract created for address: {token_address}")

        # Replace '...' with the actual function to get the liquidity
        liquidity = token_contract.functions.balanceOf(token_address).call()  # Assuming you're checking the token's own balance
        logging.info(f"Liquidity for token {token_address}: {liquidity} wei")
        
        # Check if liquidity is above the threshold
        if liquidity > 1 * 10**18:  # Example: Check if the liquidity is over 1 ETH
            logging.info(f"Promising token found: {token_address} with liquidity: {liquidity} wei")
            return True
        
        logging.warning(f"Token {token_address} does not meet liquidity requirements: {liquidity} wei")
    except Exception as e:
        logging.error(f"Error analyzing token {token_address}: {str(e)}")

    return False

def initialize_provider(network='bsc'):
    """Initialize Web3 provider for BSC or ETH based on network choice."""
    if network == 'bsc':
        provider_url = "https://bsc-dataseed.binance.org/"  # BSC provider
    elif network == 'eth':
        provider_url = "https://mainnet.infura.io/v3/e3664c8b17c54e7190eea5218400539d"  # Replace with your Infura project ID for ETH
    else:
        raise ValueError("Invalid network specified. Use 'bsc' for Binance Smart Chain or 'eth' for Ethereum.")
    
    provider = Web3(Web3.HTTPProvider(provider_url))
    
    # Add PoA middleware for BSC or other PoA chains
    provider.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    # Check if connected successfully
    if provider.is_connected():
        logging.info(f"Successfully connected to {network.upper()} network.")
    else:
        logging.error(f"Failed to connect to {network.upper()} network. Check your provider URL and network status.")
    
    return provider


# Usage Example
if __name__ == "__main__":
    token_address = "0x17B7d7618bA568E63F6875495c4e3360dE6DEEF8"
    contract_address = "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"
    api_key = "94QFVKT1T9PGFI6RN6CBC6BNUBUVY43ISS"
    network = "bsc"  # Use 'bsc' for Binance Smart Chain, 'eth' for Ethereum

    # Initialize provider based on the network
    provider = initialize_provider(network)
    
    # Analyze the token
    analyze_token(token_address, provider, contract_address, api_key, network)
