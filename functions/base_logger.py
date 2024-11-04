"""Main logger."""

from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

loc = Path(__file__).parent.parent.joinpath('logs')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = TimedRotatingFileHandler(filename=loc.joinpath("{:%Y_%m_%d}.txt".format(datetime.now())),
                              when='midnight', encoding='utf-8')
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)

formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M;%S')

fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)
