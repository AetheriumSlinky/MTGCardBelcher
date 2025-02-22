"""Contains functions that make Reddit API requests."""

import time
import re

import praw
import praw.exceptions
import prawcore

from data.exceptions import MainOperationException
from func.base_logger import logger
from func.text_functions import (get_regex_bracket_matches, generate_reply_text,
                                 dreadmaw_timer, dreadmaw_holder, DreadmawObj)


def main_error_handler(func):
    """
    Raises errors during normal operation.
    """
    def wrapper(*args, **kwargs):
        """Wrapper."""
        try:
            return func(*args, **kwargs)
        except prawcore.ServerError as server_err:
            logger.warning("Server error, retry in 5 minutes. Error code: " + str(server_err))
            time.sleep(300)
            raise MainOperationException
        except prawcore.RequestException as request_exc:
            logger.warning("Incomplete HTTP request, retry in 10 seconds. Error code: " + str(request_exc))
            time.sleep(10)
            raise MainOperationException
        except prawcore.ResponseException as response_exc:
            logger.warning("HTTP request response error, retry in 30 seconds. Error code: " + str(response_exc))
            time.sleep(30)
            raise MainOperationException
        except praw.exceptions.RedditAPIException as api_e:
            logger.warning("APIException. Error code: " + str(api_e))
            time.sleep(30)
            raise MainOperationException
    return wrapper


@main_error_handler
def get_image_links(reddit: praw.Reddit, fetchable_subs: list) -> list:
    """
    Searches target subreddits for image links.
    :param reddit: The Reddit instance.
    :param fetchable_subs: A list of subreddits where the image submissions are found.
    :return: A list of image candidate links.
    """
    image_candidates = ['https://i.redd.it/pcmd6d3o1oad1.png']  # Jollyver is always an option - RIP LardFetcher
    for fetchable_sub in fetchable_subs:  # Search all subreddits defined as sources for images
        fetchable = reddit.subreddit(fetchable_sub)
        for image_submission in fetchable.new(limit=1000):  # Get a looot of images
            if fetchable_sub not in image_submission.url:
                if (re.search('(i.redd.it|i.imgur.com)', image_submission.url)
                        and image_submission.link_flair_text == "Approved Submission"):  # Check for correct flair
                    image_candidates.append(image_submission.url)
    logger.info("Found " + str(len(image_candidates)) + " valid image submissions.")
    return image_candidates


@main_error_handler
def comment_action(reddit: praw.Reddit, comment_stream, image_links: list):
    """
    Executes check and reply for a comment.
    :param reddit: The Reddit instance.
    :param comment_stream: The praw comment stream.
    :param image_links: Image link candidates.
    """
    for comment in comment_stream:
        if comment is not None:
            comment_regex_matches = get_regex_bracket_matches(comment.body)
            if comment_requires_action(comment, comment_regex_matches):
                if (DreadmawObj.get_name() in [item.casefold() for item in comment_regex_matches]
                        and dreadmaw_timer.single_timer()):
                    dreadmaw_count_increment(reddit, dreadmaw_holder)
                comment_reply(comment, comment_regex_matches, image_links)
        else:
            break


@main_error_handler
def submission_action(reddit: praw.Reddit, submission_stream, image_links: list):
    """
    Executes check and reply for a submission.
    :param reddit: The Reddit instance.
    :param submission_stream: The praw submission stream.
    :param image_links: Image link candidates.
    """
    for submission in submission_stream:
        if submission is not None:
            submission_regex_matches = get_regex_bracket_matches(submission.selftext)
            if submission_requires_action(submission, submission_regex_matches):
                if (DreadmawObj.get_name() in [item.casefold() for item in submission_regex_matches]
                        and dreadmaw_timer.single_timer()):
                    dreadmaw_count_increment(reddit, dreadmaw_holder)
                submission_reply(submission, submission_regex_matches, image_links)
        else:
            break


def comment_requires_action(comment_data: praw.Reddit.comment, regex_matches: list) -> bool:
    """
    Checks whether a comment requires action, is by the bot itself, has no matches, or is excluded.
    :param comment_data: Reddit's praw comment API data.
    :param regex_matches: A list of regex matches in the comment.
    :return: True if comment requires action.
    """
    # State exclusions
    submission_exclusions = [
        # Weekly unjerk
        re.search(r'.*unjerk.*thread.*', string=comment_data.submission.title, flags=re.IGNORECASE)
    ]

    if comment_data.author.name == ('MTGCardBelcher' or 'MTGCardFetcher'):  # Bots
        logger.info("Bot will not reply to itself or to the real CardFetcher (comment). " + comment_data.id)
        return False

    elif not regex_matches:  # No regex matches
        logger.info("No matches in comment. " + comment_data.id)
        return False

    elif None not in submission_exclusions:  # Is on exclusion list
        logger.info("Parent submission of the comment on exclusion list. " + comment_data.id)
        return False

    else:  # Eligible for reply
        logger.info(
            "Should reply to eligible comment (" + str(regex_matches) + "): https://www.reddit.com"
            + comment_data.permalink
        )
        return True


def submission_requires_action(submission_data: praw.Reddit.submission, regex_matches: list) -> bool:
    """
    Checks whether a submission requires action, is by the bot itself, has no matches, or is excluded.
    :param submission_data: Reddit's praw submission API data.
    :param regex_matches: A list of regex matches in the submission.
    :return: True if submission requires action.
    """
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
            + submission_data.id)
        return False

    elif not regex_matches:  # No regex matches
        logger.info("No matches in submission. " + submission_data.id)
        return False

    elif None not in submission_exclusions:  # Is on exclusion list
        logger.info("Submission on exclusion list. " + submission_data.id)
        return False

    else:  # Eligible for reply
        logger.info(
            "Should reply to eligible post (" + str(regex_matches) + "): https://www.reddit.com"
            + submission_data.permalink
        )
        return True


def comment_reply(comment_data: praw.Reddit.comment, regex_matches: list, image_links: list):
    """
    Executes the reply action to an eligible comment.
    :param comment_data: Comment to reply to.
    :param regex_matches: A list of regex matches in the comment.
    :param image_links: A list of image candidate links.
    """
    reply_text = generate_reply_text(regex_matches, image_links)
    comment_data.reply(reply_text)
    logger.info("Comment reply successful: https://www.reddit.com" + comment_data.permalink)
    print("Comment reply successful: https://www.reddit.com" + comment_data.permalink)


def submission_reply(submission_data: praw.Reddit.submission, regex_matches: list, image_links: list):
    """
    Executes the reply action to an eligible submission.
    :param submission_data: Submission to reply to.
    :param regex_matches: A list of regex matches in the submission.
    :param image_links: A list of image candidate links.
    """
    reply_text = generate_reply_text(regex_matches, image_links)
    submission_data.reply(reply_text)
    logger.info("Submission reply successful: https://www.reddit.com" + submission_data.permalink)
    print("Submission reply successful: https://www.reddit.com" + submission_data.permalink)


def dreadmaw_count_increment(reddit: praw.Reddit, dreadmaw: DreadmawObj):
    """
    Edits the post on Reddit that contains Dreadmaw's call count and updates the internal counter to match it.
    :param dreadmaw: A DreadmawObj object.
    :param reddit: The Reddit instance.
    """
    new_count: int = int(reddit.comment("me0tbmp").body) + 1
    reddit.comment("me0tbmp").edit(str(new_count))
    dreadmaw.calls_count = new_count
