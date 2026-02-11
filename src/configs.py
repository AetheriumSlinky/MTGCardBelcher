"""Contains login info and reply target subreddits."""

import re
from pathlib import Path

class BotInfo:
    """
    Information required to access Reddit and Scryfall.

    OAuth requires five pieces of information:
    User Agent information,
    Account Username,
    Account Password,
    Client ID,
    Secret

    Scryfall User Agent requires special headers so that requests aren't denied.
    """
    USERNAME = 'MTGCardBelcher'
    REDDIT_OAUTH = "oauth.txt"
    SCRYFALL_USER_AGENT_HEADER = {'user-agent': 'MTGCardBelcher/1.3.0', "accept": "*/*"}


class GeneralSettings:
    """
    Settings for bot's general functionality.
    """
    PROJECT_ROOT_PATH = Path(__file__).parent.parent  # config => src => root

    # Logging module levels, recommended to either leave as-is or go for 20 on LOGS and 30 on CONSOLE
    LOGS_LEVEL = 20  # Level 20 corresponds to INFO, 21 is less verbose CONFIRMATION
    CONSOLE_MESSAGE_LEVEL = 21  # Level 20 corresponds to INFO, 21 is less verbose CONFIRMATION


class Subreddits:
    """
    Call subreddits list (where the bot comments)
    and image submission subreddits list (where the joke images come from).
    """
    CALL_SUBREDDITS = ["magicthecirclejerking", "MTGCardBelcher_dev"]
    SUBMISSION_SUBREDDITS = ["MTGCardBelcher"]
    MAX_IMAGE_SUBMISSIONS = 1000  # This cannot be higher than 1000


class IMGSubmissionParams:
    """
    Time since post creation until rejection in seconds.

    Minimum upvote count for image approval.

    Minimum upvote ratio for image approval.

    Submission flair IDs: basic, pending, approved, rejected.
    """
    MAX_IMAGE_APPROVE_TIMEDELTA = 1209600  # 2 weeks
    SCORE_THRESHOLD = 30
    RATIO_THRESHOLD = 0.74
    FLAIR_IDS = {
        "new": 'fcc29ab2-9cec-11ef-adbd-76354d1eb977',
        "pending": '337aaa10-9cf5-11ef-b08d-1e57adeb694e',
        "approved": '882ae2ac-2e80-11ef-bf2d-f2bf21373915',
        "rejected": '50a490ba-9cf5-11ef-834b-f6ac6a413fab',
        "other": '997724da-2e80-11ef-996d-26eb2b2aa996',
    }


class SpecialReplySettings:
    """
    NFT collectible settings.
    """
    NFT_REPLIES_ON = True
    REPLY_MIN_TIMER = 600  # 10 min
    REPLY_MAX_TIMER = 7200  # 2 h


class ReplySettings:
    """
    Miscellaneous bot settings.
    """
    IGNORE_CALLS_FROM = ['MTGCardBelcher', 'MTGCardFetcher']
    WEEKLY_UNJERK = re.compile(r'.*weekly.*unjerk.*', flags=re.IGNORECASE)
    BOTTOM_5 = re.compile(r'.*bottom.*scoring.*', flags=re.IGNORECASE)
    SUBMISSION_EXCLUSIONS = [WEEKLY_UNJERK, BOTTOM_5]
    COMMENTS_EXCLUSIONS = [WEEKLY_UNJERK]
    REPLY_MAX_LENGTH = 2400
    REPLY_MAX_COUNT = 8
