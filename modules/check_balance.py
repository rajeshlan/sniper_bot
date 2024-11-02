# modules/check_balance.py

from utils.wallet import get_eth_balance, get_bsc_balance, get_sol_balance

def main():
    eth_balance = get_eth_balance()
    bsc_balance = get_bsc_balance()
    sol_balance = get_sol_balance()
    
    print(f"Ethereum Balance: {eth_balance:.6f} ETH")
    print(f"Binance Smart Chain Balance: {bsc_balance:.6f} BNB")
    print(f"Solana Balance: {sol_balance:.6f} SOL")

if __name__ == "__main__":
    main()
