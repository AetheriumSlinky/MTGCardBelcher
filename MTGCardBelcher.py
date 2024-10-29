"""Bot."""

import re
import time
import random
import logging

import praw
import praw.exceptions
import prawcore
import requests

# MTGCardBelcher v1.0.0 by /u/MustaKotka (AetheriumSlinky)


class RastamonCard:
    """
    A class to represent a Rastamonliveup card.
    """
    def __init__(self, proper_name: str, spellings: list, image: str):
        """
        Constructs the Rastamonliveup card object that contains the names and links of the card.
        :param proper_name: Proper spelling of the card.
        :param spellings: Most common alternative (incorrect) spellings.
        :param image: Link to card image.
        """
        self.proper_name = proper_name
        self.spellings = spellings
        self.image = image

    def find_name(self, suspect_name: str):
        """
        Finds the proper name of the Rastamonliveup card from the pool of alternate spellings.
        :param suspect_name: Suspected Rastamonliveup cardname.
        :return: Proper name or empty string if no match is found.
        """
        if suspect_name in self.spellings:
            return self.proper_name
        else:
            return ""


class BotReplyText:
    """
    A class to represent a bot reply text divided into text elements.
    """
    def __init__(self, header: str = "", body: str = "", flavour: str = "",
                 footer: str = ""):
        """
        Constructs the bot reply text object elements.
        :param header: Element that contains the entity delivering the cards.
        :param body: Element that contains the card links.
        :param flavour: Element that contains the flavour text.
        :param footer: Element that contains the footer text.
        """
        self.header = header
        self.body = body
        self.flavour = flavour
        self.footer = footer

    def body_add_text(self, text: str):
        """
        Adds a text string to the body parameter.
        :param text: A string of text to be added to the text body parameter.
        """
        self.body += f'''{text}'''


