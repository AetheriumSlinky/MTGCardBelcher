"""Main logger."""

import logging.handlers
from pathlib import Path


def namer(name: str) -> Path:
    """
    Renames the rotating file to the format date.log.
    :param name: Path (name) of the open log file.
    :return: Path (name) of the out-rotating log file.
    """
    return loc.joinpath(name.split(".")[2] + ".log")


# Set correct location for log files
loc = Path(__file__).parent.parent.joinpath('logs')

# Get logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handle log files
file_handler = logging.handlers.TimedRotatingFileHandler(
    filename=loc.joinpath("today.log"),
    when='midnight', encoding='utf-8')
file_handler.namer = namer
file_handler.setLevel(logging.INFO)

# Handle console output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

# Formatting for log events
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M;%S')

# Set formatters and add handlers
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.addHandler(file_handler)
