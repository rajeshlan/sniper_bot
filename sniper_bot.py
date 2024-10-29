# sniper_bot.py
import logging
from utils.logger import setup_logger  # Assuming logger.py will handle logging setup
from utils.snipe import main  # Assuming snipe.py will have the main sniping logic

def main():
    setup_logger()  # Set up logging configuration
    logging.info("Starting sniper bot...")
    main()  # Call the main function from snipe.py

if __name__ == "__main__":
    main()
