# utils/logger.py
import logging
import os

def setup_logger():
    # Directory for log files
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # Get the root logger and configure it
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Avoid adding handlers multiple times if logger is reconfigured
    if not logger.handlers:
        # File handler for logging to a file
        file_handler = logging.FileHandler(os.path.join(log_dir, 'sniper_bot.log'))
        file_handler.setLevel(logging.INFO)

        # Console handler for logging to the terminal
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter to apply to both handlers
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Adding handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    logger.info("Logger initialized.")

# Call this function in your main script to set up logging.