def start_logger(log_file):
    """
    Logging config.
    :param log_file: File to write to.
    :return: Log.
    """
    log = logging.getLogger(__name__)
    logging.basicConfig(
        filename=log_file, encoding='utf-8', level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M;%S')
    return log


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


def reddit_login(login_info) -> praw.Reddit:
    """
    Logs in to Reddit.
    :param login_info: A text file containing the OAuth info.
    :return: Reddit.
    """
    with open(login_info, "r") as oauth_file:
        info = oauth_file.read().splitlines()

    reddit = praw.Reddit(
        client_id=info[0],
        client_secret=info[1],
        password=info[2],
        user_agent=info[3],
        username=info[4],
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


def get_regex_bracket_matches(text: str) -> list:
    """
    Regex searches for double square brackets (bot call) in text. Accommodates old/mobile/new Reddit.
    :param text: Text to search.
    :return: A list of all matches.
    """
    browser_double_bracket_matches = re.findall(r'''\\\[\\\[([^\\\[\]]+)\\]\\]''', text)
    mobile_double_bracket_matches = re.findall(r'''\[\[([^\[\]]+)]]''', text)
    all_matches = browser_double_bracket_matches + mobile_double_bracket_matches  # Pray for no doubles
    return all_matches


def get_scryfall_image(cardname: str) -> str:
    """
    Fetches the image URL that matches the cardname.
    :param cardname: Cardname.
    :return: Image URL if an exact match is found, empty string if no match is found or Scryfall can't be reached.
    """
    try:
        cardname_match = requests.get(f'https://api.scryfall.com/cards/named?exact={cardname}')
        if cardname_match:
            if cardname_match.json().get('content_warning'):  # Don't append the forbidden cards
                image_url = ""
            else:
                image_url = cardname_match.json()['image_uris']['normal']
        else:
            image_url = ""

    # Lazy Except because Scryfall isn't that important, just skip this if it doesn't work
    except Exception as scryfall_e:
        image_url = ""
        logger.warning("Something went wrong with Scryfall. Ignoring Scryfall: " + str(scryfall_e))

    return image_url


def get_scryfall_flavour() -> str:
    """
    Fetches a random flavour text from Scryfall.
    :return: A random flavour text, a standard funny error text string if Scryfall can't be reached.
    """
    try:
        random_flavour_card = requests.get(f'https://api.scryfall.com/cards/random?q=has%3Aflavor')
        random_flavour = random_flavour_card.json()['flavor_text']
    # Lazy except because Scryfall isn't that important, just skip it if it doesn't work
    except Exception as scryfall_e:
        logger.warning("Something went wrong with Scryfall. Ignoring Scryfall: " + str(scryfall_e))
        random_flavour = "Sometimes, rarely, Scryfall is not there and the world is out of flavour."
    return random_flavour


def rastamon_card_name_and_link(name: str) -> tuple:
    """
    Provided with a suspected Rastamonliveup card name,
    it finds the corresponding proper name and link to the card image.
    :param name: A suspected card name, probably from a regex match.
    :return: A tuple(proper name, link to card image).
    """

    # Create all Rastamonliveup cards
    simbaba = RastamonCard("Simbaba",
        ["simbaba"],
        "https://i.redd.it/3acfd9iryqjd1.png")

    japudi = RastamonCard("Japudi",
        ["japudi"],
        "https://i.redd.it/ln92vcaxjnfa1.jpg")

    kuka_beyo = RastamonCard("Kuka Beyo",
        ["kuka beyo"],
        "https://i.redd.it/7tg9y2u7mvfa1.jpg")

    tobo_dibi = RastamonCard("Tōbō Dibi",
        ["tobo dibi", "tōbō dibi"],
        "https://i.redd.it/his9093feaga1.jpg")

    bosgwan = RastamonCard("Bôsgwan",
        ["bosgwan", "bôsgwan"],
        "https://i.redd.it/b8ti2tcf9wga1.jpg")

    mwabdi = RastamonCard("Mwabdi",
        ["mwabdi"],
        "https://i.redd.it/v7tpor93xuha1.jpg")

    kadyoba = RastamonCard("Kadÿoba",
        ["kadyoba", "kadÿoba"],
        "https://i.redd.it/on1zb0bu42ja1.jpg")

    komdege_swigu = RastamonCard("Komdegé Swígu",
        ["komdege swigu", "komdegé swigu", "komdege swígu", "komdegé swígu"],
        "https://i.redd.it/kte28a4yk8ka1.jpg")

    dodonbe_dugdjita = RastamonCard("Dodonbè Dugdjita",
        ["dodonbe dugdjita", "dodonbè dugdjita"],
        "https://i.redd.it/p5ywsh4yk8ka1.jpg")

    sembizi_wamdeyo = RastamonCard("Sembizi Wamdeyo",
        ["sembizi wamdeyo"],
        "https://i.redd.it/q3ybd1udokra1.jpg")

    sebi_gyandu = RastamonCard("Sebi Gyandu",
        ["sebi gyandu"],
        "https://i.redd.it/uvqqezzgp4dd1.jpeg")

    # List-ify cards for searching
    cards = [simbaba, japudi, kuka_beyo, tobo_dibi, bosgwan, mwabdi,
             kadyoba, komdege_swigu, dodonbe_dugdjita, sembizi_wamdeyo, sebi_gyandu]

    # If a match is found return proper name and link to card image
    for creature in cards:
        if creature.find_name(name.casefold()):
            return creature.proper_name, creature.image
    return "", ""


def generate_reply_text(text: str, links: list) -> str:
    """
    Generates the text that the bot will attempt to reply with.
    :param text: The text body from a comment or a submission.
    :param links: A list of joke image link candidates.
    :return: Fully formatted reply text.
    """

    reply = BotReplyText()
    regex_matches = get_regex_bracket_matches(text)

    # Determines whether a regular reply is delivered or if one of the special modes is chosen instead
    choose_special = random.randint(-1, 1001)

    if choose_special == -1:  # Special Eldrazi, text-only
        reply.body = ("The Invasion annihilated the cards you were looking for.\n\n"
                      "Nothing but ashes and pain remain. Somehow you survive.\n\n")
        logger.info("Easter egg Eldrazi delivered.")

    elif choose_special == 0:  # Special shagging monkes, static image link only
        reply.body = ("Instead of looking for any cards you stop to admire the marvels of nature:\n\n"
                      "[The Nature Is Wonderful](https://i.redd.it/cwhcrm1b74fd1.png)\n\n")
        logger.info("Easter egg Uktabi Orangutan delivered.")

    elif choose_special == 1:  # Special phyrexian oil
        reply.header = ("You find the cards you're looking for, "
                        "but they're covered in that strange oil... It's probably nothing.\n\n")
        logger.info("Easter egg Phyrexian oil delivered.")

    elif choose_special == 2:  # Special licid mind injection
        reply.header = "The Licids have imprinted the cards you're looking for into your mind:\n\n"
        logger.info("Easter egg Licids delivered.")

    elif choose_special == 3:  # Special Dreadmaw
        reply.header = "You feel the ground quake. You see the cards you're looking for, but it's too late.\n\n"
        logger.info("Easter egg Colossal Dreadmaw delivered.")

    elif choose_special == 4:  # Special hungery Yargle
        reply.header = ("The Frog Spirit had the cards... But it was hungry and ate them. "
                        "Worry not, it tells you what they were: 'Gnshhagghkkapphribbit'.\n\n")
        logger.info("Easter egg Yargle delivered.")

    elif choose_special == 5:  # Special grumpy bot
        reply.header = ("You! Yes, you! I'm tired of your and your friends' crap. "
                        "Go fetch. _Throws the cards on the floor:_\n\n")
        logger.info("Easter egg 'Sod Off' delivered.")

    else:  # The normal mode - determine a random creature type
        creature_type = random.choice([
            "Horrors", "Kobolds", "Goblins", "Zombies", "Vampires", "Werewolves", "Legitimate Businesspeople",
            "Brushwaggs", "Camarids", "Giants", "Devils", "Hydras", "Krakens", "Nightmares", "Dragons",
            "Cyclopes", "Skeletons", "Dreadnoughts", "Wurms", "Leviathans",
        ])
        reply.header = f"The {creature_type} have delivered the cards you're looking for:\n\n"

    # If there is only a single card to fetch get a random flavour text from Scryfall
    if len(regex_matches) == 1:
        reply.flavour = f'''_{get_scryfall_flavour()}_\n\n'''

    # If neither no-card links special mode was chosen execute normal mode
    if choose_special >= 1:

        # Attempt to fetch regex matches and associated exact card name match from Scryfall
        for cardname in regex_matches:
            scryfall_image = get_scryfall_image(cardname)
            rastamon_card = rastamon_card_name_and_link(cardname)

            # Some overrides for Rastamonliveup cards
            if rastamon_card[0]:
                reply.header = "Rastamonliveup has delivered the cards you're looking for:\n\n"
                reply.body_add_text(f'''[{rastamon_card[0]}]'''
                                    f'''({rastamon_card[1]})\n\n''')
                if rastamon_card[0] == "Kuka Beyo":
                    reply.body = f'''[Kuka Beyo]({rastamon_card[1]}) :)\n\n'''
                    reply.flavour = ""
                if rastamon_card[0] == "Sebi Gyandu":
                    reply.flavour = "_Tell the children the truth_\n\n"

            # If a real cardname matches the regex make a Scryfall link
            elif scryfall_image:
                reply.body_add_text(f'''[{cardname}]({random.choice(links)})'''
                                    f''' - ([sf]({scryfall_image}))\n\n''')

            # No real cardname matches, no Scryfall link
            else:
                reply.body_add_text(f'''[{cardname}]({random.choice(links)})\n\n''')

    # Add the standard footer text
    reply.footer = "*********\n\nSubmit your content at: r/MTGCardBelcher"

    reply_text = f'''{reply.header}{reply.body}{reply.flavour}{reply.footer}'''

    return reply_text


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


# Setup
if __name__ == "__main__":
    print("Init...")

    # Create a text file (here oauth.txt) with five rows
    # or any other preferred method of delivering login info.
    # 1. Client id
    # 2. Secret
    # 3. Account password
    # 4. User Agent information
    # 5. Account username

    oauth = "P:\\oauth.txt"
    logs = "P:\\log.txt"
    logger = start_logger(logs)  # Start logging
    logger.info('New Reddit session start.')
    target_subreddits = ["magicthecirclejerking", "MTGCardBelcher_dev"]  # Targets list
    reddit_streams = login_sequence(oauth, target_subreddits)  # Open Reddit
    image_refresh_timer = time.time()  # Image submission fetch timer
    image_submission_links = get_image_links(reddit_streams["reddit"])  # Fetch joke images once before main loop
    logger.info('Reddit session initiation complete.')
    print("...init complete.")

    # Main loop
    while True:
        if time.time() - image_refresh_timer > 1800:  # Get image links every 30 minutes
            image_refresh_timer = time.time()
            image_submission_links = get_image_links(reddit_streams["reddit"])

        for sub in target_subreddits:
            comment_action(reddit_streams["comments"][sub], image_submission_links)
            submission_action(reddit_streams["submissions"][sub], image_submission_links)

        # Reddit has in-built sleep already but just in case sleep again
        time.sleep(5)
