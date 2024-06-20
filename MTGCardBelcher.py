import praw
import praw.exceptions
import re
import time
import random

with open("", "r") as oauth_file:
    info = oauth_file.read().splitlines()

UA = "MTGCardBelcher v1.0.0 by /u/MustaKotka (AetheriumSlinky)"

r = praw.Reddit(
    client_id=info[0],
    client_secret=info[1],
    password=info[2],
    user_agent=UA,
    username=info[3]
)


def comment_requires_action(comment_data: praw.Reddit.comment) -> bool:
    """
    Checks whether a comment has been replied to already or is excluded.
    :param comment_data: Reddit's praw comment api data.
    :return: True if comment requires action.
    """
    comment_double_bracket_matches = get_bracket_matches(comment_data.body)
    submission_exclusions = [
        # Weekly unjerk
        re.search(r'.*unjerk.*thread.*', string=comment_data.body, flags=re.IGNORECASE)
    ]

    if comment_double_bracket_matches is None:
        print("No double bracket matches (comment). " + comment_data.id)
        return False
    elif comment_data.author == 'MTGCardBelcher' or 'MTGCardFetcher':
        print("Bot will not reply to itself or to the real CardFetcher (comment). " + comment_data.id)
        return False
    elif comment_data.submission.title in submission_exclusions:
        print("Submission of the comment on exclusion list. " + comment_data.id)
        return False
    else:
        print("Should reply to eligible comment: " + comment_data.id)
        return True


def submission_requires_action(submission_data: praw.Reddit.submission) -> bool:
    """
    Checks whether a submission has been replied to already or is excluded.
    :param submission_data: Reddit's praw submission api data.
    :return: True if submission requires action.
    """
    submission_double_bracket_match = get_bracket_matches(submission_data.selftext)
    submission_exclusions = [
        # Weekly unjerk
        re.search(r'.*unjerk.*thread.*', string=submission_data.selftext, flags=re.IGNORECASE),
        # Bottom scoring submissions
        re.search(r'.*bottom.*scoring.*', string=submission_data.selftext, flags=re.IGNORECASE),
    ]

    if submission_double_bracket_match is None:
        print("No double bracket matches (submission). " + submission_data.id)
        return False
    elif submission_data.author == 'MTGCardBelcher' or 'MTGCardFetcher':
        print("Bot will not reply to itself or to the real CardFetcher (submission). " + submission_data.id)
        return False
    elif submission_data.title is submission_exclusions:
        print("Submission on exclusion list. " + submission_data.id)
        return False
    else:
        print("Should reply to eligible post: " + submission_data.id)
        return True


def get_bracket_matches(text: str) -> list:
    """
    Regex searches for double square brackets (bot call) in text.
    :param text: Text to search.
    :return: A list of all matches.
    """
    double_bracket_matches = re.findall(r'\[\[([^\[\]]*?)]]', text)
    return double_bracket_matches


def get_image_links(reddit: praw.Reddit) -> list:
    """
    Searches target CardBelcher subreddit for image links.
    :param reddit: Reddit.
    :return: A list of image candidate links.
    """
    card_belcher = reddit.subreddit('MTGCardBelcher')
    img_candidates = ['https://www.reddit.com/media?url=https%3A%2F%2Fi.redd.it%2Ftwl36n1dil7d1.png']  # Pot of Greed
    for image_submissions in card_belcher.hot(limit=50):
        if "/r/MTGCardBelcher" not in image_submissions.url:
            if re.search('(i.redd.it|i.imgur.com)' and image_submissions.link_flair_text == "Card Submission",
                         image_submissions.url):
                img_candidates.append(image_submissions.url)
                print("Valid image submission: ", image_submissions.url)
            else:
                print("Invalid submission: ", image_submissions.url)
    return img_candidates


def bot_comment_action(
        comment: praw.Reddit.comment,
        image_links: list):
    """
    Executes the reply action in an eligible comment.
    :param comment: Comment to reply to.
    :param image_links: A list of image candidate links.
    """
    creature_type = random.choice([
        "Horrors", "Kobolds", "Goblins", "Zombies", "Vampires", "Cephalids"
    ])
    bot_reply_text = "The " + creature_type + " have found the cards you're looking for:\n\n"

    text_matches = get_bracket_matches(comment.body)

    for match_str in text_matches:
        img_link = random.choice(image_links)
        bot_reply_text += "[" + match_str + "](" + img_link + ")\n"
    bot_reply_text += "\n*********\n\n^^^Submit ^^^your ^^^content ^^^at:\n\nr/MTGCardBelcher"

    try:
        comment.reply(bot_reply_text)
    except praw.exceptions.RedditAPIException:
        print("Failed to reply to comment: " + comment.id)


def bot_submission_action(
        submission: praw.Reddit.submission,
        image_links: list):
    """
    Executes the reply action in an eligible submission.
    :param submission: Submission to reply to.
    :param image_links: A list of image candidate links.
    """
    creature_type = random.choice([
        "Horrors", "Kobolds", "Goblins", "Zombies", "Vampires", "Cephalids"
    ])
    bot_reply_text = "The " + creature_type + " have found the cards you're looking for:\n\n"

    text_matches = get_bracket_matches(submission.selftext)

    for match_str in text_matches:
        img_link = random.choice(image_links)
        bot_reply_text += "[" + match_str + "](" + img_link + ")\n"
    bot_reply_text += "\n*********\n\n^^^Submit ^^^your ^^^content ^^^at:\n\nr/MTGCardBelcher"

    try:
        submission.reply(bot_reply_text)
    except praw.exceptions.RedditAPIException:
        print("Failed to reply to submission: " + submission.id)


target = "magicthecirclejerking"
img_links = get_image_links(r)


# Main loop
while True:
    image_refresh_timer = time.time()

    if time.time() - image_refresh_timer > 58:
        img_links = get_image_links(r)

    for mtcj_comment in r.subreddit(target).stream.comments(skip_existing=True):
        if comment_requires_action(mtcj_comment):
            bot_comment_action(mtcj_comment, img_links)

    for mtcj_submission in r.subreddit(target).stream.submissions(skip_existing=True):
        if submission_requires_action(mtcj_submission):
            bot_submission_action(mtcj_submission, img_links)

    time.sleep(10)
