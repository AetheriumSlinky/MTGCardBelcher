import praw
import praw.exceptions
import re
import time
import random

# MTGCardBelcher v1.0.0 by /u/MustaKotka (AetheriumSlinky)


def get_regex_bracket_matches(text: str) -> list:
    """
    Regex searches for double square brackets (bot call) in text.
    :param text: Text to search.
    :return: A list of all matches.
    """
    browser_double_bracket_matches = re.findall(r'''\\\[\\\[([^\\\[\]]+)\\]\\]''', text)
    mobile_double_bracket_matches = re.findall(r'''\[\[([^\[\]]+)]]''', text)
    all_matches = browser_double_bracket_matches + mobile_double_bracket_matches

    return all_matches


def get_image_links(reddit: praw.Reddit) -> list:
    """
    Searches target CardBelcher subreddit for image links.
    :param reddit: Reddit.
    :return: A list of image candidate links.
    """
    card_belcher = reddit.subreddit('MTGCardBelcher')
    image_candidates = ['https://i.redd.it/pcmd6d3o1oad1.png']  # Jollyver is always an option - RIP LardFetcher
    for image_submissions in card_belcher.new(limit=97):  # Don't hit rate limits
        if "/r/MTGCardBelcher" not in image_submissions.url:
            if (re.search('(i.redd.it|i.imgur.com)', image_submissions.url)
                    and image_submissions.link_flair_text == "Card Submission"):
                image_candidates.append(image_submissions.url)
    return image_candidates


def generate_reply_text(reply_text_string: str, image_links: list) -> str:

    choose_special = random.randint(-5, 100)

    if choose_special == 0:  # Special Eldrazi no image card links
        bot_reply_text = (
            "The Invasion annihilated the cards you were looking for.\n\n"
            "Nothing but ashes and pain remain. Somehow you survive.\n\n"
        )

    elif choose_special == -1:  # Special shagging monkes
        bot_reply_text = (
            "Instead of looking for any cards you stop to admire the marvels of nature:\n\n"
            "[The Nature Is Wonderful]"
            "(https://cards.scryfall.io/large/front/1/0/101c7d58-43cc-4ebd-87f1-2016fbff56dd.jpg?1562276965)\n\n"
        )

    else:
        text_matches = get_regex_bracket_matches(reply_text_string)

        if choose_special == -2:  # Special phyrexian oil
            bot_reply_text = ("You find the cards you're looking for, "
                              "but they're covered in that strange oil... It's probably nothing.\n\n")

        elif choose_special == -3:  # Special licid mind injection
            bot_reply_text = "The Licids have imprinted the cards you're looking for into your mind:\n\n"

        elif choose_special == -4:  # Special Dreadmaw
            bot_reply_text = "You feel the ground quake. You see the cards you're looking for, but it's too late.\n\n"

        elif choose_special == -5:  # Special hungy Yargle
            bot_reply_text = ("The Frog Spirit tried to give you the cards... But it was so hungry that it ate them. "
                              "It tells you what they were, though: 'Gnshhagghkkapphribbit'\n\n")

        else:
            creature_type = random.choice([
                "Horrors", "Kobolds", "Goblins", "Zombies", "Vampires", "Werewolves", "Legitimate Businesspeople",
                "Brushwaggs", "Camarids", "Giants", "Devils", "Hydras", "Krakens", "Nightmares", "Dragons",
                "Cyclopses", "Skeletons", "Dreadnoughts", "Wurms", "Leviathans",
            ])

            bot_reply_text = "The " + creature_type + " have delivered the cards you're looking for:\n\n"

        for match_text_string in text_matches:
            bot_reply_text += "[" + match_text_string + "](" + random.choice(image_links) + ")\n\n"

    bot_reply_text += "*********\n\n^^^Submit ^^^your ^^^content ^^^at:\n\nr/MTGCardBelcher"

    return bot_reply_text


def comment_requires_action(comment_data: praw.Reddit.comment) -> bool:
    """
    Checks whether a comment has been replied to already or is excluded.
    :param comment_data: Reddit's praw comment api data.
    :return: True if comment requires action.
    """
    comment_double_bracket_matches: list = get_regex_bracket_matches(comment_data.body)
    submission_exclusions = [
        # Weekly unjerk
        re.search(r'.*unjerk.*thread.*', string=comment_data.submission.title, flags=re.IGNORECASE)
    ]

    if comment_data.author.name == ('MTGCardBelcher' or 'MTGCardFetcher'):
        print("Bot will not reply to itself or to the real CardFetcher (comment). " + comment_data.permalink)
        return False
    elif not comment_double_bracket_matches:
        print("No matches in comment. " + comment_data.permalink)
        return False
    elif None not in submission_exclusions:
        print("Parent submission of the comment on exclusion list. " + comment_data.permalink)
        return False
    else:
        print(
            "Should reply to eligible comment (" + str(comment_double_bracket_matches) + "): "
            + comment_data.permalink
        )
        return True


