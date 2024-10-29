#python -m modules.check_balance (run with this) 

from utils.wallet import get_eth_balance, get_bsc_balance

def main():
    eth_balance = get_eth_balance()
    bsc_balance = get_bsc_balance()
    print(f"Ethereum Balance: {eth_balance} ETH")
    print(f"Binance Smart Chain Balance: {bsc_balance} BNB")

if __name__ == "__main__":
    main()