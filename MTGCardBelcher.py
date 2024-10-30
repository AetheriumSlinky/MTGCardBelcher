"""MTGCardBelcher v1.1.0 by /u/MustaKotka (AetheriumSlinky)"""

import time

from data.configs import oauth, target_subreddits
from functions.base_logger import logger
from functions.timer import RefreshTimer
from functions.reddit_login import login_sequence
import functions.reddit_actions as r


def main():
    """Main loop."""
    # Setup
    print("Init...")
    logger.info('New Reddit session start.')
    reddit_streams = login_sequence(oauth, target_subreddits)  # Open Reddit streams
    image_refresh = RefreshTimer(1800)  # Joke image submissions fetch timer
    image_submission_links = r.get_image_links(reddit_streams["reddit"])
    logger.info('Reddit session initiation complete.')
    print("...init complete.")

    # Main loop
    while True:
        if image_refresh.timer():  # Has 30 minutes passed?
            image_submission_links = r.get_image_links(reddit_streams["reddit"])

        for sub in target_subreddits:
            r.comment_action(reddit_streams["comments"][sub], image_submission_links)
            r.submission_action(reddit_streams["submissions"][sub], image_submission_links)

        # Reddit has in-built sleep already but just in case sleep again
        time.sleep(5)


if __name__ == "__main__":
    main()
