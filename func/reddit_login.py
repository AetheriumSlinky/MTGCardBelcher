"""Contains functions that handle logging in to Reddit."""

import time

import praw
import praw.exceptions
import prawcore

from func.base_logger import logger


def login_error_handler(func):
    """
    Handles the errors during login. Does not attempt login.
    """
    def wrapper(*args, **kwargs):
        """Wrapper."""
        while True:
            try:
                return func(*args, **kwargs)
            except prawcore.ServerError as server_err:
                logger.warning("Server error, retry in 5 minutes. Error code: " + str(server_err))
                time.sleep(300)
            except prawcore.RequestException as request_exc:
                logger.warning("Incomplete HTTP request, retry in 10 seconds. Error code: " + str(request_exc))
                time.sleep(10)
            except prawcore.ResponseException as response_exc:
                logger.warning("HTTP request response error, retry in 30 seconds. Error code: " + str(response_exc))
                time.sleep(30)
            except praw.exceptions.RedditAPIException as api_e:
                logger.warning("APIException. Error code: " + str(api_e))
                time.sleep(30)
    return wrapper


def reddit_login(login_info) -> praw.Reddit:
    """
    Logs in to Reddit.
    :param login_info: A text file containing the OAuth info.
    :return: Reddit.
    """
    with open(login_info, "r") as oauth_file:
        info = oauth_file.read().splitlines()

    reddit = praw.Reddit(
        user_agent=info[0],
        username=info[1],
        password=info[2],
        client_id=info[3],
        client_secret=info[4],
    )
    return reddit


@login_error_handler
def login_sequence(login_info, targets: list) -> dict:
    """
    Gathers the different comment and submissions streams together.
    :param login_info: A text file containing the OAuth info.
    :param targets: A list of target subreddits.
    :return: A dict of Reddit, comments and submissions.
    """
    reddit = reddit_login(login_info)
    comments = comment_streams(reddit, targets)
    submissions = submission_streams(reddit, targets)
    logger.info('Reddit login successful.')
    return {"reddit": reddit, "comments": comments, "submissions": submissions}


def comment_streams(reddit: praw.Reddit, targets: list) -> dict:
    """
    Opens the comment streams on MTCJ and MTGCardBelcher_dev.
    :param reddit: Reddit.
    :param targets: A list of target subreddits.
    :return: Dict of target subreddits streams.
    """
    streams = {}
    for target in targets:
        streams[target] = reddit.subreddit(target).stream.comments(skip_existing=True, pause_after=2)
    return streams


def submission_streams(reddit: praw.Reddit, targets: list) -> dict:
    """
    Opens the submission streams on MTCJ and MTGCardBelcher_dev.
    :param reddit: Reddit.
    :param targets: A list of target subreddits.
    :return: Dict of target subreddits streams.
    """
    streams = {}
    for target in targets:
        streams[target] = reddit.subreddit(target).stream.submissions(skip_existing=True, pause_after=2)
    return streams
