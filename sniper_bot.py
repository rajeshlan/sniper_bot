# sniper_bot.py

import logging
from utils.logger import setup_logger  # Sets up the logging configuration
from utils.snipe import execute_sniping  # Main sniping functionality

def start_sniping():
    """
    Sets up the logging and initiates the sniping process.
    """
    setup_logger()
    logging.info("Starting sniper bot...")
    execute_sniping()

if __name__ == "__main__":
    start_sniping()
