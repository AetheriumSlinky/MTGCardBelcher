"""Contains login info and reply target subreddits."""

import re
from func.timer import RefreshTimer

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
    META_FEEDBACK_OTHER_FLAIR_ID = '997724da-2e80-11ef-996d-26eb2b2aa996'


class MiscSettings:
    """
    Miscellaneous bot settings.
    """
    IGNORE_CALLS_FROM = ['MTGCardBelcher', 'MTGCardFetcher']
    WEEKLY_UNJERK = re.compile(r'.*unjerk.*thread.*', flags=re.IGNORECASE)
    BOTTOM_5 = re.compile(r'.*bottom.*scoring.*', flags=re.IGNORECASE)
    NFT_REPLIES_ON = True


# This timer is set for the Negate special flavour so that it's not called too often (once a day)
# Starts at 0 so that the reply is available immediately after each bot restart
negate_timer = RefreshTimer(0)

# This time is set for the special Colossal Dreasmaw text so that it's not called too often (variable cooldown)
# Starts at 0 so that the reply is available immediately after each bot restart
dreadmaw_timer = RefreshTimer(0)

# This timer is set for the special Storm Crow text so that it's not called too often (variable cooldown)
# Starts at 0 so that the reply is available immediately after each bot restart
stormcrow_timer = RefreshTimer(0)
