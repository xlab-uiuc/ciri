import logging
from pathlib import Path

# Set up logger with a descriptive name
logger = logging.getLogger("Ciri")
logger.setLevel(logging.INFO)

# Create console handler for terminal output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create file handler for debug logs
log_path = Path("ciri_debug.log")
file_handler = logging.FileHandler(log_path)
file_handler.setLevel(logging.DEBUG)

# Create formatter with detailed output format
formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Add formatter to handlers
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add both handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Prevent duplicate log messages
logger.propagate = False
