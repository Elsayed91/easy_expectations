import logging
import os

# Define the log format
log_format = "%(asctime)s [%(levelname)s] %(message)s"

# Create a StreamHandler to display messages to the console
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter(log_format))
stream_handler.setLevel(
    logging.WARNING
)  # Set this handler to capture WARNING level and above

# Get the root logger and set its level to INFO
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Remove existing handlers from the root logger (to start with a clean slate)
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Add the StreamHandler to the root logger
root_logger.addHandler(stream_handler)

# If EE_LOGGING environment variable exists and is set to "True", enable file logging
if os.environ.get("EE_LOGGING") == "True":
    # Create a FileHandler to log messages to a file
    log_file_path = "easy_expectations.log"
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(logging.Formatter(log_format))
    file_handler.setLevel(
        logging.INFO
    )  # Set this handler to capture INFO level and above

    # Add the FileHandler to the root logger
    root_logger.addHandler(file_handler)

# Suppress logging from 'great_expectations'
logging.getLogger("great_expectations").setLevel(logging.WARNING)

logger = root_logger
