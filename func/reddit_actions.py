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


class ImageSubmission:
    """
    Image submission params.
    """
    def __init__(self, image_submission: praw.Reddit.submission):
        self.flair_id = image_submission.link_flair_template_id
        self.created = image_submission.created_utc
        self.score = image_submission.score
        self.ratio = image_submission.upvote_ratio
        self.permalink = image_submission.permalink
        self.url = image_submission.url
        self.approved = image_submission.approved


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
def sub_actions(reddit_data: RedditData, source_subreddits: list) -> list:
    """
    Executes checks and actions in the image submission subreddit. Returns a list of image candidates.
    :param reddit_data: RedditData object.
    :param source_subreddits: Image submission subreddit.
    :return: A list of image candidates.
    """
    reddit: praw.Reddit = reddit_data.reddit
    image_candidate_urls = ['https://i.redd.it/pcmd6d3o1oad1.png'] # Jollyver is always an option - RIP LardFetcher
    pending_count = 0
    reject_count = 0
    approve_count = 0

    for source in source_subreddits:

        # Iterate over all fetchable submissions
        for image_submission in reddit.subreddit(source).new(limit=Subreddits.MAX_IMAGE_SUBMISSIONS):

            try:
                img_sub = ImageSubmission(image_submission)

                if should_pending(img_sub):
                    update_flair(image_submission, IMGSubmissionParams.PENDING_FLAIR_ID)
                    img_sub.flair_id = IMGSubmissionParams.PENDING_FLAIR_ID
                    pending_count += 1

                if should_approve(img_sub):
                    update_flair(image_submission, IMGSubmissionParams.APPROVED_FLAIR_ID)
                    img_sub.flair_id = IMGSubmissionParams.APPROVED_FLAIR_ID
                    approve_count += 1

                if should_reject(img_sub):
                    update_flair(image_submission, IMGSubmissionParams.REJECTED_FLAIR_ID)
                    img_sub.flair_id = IMGSubmissionParams.REJECTED_FLAIR_ID
                    reject_count += 1

            except AttributeError:
                update_flair(image_submission, IMGSubmissionParams.META_FEEDBACK_OTHER_FLAIR_ID)
                logger.info(f"Something for https://reddit.com{image_submission.permalink} is missing. Investigate.")
                print(f"Something for https://reddit.com{image_submission.permalink} is missing. Investigate.")

            # Check if submission has the correct flair
            if is_valid_image_submission(image_submission, source):
                image_candidate_urls.append(image_submission.url)

    logger.info(f"Found {str(pending_count)} new image submissions.")
    logger.info(f"Updated {str(approve_count + reject_count)} old submissions.")
    logger.info(f"Using {str(len(image_candidate_urls))} valid image submissions.")

    return image_candidate_urls


def is_valid_image_submission(image_submission: praw.Reddit.submission, source_subreddit: str) -> bool:
    """
    Checks for image submission eligibility.
    :param image_submission: An image submission candidate.
    :param source_subreddit: Image candidate subreddit's name.
    :return: True if image candidate is eligible, otherwise False.
    """
    if ((source_subreddit not in image_submission.url)
            and (re.search('(i.redd.it|i.imgur.com)', image_submission.url))
            and (image_submission.link_flair_template_id == IMGSubmissionParams.APPROVED_FLAIR_ID)):
        return True
    return False


def should_pending(img_sub: ImageSubmission) -> bool:
    """
    Checks whether user-assigned flair should be set to pending if it is approved.
    :param img_sub: An ImageSubmission object with Reddit submission's attributes.
    :return: True if flair should be changed, otherwise False.
    """
    if (img_sub.flair_id == IMGSubmissionParams.CARD_SUBMISSION_FLAIR_ID
        and img_sub.approved):
        logger.info(f"The flair for https://reddit.com{img_sub.permalink} should be updated to pending status.")
        print(f"The flair for https://reddit.com{img_sub.permalink} should be updated to pending status.")
        return True
    return False


def should_approve(img_sub: ImageSubmission) -> bool:
    """
    Checks whether a pending status submission should be an eligible image submission used by the bot.
    :param img_sub: An ImageSubmission object with Reddit submission's attributes.
    :return: True if flair should be changed, otherwise False.
    """
    if (img_sub.flair_id == IMGSubmissionParams.PENDING_FLAIR_ID
        and img_sub.score >= IMGSubmissionParams.SCORE_THRESHOLD
        and img_sub.ratio >= IMGSubmissionParams.RATIO_THRESHOLD):
        logger.info(f"The https://reddit.com{img_sub.permalink} submission should be approved.")
        print(f"The https://reddit.com{img_sub.permalink} submission should be approved.")
        return True
    return False


def should_reject(img_sub: ImageSubmission) -> bool:
    """
    Checks whether a pending status submission should become a rejected submission.
    :param img_sub: An ImageSubmission object with Reddit submission's attributes.
    :return: True if flair should be changed, otherwise False.
    """
    if (img_sub.flair_id == IMGSubmissionParams.PENDING_FLAIR_ID
        and int(time.time()) - img_sub.created > IMGSubmissionParams.MAX_IMAGE_APPROVE_TIMEDELTA):
        logger.info(f"The https://reddit.com{img_sub.permalink} submission should be rejected.")
        print(f"The https://reddit.com{img_sub.permalink} submission should be rejected.")
        return True
    return False


