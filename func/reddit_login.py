"""Contains functions that handle logging in to Reddit."""

import time

import praw
import praw.exceptions
import prawcore

from func.base_logger import logger
from data.exceptions import LoginException, FatalLoginError


class RedditData:
    """
    Combined Reddit and SubredditData object.
    """
    def __init__(self, login_info, targets: list):
        self.reddit = reddit_login(login_info)
        self.subreddits = {}
        for subreddit in targets:
            self.subreddits[subreddit] = SubredditData(subreddit, self.reddit)


class SubredditData:
    """
    Subreddit streams object. Target, submissions, comments.
    """
    def __init__(self, target: str, reddit: praw.Reddit):
        self.target = target
        self.submissions = reddit.subreddit(target).stream.submissions(skip_existing=True, pause_after=1)
        self.comments = reddit.subreddit(target).stream.comments(skip_existing=True, pause_after=1)


def login_error_handler(func):
    """
    Handles the errors during login. Does not attempt login.
    """
    def wrapper(*args, **kwargs):
        """Wrapper."""
        try:
            return func(*args, **kwargs)
        except prawcore.ServerError as server_err:
            logger.warning("Server error, retry in 5 minutes. Error code: " + str(server_err))
            time.sleep(300)
            raise LoginException
        except prawcore.RequestException as request_exc:
            logger.warning("Incomplete HTTP request, retry in 10 seconds. Error code: " + str(request_exc))
            time.sleep(10)
            raise LoginException
        except prawcore.ResponseException as response_exc:
            logger.warning("HTTP request response error, retry in 30 seconds. Error code: " + str(response_exc))
            time.sleep(30)
            raise LoginException
        except praw.exceptions.RedditAPIException as api_e:
            logger.warning("APIException. Error code: " + str(api_e))
            time.sleep(30)
            raise LoginException
    return wrapper


@login_error_handler
def reddit_login(login_info) -> praw.Reddit:
    """
    Logs in to Reddit.
    :param login_info: A text file containing the OAuth info.
    :return: The Reddit instance.
    """
    with open(login_info, "r") as oauth_file:
        info = oauth_file.read().splitlines()

    reddit = praw.Reddit(
        user_agent=info[0],
        username=info[1],
        password=info[2],
        client_id=info[3],
        client_secret=info[4])

    logger.info("Reddit login successful.")
    return reddit


def try_login_loop(login_info, targets: list) -> RedditData:
    """
    Tries to log in on loop perpetually. Raises FatalLoginError if there are too many attempts to log in.
    :param login_info: A text file containing the OAuth info.
    :param targets: A list of target subreddits.
    :return: A RedditData object containing the Reddit instance and subreddit streams.
    """
    attempts = 0
    while attempts < 20:
        try:
            return RedditData(login_info, targets)

        except LoginException:
            time.sleep(2 ** attempts)
            logger.warning(f"Exception while retrieving Reddit data during login."
                           f"Retrying after {2 ** attempts} seconds.")
            attempts += 1

    logger.critical(f"There were {attempts} failed login attempts. Stopped trying to log in. Goodbye.")
    raise FatalLoginError("Too many failed login attemps. Exiting program. Goodbye.")
