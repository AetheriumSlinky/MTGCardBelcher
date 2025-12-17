"""Main logger."""

import logging.handlers
from pathlib import Path
from src.configs import GeneralSettings


# Set a custom logging level
CONFIRMATION = 21

def logForLevel(self, message, *args, **kwargs):
    if self.isEnabledFor(CONFIRMATION):
        self._log(CONFIRMATION, message, args, **kwargs)

def logToRoot(message, *args, **kwargs):
    logging.log(CONFIRMATION, message, *args, **kwargs)


def file_namer(name: str) -> Path:
    """
    Renames the rotating file to the format date.log.
    :param name: Path (name) of the open log file.
    :return: Path (name) of the out-rotating log file.
    """
    return loc.joinpath(name.split(".")[2] + ".log")


# Create the CONFIRMATION logging level
logging.addLevelName(CONFIRMATION, "CONFIRMATION")
logging.CONFIRMATION = CONFIRMATION
logging.getLoggerClass().confirmation = logForLevel
logging.confirmation = logToRoot

# Set correct location for log files
loc = GeneralSettings.PROJECT_ROOT_PATH.joinpath('logs')

# Get logger
logger = logging.getLogger(__name__)

# Set available minimum logger level
logger.setLevel(logging.INFO)

# Handle log file names
file_handler = logging.handlers.TimedRotatingFileHandler(
    filename=loc.joinpath("today.log"),
    when='midnight', encoding='utf-8')
file_handler.namer = file_namer

# Set log file event level
file_handler.setLevel(GeneralSettings.LOGS_LEVEL)

# Handle console output
console_handler = logging.StreamHandler()
console_handler.setLevel(GeneralSettings.CONSOLE_MESSAGE_LEVEL)

# Formatting for log events
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M;%S')

# Set formatters and add handlers
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.addHandler(file_handler)