def update_flair(image_submission: praw.Reddit.submission, new_flair_id: str):
    """
    Updates the image submission's flair on Reddit.
    :param image_submission: Image submission.
    :param new_flair_id:
    """
    image_submission.mod.flair(flair_template_id=new_flair_id)
    logger.info(f"Flair status for {image_submission.id} updated.")
    print(f"Flair status for {image_submission.id} updated.")


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
            try:
                item_type = "comment"
                comment_regex_matches = get_regex_bracket_matches(comment.body)
                low_matches = [item.casefold() for item in comment_regex_matches]
                if comment_requires_action(comment, comment_regex_matches):

                    if (MiscSettings.NFT_REPLIES_ON
                            and ColossalDreadmaw.NAME.casefold() in low_matches
                            and dreadmaw_timer.single_timer()):
                        special_reply(item_type, reddit_data, comment, ColossalDreadmaw.NAME)

                    elif (MiscSettings.NFT_REPLIES_ON
                          and StormCrow.NAME.casefold() in low_matches
                          and stormcrow_timer.single_timer()):
                        special_reply(item_type, reddit_data, comment, StormCrow.NAME)

                    else:
                        item_reply(item_type, comment, comment_regex_matches, image_links)
            except AttributeError as e:
                logger.warning(f"An AttributeError was thrown most likely due to a deleted comment. Full error: {e}")
                break
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
            try:
                item_type = "submission"
                submission_regex_matches = get_regex_bracket_matches(submission.selftext)
                low_matches = [item.casefold() for item in submission_regex_matches]
                if submission_requires_action(submission, submission_regex_matches):

                    if (MiscSettings.NFT_REPLIES_ON
                            and ColossalDreadmaw.NAME.casefold() in low_matches
                            and dreadmaw_timer.single_timer()):
                        special_reply(item_type, reddit_data, submission, ColossalDreadmaw.NAME)

                    elif (MiscSettings.NFT_REPLIES_ON
                          and StormCrow.NAME.casefold() in low_matches
                          and stormcrow_timer.single_timer()):
                        special_reply(item_type, reddit_data, submission, StormCrow.NAME)

                    else:
                        item_reply(item_type, submission, submission_regex_matches, image_links)

            except AttributeError as e:
                logger.warning(f"An AttributeError was thrown most likely due to a deleted comment. Full error: {e}")
                break

        else:
            break


def comment_requires_action(comment_data: praw.Reddit.comment, regex_matches: list) -> bool:
    """
    Checks whether a comment requires action, is by the bot itself, has no matches, or is excluded.
    :param comment_data: Reddit's praw comment API data.
    :param regex_matches: A list of regex matches in the comment.
    :return: True if comment requires action.
    """
    comment_parent_exclusions = [
        title.search(string=comment_data.submission.title) for title in MiscSettings.COMMENTS_EXCLUSIONS
    ]

    if comment_data.author.name in MiscSettings.IGNORE_CALLS_FROM:  # Bots
        logger.info("Bot will not reply to itself or to the real CardFetcher (comment). " + comment_data.id)
        return False

    elif not regex_matches:  # No regex matches
        logger.info("No matches in comment. " + comment_data.id)
        return False

    elif any(comment_parent_exclusions):  # Is on exclusion list
        logger.info("Submission of the comment on exclusion list. " + comment_data.id)
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

    submission_exclusions = [
        title.search(string=submission_data.title) for title in MiscSettings.SUBMISSION_EXCLUSIONS
    ]

    if submission_data.author.name in MiscSettings.IGNORE_CALLS_FROM:  # Bots
        logger.info(
            "Bot will not reply to itself or to the real CardFetcher (submission). "
            + submission_data.id)
        return False

    elif not regex_matches:  # No regex matches
        logger.info("No matches in submission. " + submission_data.id)
        return False

    elif any(submission_exclusions):  # Is on exclusion list
        logger.info("Submission on exclusion list. " + submission_data.id)
        return False

    else:  # Eligible for reply
        logger.info(
            "Should reply to eligible post (" + ', '.join(regex_matches) + "): https://www.reddit.com"
            + submission_data.permalink
        )
        return True


def item_reply(item_type: str, item_data: praw.Reddit.comment, regex_matches: list, image_links: list):
    """
    Executes the reply action to an eligible item.
    :param item_type:
    :param item_data: Item to reply to.
    :param regex_matches: A list of regex matches in the item.
    :param image_links: A list of image candidate links.
    """
    reply_text = generate_reply_text(regex_matches, image_links)
    item_data.reply(reply_text)
    logger.info(f"Reply to {item_type} successful: https://www.reddit.com" + item_data.permalink)
    print(f"Reply to {item_type} successful: https://www.reddit.com" + item_data.permalink)


def special_reply(item_type: str, reddit_data: RedditData, item, callname: str):
    """
    Executes the special collectible reply action to an eligible comment or submission.
    :param item_type:
    :param reddit_data: A RedditData object.
    :param item: A comment or a submission.
    :param callname: Name of the card that was called.
    """
    if callname == ColossalDreadmaw.NAME:
        dreadmaw_art = reddit_data.collectibles[ColossalDreadmaw.NAME].dreadmaw_ascii_art()
        item.reply(dreadmaw_art)
        dreadmaw_timer.new_expiry_time(random.randint(ColossalDreadmaw.TIMER_MIN, ColossalDreadmaw.TIMER_MAX))
        logger.info(f"Colossal Dreadmaw NFT reply to {item_type} successful: https://www.reddit.com" + item.permalink)
        print(f"Colossal Dreadmaw NFT reply to {item_type} successful: https://www.reddit.com" + item.permalink)

    elif callname == StormCrow.NAME:
        stormcrow_art = reddit_data.collectibles[StormCrow.NAME].stormcrow_ascii_art()
        item.reply(stormcrow_art)
        stormcrow_timer.new_expiry_time(random.randint(StormCrow.TIMER_MIN, StormCrow.TIMER_MAX))
        logger.info(f"Storm Crow NFT reply to {item_type} successful: https://www.reddit.com" + item.permalink)
        print(f"Storm Crow NFT reply to {item_type} successful: https://www.reddit.com" + item.permalink)
