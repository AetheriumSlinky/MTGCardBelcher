import re
import time
import random
import logging

import praw
import praw.exceptions
import prawcore
import requests

# MTGCardBelcher v1.0.0 by /u/MustaKotka (AetheriumSlinky)


def start_logger(log_file):
    log = logging.getLogger(__name__)
    logging.basicConfig(
        filename=log_file, encoding='utf-8', level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M;%S')
    return log


def login_error_handler(func):
    def wrapper(*args, **kwargs):
        while True:
            try:
                func(*args, **kwargs)
                break
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
    def wrapper(*args, **kwargs):
        while True:
            try:
                func(*args, **kwargs)
                break
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
    Keeps trying to log in to Reddit.
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
    for image_submissions in card_belcher.new(limit=250):  # Get a looot of images
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
            if cardname_match.json().get('content_warning'):
                image_url = ""
            else:
                image_url = cardname_match.json()['image_uris']['normal']
        else:
            image_url = ""
    # Lazy except because Scryfall isn't that important, just skip it if it doesn't work
    except Exception as scryfall_e:
        image_url = ""
        logger.warning("Something went wrong with Scryfall. Ignoring Scryfall: " + str(scryfall_e))
    return image_url


def get_scryfall_flavour() -> str:
    """
    Fetches a random flavour text from Scryfall.
    :return: A random flavour text, a standardised text string if Scryfall can't be reached.
    """
    try:
        random_flavour_card = requests.get(f'https://api.scryfall.com/cards/random?q=has%3Aflavor')
        random_flavour = random_flavour_card.json()['flavor_text']
    # Lazy except because Scryfall isn't that important, just skip it if it doesn't work
    except Exception as scryfall_e:
        logger.warning("Something went wrong with Scryfall. Ignoring Scryfall: " + str(scryfall_e))
        random_flavour = "Sometimes, rarely, Scryfall is not there and the world is out of flavour."
    return random_flavour


def rastamonliveup_name_link(name: str) -> tuple:
    """
    Provided with a suspected Rastamonliveup card name,
    it finds the corresponding proper name and link to the card image.
    :param name: A card name, probably from a regex match.
    :return: A tuple(proper name, link to card image).
    """
    cards = {
        "Simbaba": {
            "names": ["simbaba"],
            "link": "https://i.redd.it/3acfd9iryqjd1.png"
        },
        "Japudi": {
            "names": ["japudi"],
            "link": "https://i.redd.it/ln92vcaxjnfa1.jpg"
        },
        "Kuka Beyo": {
            "names": ["kuka beyo"],
            "link": "https://i.redd.it/7tg9y2u7mvfa1.jpg",
        },
        "Tōbō Dibi": {
            "names": ["tobo dibi", "tōbō dibi"],
            "link": "https://i.redd.it/his9093feaga1.jpg",
        },
        "Bôsgwan": {
            "names": ["bosgwan", "bôsgwan"],
            "link": "https://i.redd.it/b8ti2tcf9wga1.jpg",
        },
        "Mwabdi": {
            "names": ["mwabdi"],
            "link": "https://i.redd.it/v7tpor93xuha1.jpg",
        },
        "Kadÿoba": {
            "names": ["kadyoba", "kadÿoba"],
            "link": "https://i.redd.it/on1zb0bu42ja1.jpg",
        },
        "Komdegé Swígu": {
            "names": ["komdege swigu", "komdegé swigu", "komdege swígu", "komdegé swígu"],
            "link": "https://i.redd.it/kte28a4yk8ka1.jpg",
        },
        "Dodonbè Dugdjita": {
            "names": ["dodonbe dugdjita", "dodonbè dugdjita"],
            "link": "https://i.redd.it/p5ywsh4yk8ka1.jpg",
        },
        "Sembizi Wamdeyo": {
            "names": ["sembizi wamdeyo"],
            "link": "https://i.redd.it/q3ybd1udokra1.jpg",
        },
        "Sebi Gyandu": {
            "names": ["sebi gyandu"],
            "link": "https://i.redd.it/uvqqezzgp4dd1.jpeg",
        },
    }

    for creature, info_keys in cards.items():
        if name.lower() in info_keys["names"]:
            return creature, info_keys["link"]
    return "", ""


def generate_reply_text(reply_text_string: str, image_links: list) -> str:
    """
    Generates the text that the bot will attempt to reply with. Note Scryfall API calls.
    :param reply_text_string: The regex matches from the original comment or submission.
    :param image_links: A list of images links.
    :return: Fully formatted reply text.
    """
    # Determines whether a regular reply is delivered or if one of the special modes is chosen instead
    choose_special = random.randint(-6, 1001)

    if choose_special < 1:
        logger.info('Easter egg reply delivered.')

    if choose_special == 0:  # Special Eldrazi no image card links
        bot_reply_text = (
            "The Invasion annihilated the cards you were looking for.\n\n"
            "Nothing but ashes and pain remain. Somehow you survive.\n\n"
        )

    elif choose_special == -1:  # Special shagging monkes
        bot_reply_text = (
            "Instead of looking for any cards you stop to admire the marvels of nature:\n\n"
            "[The Nature Is Wonderful]"
            "(https://i.redd.it/cwhcrm1b74fd1.png)\n\n"
        )

    else:
        regex_matches = get_regex_bracket_matches(reply_text_string)
        scryfall_images = []
        random_flavour = ""
        is_rastamonliveup_match = False

        # Attempt to fetch regex matches and associated exact card name match from Scryfall
        for cardname in regex_matches:
            scryfall_images.append(get_scryfall_image(cardname))

            # If there is only a single card to fetch also get a random flavour text from Scryfall
            if len(regex_matches) == 1:
                random_flavour = get_scryfall_flavour()

        for regex_match in regex_matches:
            rastamon_name_link_obj = rastamonliveup_name_link(regex_match)
            if rastamon_name_link_obj[0]:
                is_rastamonliveup_match = True

        if is_rastamonliveup_match:  # Special Rastamonliveup
            bot_reply_text = "Rastamonliveup has delivered the cards you're looking for:\n\n"

        elif choose_special == -2:  # Special phyrexian oil
            bot_reply_text = ("You find the cards you're looking for, "
                              "but they're covered in that strange oil... It's probably nothing.\n\n")

        elif choose_special == -3:  # Special licid mind injection
            bot_reply_text = "The Licids have imprinted the cards you're looking for into your mind:\n\n"

        elif choose_special == -4:  # Special Dreadmaw
            bot_reply_text = "You feel the ground quake. You see the cards you're looking for, but it's too late.\n\n"

        elif choose_special == -5:  # Special hungery Yargle
            bot_reply_text = ("The Frog Spirit had the cards... But it was hungry and ate them. "
                              "Worry not, it tells you what they were: 'Gnshhagghkkapphribbit'.\n\n")

        elif choose_special == -6:  # Special grumpy bot
            bot_reply_text = ("You! Yes, you! I'm tired of your and your friends' crap. "
                              "Go fetch. _Throws the cards on the floor:_\n\n")

        else:  # The normal mode - determine a random creature type
            creature_type = random.choice([
                "Horrors", "Kobolds", "Goblins", "Zombies", "Vampires", "Werewolves", "Legitimate Businesspeople",
                "Brushwaggs", "Camarids", "Giants", "Devils", "Hydras", "Krakens", "Nightmares", "Dragons",
                "Cyclopes", "Skeletons", "Dreadnoughts", "Wurms", "Leviathans",
            ])

            bot_reply_text = "The " + creature_type + " have delivered the cards you're looking for:\n\n"

        # Create links based on regex matches
        for index, regex_match in enumerate(regex_matches):

            # Rastamonliveup has special links
            rastamonliveup_info = rastamonliveup_name_link(regex_match)

            if rastamonliveup_info[0]:
                bot_reply_text += (
                    f'''[{rastamonliveup_info[0]}]'''
                    f'''({rastamonliveup_info[1]})\n\n'''
                )

            # Add the Scryfall link if the exact card name match exists
            elif scryfall_images[index]:
                bot_reply_text += (
                    f'''[{regex_match}]({random.choice(image_links)})'''
                    f''' - ([sf]({scryfall_images[index]}))\n\n'''
                )

                # Add a random flavour text (if only a single fetch)
                if random_flavour:
                    bot_reply_text += f'''_{random_flavour}_\n\n'''

            # In other cases add no special stuff, only a link to the joke card
            else:
                bot_reply_text += f'''[{regex_match}]({random.choice(image_links)})\n\n'''

                # Add a random flavour text (if only a single fetch)
                if random_flavour:
                    bot_reply_text += f'''_{random_flavour}_\n\n'''

    # Final line of text, always the same
    bot_reply_text += "*********\n\n^^^Submit ^^^your ^^^content ^^^at:\n\nr/MTGCardBelcher"

    return bot_reply_text


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
    for comment in comment_stream:
        try:
            if comment_requires_action(comment):
                comment_reply(comment, image_links)
        except AttributeError:  # No comments in stream results in None
            break


@main_error_handler
def submission_action(submission_stream, image_links: list):
    for submission in submission_stream:
        try:
            if submission_requires_action(submission):
                submission_reply(submission, image_links)
        except AttributeError:  # No comments in stream results in None
            break


# Setup, run only once
if __name__ == "__main__":
    print("Init...")

    # Create a text file (here oauth.txt) with five rows
    # or any other preferred method of delivering login info.
    # 1. Client id
    # 2. Secret
    # 3. Account password
    # 4. User Agent information
    # 5. Account username

    oauth = "oauth.txt"
    logs = "log.txt"
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
