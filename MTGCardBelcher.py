"""MTGCardBelcher v1.1.0 by /u/MustaKotka (AetheriumSlinky)"""
import sys
import time

from data.configs import oauth, target_subreddits, submissions_subreddits
from func.base_logger import logger
from func.timer import RefreshTimer
from func.reddit_login import try_login_loop
from data.exceptions import MainOperationException, FatalLoginError
import func.reddit_actions as r


def main():
    """Main."""
    # Setup
    print("Init...")
    logger.info('New Reddit session start.')
    image_refresh = RefreshTimer(1800)  # Joke image submissions fetch timer

    # Login
    try:
        reddit_streams = try_login_loop(oauth, target_subreddits)  # Open Reddit streams
        image_submission_links = r.get_image_links(reddit_streams.reddit, submissions_subreddits) # Fetch the images
    except FatalLoginError as e:
        print(e)
        sys.exit()

    logger.info('Reddit session successfully started.')
    print("...init complete.")

    # Main loop
    while True:
        try:
            if image_refresh.recurring_timer():  # Has 30 minutes passed?
                image_submission_links = r.get_image_links(reddit_streams.reddit, submissions_subreddits)

            for sub in target_subreddits:
                r.comment_action(reddit_streams.subreddits[sub].comments, image_submission_links)
                r.submission_action(reddit_streams.subreddits[sub].submissions, image_submission_links)

        except MainOperationException:
            reddit_streams = try_login_loop(oauth, target_subreddits)

        except FatalLoginError as e:
            print(e)
            sys.exit()

        # Reddit has in-built sleep already but just in case sleep again
        time.sleep(5)


if __name__ == "__main__":
    main()
