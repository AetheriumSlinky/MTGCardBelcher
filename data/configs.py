"""Contains login info and reply target subreddits."""

import re

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
    SCRYFALL_USER_AGENT_HEADER = {'user-agent': 'MTGCardBelcher/1.2.0', "accept": "*/*"}


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
    MAX_IMAGE_APPROVE_TIMEDELTA = 1209600
    SCORE_THRESHOLD = 30
    RATIO_THRESHOLD = 0.74
    CARD_SUBMISSION_FLAIR_ID = 'fcc29ab2-9cec-11ef-adbd-76354d1eb977'
    PENDING_FLAIR_ID = '337aaa10-9cf5-11ef-b08d-1e57adeb694e'
    APPROVED_FLAIR_ID = '882ae2ac-2e80-11ef-bf2d-f2bf21373915'
    REJECTED_FLAIR_ID = '50a490ba-9cf5-11ef-834b-f6ac6a413fab'

class IgnoreExclusions:
    """
    Miscellaneous exclusions and ignores.
    """
    IGNORE_CALLS_FROM = ['MTGCardBelcher', 'MTGCardFetcher']
    WEEKLY_UNJERK = re.compile(r'.*unjerk.*thread.*', flags=re.IGNORECASE)
    BOTTOM_5 = re.compile(r'.*bottom.*scoring.*', flags=re.IGNORECASE)
