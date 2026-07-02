"""MTGCardBelcher v1.3.0 by /u/MustaKotka (AetheriumSlinky)"""
import sys
import time

from src.func.base_logger import logger
from src.func.reddit_connection import RedditData
from src.func.timer import RefreshTimer
from src.data.exceptions import OperationConnectionException, FatalConnectionError
from src.configs import BotInfo, Subreddits
import src.func.reddit_actions as r


def main():
    """Main."""
    # Setup
    logger.info('New Reddit session start.')
    image_refresh = RefreshTimer(1800, refresh_on_start=True)  # Joke image submissions fetch timer
    connection = RedditData(BotInfo.REDDIT_OAUTH, Subreddits.CALL_SUBREDDITS)
    image_submission_links = []

    # Loop
    while True:
        try:
            if image_refresh.is_it_time():  # Has 30 minutes passed?
                image_submission_links = r.sub_actions(connection, Subreddits.SUBMISSION_SUBREDDITS)

            for sub in Subreddits.CALL_SUBREDDITS:
                r.comment_action(connection, sub, image_submission_links)
                r.submission_action(connection, sub, image_submission_links)

        except OperationConnectionException:
            connection = RedditData(BotInfo.REDDIT_OAUTH, Subreddits.CALL_SUBREDDITS)
            logger.info("OAuth info resent.")

        except FatalConnectionError as e:
            logger.critical(e)
            sys.exit()

        # Reddit has in-built sleep already but just in case sleep again
        time.sleep(1)


if __name__ == "__main__":
    main()
