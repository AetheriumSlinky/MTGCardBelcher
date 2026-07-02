"""Contains functions that handle logging in to Reddit."""

import praw
import praw.exceptions

from src.func.base_logger import logger
from src.data.collectibles import Collectibles


class SubredditData:
    """
    Subreddit streams object. Target, submissions, comments.
    """
    def __init__(self, target: str, reddit: praw.Reddit):
        self.target = target
        self.submissions = reddit.subreddit(target).stream.submissions(skip_existing=True, pause_after=1)
        self.comments = reddit.subreddit(target).stream.comments(skip_existing=True, pause_after=1)


class RedditData:
    """
    A combined Reddit, SubredditData, and collectible card objects dict -object with the active connection to Reddit.
    """
    def __init__(self, login_info, targets: list):
        self.targets = targets
        self.reddit: praw.Reddit
        self.subreddit_streams: dict[str, SubredditData]
        self.collectibles: Collectibles
        self.__login(login_info)


    def __reddit_login(self, login_info):
        """
        Logs in to Reddit.
        :param login_info: A text file containing the OAuth info.
        """
        with open(login_info, "r") as oauth_file:
            info = oauth_file.read().splitlines()

        reddit_instance = praw.Reddit(
            user_agent=info[0],
            username=info[1],
            password=info[2],
            client_id=info[3],
            client_secret=info[4])

        self.reddit = reddit_instance
        logger.confirmation("Reddit login attempt successful.")

    def __open_streams(self):
        """
        Creates a dictionary with SubredditData objects with subreddit names as keys.
        """
        self.subreddit_streams = {}
        for subreddit in self.targets:
            self.subreddit_streams[subreddit] = SubredditData(subreddit, self.reddit)
            logger.info(f"Stream connections for {subreddit} were initiated or restored.")

    def __collectibles(self):
        """
        Creates instances of the collectible card objects.
        """
        self.collectibles = Collectibles(self.reddit)

    def __login(self, login_info):
        """
        Initiates the RedditData object properly.
        :param login_info: A text file containing the OAuth info.
        :return: A RedditData object containing the Reddit instance and subreddit streams.
        """
        self.__reddit_login(login_info)
        self.__open_streams()
        self.__collectibles()
