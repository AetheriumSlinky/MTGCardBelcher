"""Main logger config."""

from datetime import datetime
import logging
from pathlib import Path

root = Path(__file__).parent.parent

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename=f"{root}\\logs\\{datetime.today().strftime('%Y_%m_%d')}.txt",
    encoding='utf-8', level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M;%S'
    )
