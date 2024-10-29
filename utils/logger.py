# utils/logger.py
import logging
import os

def setup_logger():
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create file handler to log to a file
    file_handler = logging.FileHandler(os.path.join(log_dir, 'sniper_bot.log'))
    file_handler.setLevel(logging.INFO)

    # Create console handler to log to terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create formatter and set it for both handlers
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Logger is set up.")

# You can call this function in your main script to set up logging.