def submission_requires_action(submission_data: praw.Reddit.submission) -> bool:
    """
    Checks whether a submission has been replied to already or is excluded.
    :param submission_data: Reddit's praw submission api data.
    :return: True if submission requires action.
    """
    submission_double_bracket_matches = get_regex_bracket_matches(submission_data.selftext)
    submission_exclusions = [
        # Weekly unjerk
        re.search(r'.*unjerk.*thread.*', string=submission_data.title, flags=re.IGNORECASE),
        # Bottom scoring submissions
        re.search(r'.*bottom.*scoring.*', string=submission_data.title, flags=re.IGNORECASE),
    ]

    if submission_data.author.name == ("MTGCardBelcher" or "MTGCardFetcher"):
        print("Bot will not reply to itself or to the real CardFetcher (submission). " + submission_data.permalink)
        return False
    elif not submission_double_bracket_matches:
        print("No matches in submission. " + submission_data.permalink)
        return False
    elif None not in submission_exclusions:
        print("Submission on exclusion list. " + submission_data.permalink)
        return False
    else:
        print(
            "Should reply to eligible post (" + str(submission_double_bracket_matches) + "): "
            + submission_data.permalink
        )
        return True


def bot_comment_reply_action(
        comment_data: praw.Reddit.comment,
        image_links: list):
    """
    Executes the reply action in an eligible comment.
    :param comment_data: Comment to reply to.
    :param image_links: A list of image candidate links.
    """
    reply_text = generate_reply_text(comment_data.body, image_links)
    try:
        comment.reply(reply_text)
        print("Comment reply successful: " + comment_data.id)
    except praw.exceptions.RedditAPIException as e:
        print("Failed to reply to comment because Reddit has a problem: " + str(e))


def bot_submission_reply_action(
        submission_data: praw.Reddit.submission,
        image_links: list):
    """
    Executes the reply action in an eligible submission.
    :param submission_data: Submission to reply to.
    :param image_links: A list of image candidate links.
    """
    reply_text = generate_reply_text(submission_data.selftext, image_links)
    try:
        submission.reply(reply_text)
        print("Post reply successful: " + submission_data.id)
    except praw.exceptions.RedditAPIException as e:
        print("Failed to reply to post because Reddit has a problem: " + str(e))


if __name__ == "__main__":
    print("Init...")

    with open("oauth.txt", "r") as oauth_file:
        info = oauth_file.read().splitlines()

# Create a text file (here oauth.txt) with five rows:
    # Client id
    # Secret
    # Account password
    # User Agent information
    # Account username

    r = praw.Reddit(
        client_id=info[0],
        client_secret=info[1],
        password=info[2],
        user_agent=info[3],
        username=info[4]
    )

    image_submission_links = get_image_links(r)
    image_refresh_timer = round(time.time())
    target = "magicthecirclejerking"
    mtcj_comments = r.subreddit(target).stream.comments(skip_existing=True, pause_after=2)
    mtcj_submissions = r.subreddit(target).stream.submissions(skip_existing=True, pause_after=2)

    print("...init complete.")

    # Main loop
    while True:

        if round(time.time()) - image_refresh_timer > 120:
            image_refresh_timer = round(time.time())
            image_submission_links = get_image_links(r)
            print("Found " + str(len(image_submission_links)) + " valid image submissions.")

        for comment in mtcj_comments:
            try:
                if comment_requires_action(comment):
                    bot_comment_reply_action(comment, image_submission_links)
                    print("Eligible comment reply finished.")
            except AttributeError:  # No comments in stream results in None
                break
            except praw.exceptions.RedditAPIException:
                print("Reddit is experiencing problems (comments).")
                break

        for submission in mtcj_submissions:
            try:
                if submission_requires_action(submission):
                    bot_submission_reply_action(submission, image_submission_links)
                    print("Eligible submission reply finished.")
            except AttributeError:  # No submissions in stream results in None
                break
            except praw.exceptions.RedditAPIException:
                print("Reddit is experiencing problems (submissions).")  # Does this bit work??
                break

        time.sleep(0.1)
