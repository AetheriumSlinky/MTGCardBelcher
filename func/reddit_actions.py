"""Contains functions that make Reddit API requests."""

import time
import re
import random

import praw
import praw.exceptions
import prawcore

from func.base_logger import logger
from func.reddit_connection import RedditData
from data.exceptions import MainOperationException
from data.configs import IMGSubmissionParams, Subreddits, MiscSettings, dreadmaw_timer, stormcrow_timer
from data.collectibles import ColossalDreadmaw, StormCrow
from func.text_functions import get_regex_bracket_matches, generate_reply_text


def main_error_handler(func):
    """
    Raises MainOperationError during abnormal operation.
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
        except praw.exceptions.RedditAPIException as rapi_e:
            logger.warning("RedditAPIException, retry in 10 seconds. Error code: " + str(rapi_e))
            time.sleep(10)
            raise MainOperationException
        except praw.exceptions.APIException as api_e:
            logger.warning("APIException, retry in 10 seconds. Error code: " + str(api_e))
            time.sleep(10)
            raise MainOperationException
    return wrapper


@main_error_handler
def source_sub_action(reddit_data: RedditData, source_subreddits: list) -> list:
    """
    Executes checks and actions in the image submission subreddit. Returns a list of image candidates.
    :param reddit_data: RedditData object.
    :param source_subreddits: Image submission subreddit.
    :return: A list of image candidates.
    """
    reddit: praw.Reddit = reddit_data.reddit
    image_candidate_urls = ['https://i.redd.it/pcmd6d3o1oad1.png'] # Jollyver is always an option - RIP LardFetcher
    flair_update_count = 0

    for source in source_subreddits:

        # Iterate over all fetchable submissions
        for image_submission in reddit.subreddit(source).new(limit=Subreddits.MAX_IMAGE_SUBMISSIONS):

            # Figure out if a new flair is needed for an image post
            new_flair_id = determine_new_flair_id(image_submission, source)

            # If a new flair was generated update current flair
            if new_flair_id:
                flair_update_count += 1
                update_flair(image_submission, new_flair_id)

            # Check if submission has the correct flair
            if image_submission_is_eligible(image_submission, source):
                image_candidate_urls.append(image_submission.url)

    logger.info(f"Found and updated {str(flair_update_count)} image submission flairs.")
    logger.info(f"Found {str(len(image_candidate_urls))} valid image submissions.")
    return image_candidate_urls


def image_submission_is_eligible(image_submission: praw.Reddit.submission, source_subreddit: str) -> bool:
    """
    Checks for image submission eligibility.
    :param image_submission: An image submission candidate.
    :param source_subreddit: Image candidate subreddit's name.
    :return: True if image candidate is eligible, otherwise False.
    """
    if ((source_subreddit not in image_submission.url)
            and (re.search('(i.redd.it|i.imgur.com)', image_submission.url))
            and (image_submission.link_flair_template_id == IMGSubmissionParams.APPROVED_FLAIR_ID)):

            # Fetching from the correct place, post is an image and has the correct flair
            return True

    # At least one of the conditions was off, probably the flair
    return False


def determine_new_flair_id(image_submission: praw.Reddit.submission, source_subreddit: str) -> str:
    """
    Determines the new flair ID for an image submission if its status has changed since the last check.
    :param image_submission: Image submission.
    :param source_subreddit: Image source subreddit name.
    :return: If a change is needed a new flair ID string, otherwise an empty string.
    """
    flair_id = ''

    if (source_subreddit not in image_submission.url
        and re.search('(i.redd.it|i.imgur.com)', image_submission.url)):

        try:
            if (image_submission.link_flair_template_id == IMGSubmissionParams.CARD_SUBMISSION_FLAIR_ID
                and image_submission.approved):
                flair_id = IMGSubmissionParams.PENDING_FLAIR_ID
                logger.info(f"The flair for https://reddit.com{image_submission.permalink} should be updated.")
                print(f"The flair for https://reddit.com{image_submission.permalink} should be updated.")

            if image_submission.link_flair_template_id == IMGSubmissionParams.PENDING_FLAIR_ID:
                if (image_submission.score >= IMGSubmissionParams.SCORE_THRESHOLD
                    and image_submission.upvote_ratio >= IMGSubmissionParams.RATIO_THRESHOLD):
                    flair_id = IMGSubmissionParams.APPROVED_FLAIR_ID
                    logger.info(f"The flair for https://reddit.com{image_submission.permalink} should be updated.")
                    print(f"The flair for https://reddit.com{image_submission.permalink} should be updated.")

            if (image_submission.link_flair_template_id == IMGSubmissionParams.PENDING_FLAIR_ID
                    and int(time.time()) - image_submission.created_utc
                    > IMGSubmissionParams.MAX_IMAGE_APPROVE_TIMEDELTA):
                flair_id = IMGSubmissionParams.REJECTED_FLAIR_ID
                logger.info(f"The flair for https://reddit.com{image_submission.permalink} should be updated.")
                print(f"The flair for https://reddit.com{image_submission.permalink} should be updated.")

        except AttributeError:
            flair_id = IMGSubmissionParams.META_FEEDBACK_OTHER_FLAIR_ID
            logger.info(f"The flair for https://reddit.com{image_submission.permalink} is missing. Using 'Other'.")
            print(f"The flair for https://reddit.com{image_submission.permalink} is missing. Using 'Other'.")

    return flair_id


def update_flair(image_submission: praw.Reddit.submission, new_flair_id: str):
    """
    Updates the image submission's flair on Reddit.
    :param image_submission: Image submission.
    :param new_flair_id:
    """
    if new_flair_id == IMGSubmissionParams.PENDING_FLAIR_ID:
        flair_text = "pending"
    elif new_flair_id == IMGSubmissionParams.APPROVED_FLAIR_ID:
        flair_text = "approved"
    elif new_flair_id == IMGSubmissionParams.REJECTED_FLAIR_ID:
        flair_text = "rejected"
    else:
        flair_text = "some other flair"

    image_submission.mod.flair(flair_template_id=new_flair_id)
    logger.info(f"Flair status for {image_submission.id} updated to '{flair_text}'.")
    print(f"Flair status for {image_submission.id} updated to '{flair_text}'.")


@main_error_handler
def comment_action(reddit_data: RedditData, target_subreddit: str, image_links: list):
    """
    Executes check and reply for a comment.
    :param reddit_data: RedditData object.
    :param target_subreddit: Targeted subreddit.
    :param image_links: Image link candidates.
    """
    for comment in reddit_data.subreddit_streams[target_subreddit].comments:
        if comment is not None:
            comment_regex_matches = get_regex_bracket_matches(comment.body)
            low_matches = [item.casefold() for item in comment_regex_matches]
            if comment_requires_action(comment, comment_regex_matches):

                if (MiscSettings.NFT_REPLIES_ON
                        and ColossalDreadmaw.NAME.casefold() in low_matches
                        and dreadmaw_timer.single_timer()):
                    special_reply(reddit_data, comment, ColossalDreadmaw.NAME)

                elif (MiscSettings.NFT_REPLIES_ON
                      and StormCrow.NAME.casefold() in low_matches
                      and stormcrow_timer.single_timer()):
                    special_reply(reddit_data, comment, StormCrow.NAME)

                else:
                    comment_reply(comment, comment_regex_matches, image_links)
        else:
            break


@main_error_handler
def submission_action(reddit_data: RedditData, target_subreddit, image_links: list):
    """
    Executes check and reply for a submission.
    :param reddit_data: RedditData object.
    :param target_subreddit: Targeted subreddit.
    :param image_links: Image link candidates.
    """
    for submission in reddit_data.subreddit_streams[target_subreddit].submissions:
        if submission is not None:
            submission_regex_matches = get_regex_bracket_matches(submission.selftext)
            low_matches = [item.casefold() for item in submission_regex_matches]
            if submission_requires_action(submission, submission_regex_matches):

                if (MiscSettings.NFT_REPLIES_ON
                        and ColossalDreadmaw.NAME.casefold() in low_matches
                        and dreadmaw_timer.single_timer()):
                    special_reply(reddit_data, submission, ColossalDreadmaw.NAME)

                elif (MiscSettings.NFT_REPLIES_ON
                      and StormCrow.NAME.casefold() in low_matches
                      and stormcrow_timer.single_timer()):
                    special_reply(reddit_data, submission, StormCrow.NAME)

                else:
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
        MiscSettings.WEEKLY_UNJERK.search(string=comment_data.submission.title)
    ]

    if comment_data.author.name in MiscSettings.IGNORE_CALLS_FROM:  # Bots
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
            "Should reply to eligible comment (" + ', '.join(regex_matches) + "): https://www.reddit.com"
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
        MiscSettings.WEEKLY_UNJERK.search(string=submission_data.title),
        MiscSettings.BOTTOM_5.search(string=submission_data.title),
    ]

    if submission_data.author.name in MiscSettings.IGNORE_CALLS_FROM:  # Bots
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
            "Should reply to eligible post (" + ', '.join(regex_matches) + "): https://www.reddit.com"
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


def special_reply(reddit_data: RedditData, item, callname: str):
    """
    Executes the special collectible reply action to an eligible comment or submission.
    :param reddit_data: A RedditData object.
    :param item: A comment or a submission.
    :param callname: Name of the card that was called.
    """
    if callname == ColossalDreadmaw.NAME:
        dreadmaw_art = reddit_data.collectibles[ColossalDreadmaw.NAME].dreadmaw_ascii_art()
        item.reply(dreadmaw_art)
        dreadmaw_timer.new_expiry_time(random.randint(ColossalDreadmaw.TIMER_MIN, ColossalDreadmaw.TIMER_MAX))
        logger.info("Colossal Dreadmaw collectible NFT reply successful: https://www.reddit.com" + item.permalink)
        print("Colossal Dreadmaw collectible NFT reply successful: https://www.reddit.com" + item.permalink)

    elif callname == StormCrow.NAME:
        stormcrow_art = reddit_data.collectibles[StormCrow.NAME].stormcrow_ascii_art()
        item.reply(stormcrow_art)
        stormcrow_timer.new_expiry_time(random.randint(StormCrow.TIMER_MIN, StormCrow.TIMER_MAX))
        logger.info("Storm Crow collectible NFT reply successful: https://www.reddit.com" + item.permalink)
        print("Storm Crow collectible NFT reply successful: https://www.reddit.com" + item.permalink)
