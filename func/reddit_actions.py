"""Contains functions that make Reddit API requests."""

import time
import re

import praw.exceptions
import prawcore

from data.configs import oauth, target_subreddits
from func.base_logger import logger
from func.text_functions import get_regex_bracket_matches, generate_reply_text
from func.reddit_login import login_sequence


def main_error_handler(func):
    """
    Handles errors during normal operation. Attempts re-login if all else fails.
    """
    def wrapper(*args, **kwargs):
        """Wrapper."""
        while True:
            try:
                return func(*args, **kwargs)
            except prawcore.ServerError as server_err:
                logger.warning("Server error, retry in 5 minutes. Error code: " + str(server_err))
                time.sleep(300)
                login_sequence(oauth, target_subreddits)
            except prawcore.RequestException as request_exc:
                logger.warning("Incomplete HTTP request, retry in 10 seconds. Error code: " + str(request_exc))
                time.sleep(10)
                login_sequence(oauth, target_subreddits)
            except prawcore.ResponseException as response_exc:
                logger.warning("HTTP request response error, retry in 30 seconds. Error code: " + str(response_exc))
                time.sleep(30)
                login_sequence(oauth, target_subreddits)
            except praw.exceptions.RedditAPIException as api_e:
                logger.warning("APIException. Error code: " + str(api_e))
                time.sleep(30)
    return wrapper


@main_error_handler
def get_image_links(reddit: praw.Reddit) -> list:
    """
    Searches target CardBelcher subreddit for image links.
    :param reddit: Reddit.
    :return: A list of image candidate links.
    """
    card_belcher = reddit.subreddit('MTGCardBelcher')
    image_candidates = ['https://i.redd.it/pcmd6d3o1oad1.png']  # Jollyver is always an option - RIP LardFetcher
    for image_submissions in card_belcher.new(limit=1000):  # Get a looot of images
        if "/r/MTGCardBelcher" not in image_submissions.url:
            if (re.search('(i.redd.it|i.imgur.com)', image_submissions.url)
                    and image_submissions.link_flair_text == "Card Submission"):  # Check for correct flair
                image_candidates.append(image_submissions.url)
    logger.info("Found " + str(len(image_candidates)) + " valid image submissions.")
    return image_candidates


def comment_requires_action(comment_data: praw.Reddit.comment) -> bool:
    """
    Checks whether a comment requires action, is by the bot itself, has no matches, or is excluded.
    :param comment_data: Reddit's praw comment API data.
    :return: True if comment requires action.
    """
    # Get regex matches
    comment_double_bracket_matches = get_regex_bracket_matches(comment_data.body)

    # State exclusions
    submission_exclusions = [
        # Weekly unjerk
        re.search(r'.*unjerk.*thread.*', string=comment_data.submission.title, flags=re.IGNORECASE)
    ]

    if comment_data.author.name == ('MTGCardBelcher' or 'MTGCardFetcher'):  # Bots
        logger.info("Bot will not reply to itself or to the real CardFetcher (comment). " + comment_data.permalink)
        return False

    elif not comment_double_bracket_matches:  # No regex matches
        logger.info("No matches in comment. " + comment_data.permalink)
        return False

    elif None not in submission_exclusions:  # Is on exclusion list
        logger.info("Parent submission of the comment on exclusion list. " + comment_data.permalink)
        return False

    else:  # Eligible for reply
        logger.info(
            "Should reply to eligible comment (" + str(comment_double_bracket_matches) + "): "
            + comment_data.permalink
        )
        return True


def submission_requires_action(submission_data: praw.Reddit.submission) -> bool:
    """
    Checks whether a submission requires action, is by the bot itself, has no matches, or is excluded.
    :param submission_data: Reddit's praw submission API data.
    :return: True if submission requires action.
    """
    # Get regex matches
    submission_double_bracket_matches = get_regex_bracket_matches(submission_data.selftext)

    # State exclusions
    submission_exclusions = [
        # Weekly unjerk
        re.search(r'.*unjerk.*thread.*', string=submission_data.title, flags=re.IGNORECASE),
        # Bottom scoring submissions
        re.search(r'.*bottom.*scoring.*', string=submission_data.title, flags=re.IGNORECASE),
    ]

    if submission_data.author.name == ("MTGCardBelcher" or "MTGCardFetcher"):  # Bots
        logger.info(
            "Bot will not reply to itself or to the real CardFetcher (submission). "
            + submission_data.permalink)
        return False

    elif not submission_double_bracket_matches:  # No regex matches
        logger.info("No matches in submission. " + submission_data.permalink)
        return False

    elif None not in submission_exclusions:  # Is on exclusion list
        logger.info("Submission on exclusion list. " + submission_data.permalink)
        return False

    else:  # Eligible for reply
        logger.info(
            "Should reply to eligible post (" + str(submission_double_bracket_matches) + "): "
            + submission_data.permalink
        )
        return True


def comment_reply(comment_data: praw.Reddit.comment, image_links: list):
    """
    Executes the reply action to an eligible comment.
    :param comment_data: Comment to reply to.
    :param image_links: A list of image candidate links.
    """
    reply_text = generate_reply_text(comment_data.body, image_links)
    comment_data.reply(reply_text)
    logger.info("Comment reply successful: " + comment_data.id)
    print("Comment reply successful: " + comment_data.permalink)


def submission_reply(submission_data: praw.Reddit.submission, image_links: list):
    """
    Executes the reply action to an eligible submission.
    :param submission_data: Submission to reply to.
    :param image_links: A list of image candidate links.
    """
    reply_text = generate_reply_text(submission_data.selftext, image_links)
    submission_data.reply(reply_text)
    logger.info("Submission reply successful: " + submission_data.id)
    print("Submission reply successful: " + submission_data.permalink)


@main_error_handler
def comment_action(comment_stream, image_links: list):
    """
    Executes check and reply for a comment.
    :param comment_stream: The praw comment stream.
    :param image_links: Image link candidates.
    """
    for comment in comment_stream:
        try:
            if comment_requires_action(comment):
                comment_reply(comment, image_links)
        except AttributeError:  # No comments in stream results in None
            break


@main_error_handler
def submission_action(submission_stream, image_links: list):
    """
    Executes check and reply for a submission.
    :param submission_stream: The praw submission stream.
    :param image_links: Image link candidates.
    """
    for submission in submission_stream:
        try:
            if submission_requires_action(submission):
                submission_reply(submission, image_links)
        except AttributeError:  # No comments in stream results in None
            break
