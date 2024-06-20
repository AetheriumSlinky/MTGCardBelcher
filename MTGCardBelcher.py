import praw
import re
import time
import random
import sqlite3
import os
from tendo import singleton
import sys
import importlib

importlib.reload(sys)

conn = sqlite3.connect('state.sqlite')
cursor = conn.cursor()
persistence = True


def check_condition(comment_data):
    text = comment_data.body
    matches_in_comment = get_bracket_matches(text)
    comment_id = comment_data.id
    comment_author = str(comment_data.author)
    cursor.execute('SELECT comment_id FROM replied WHERE comment_id=?', (comment_data.id,))
    already_replied = cursor.fetchone()
    exclusions = 'Weekly /unjerk Thread'

    print(f"{comment_id} {comment_author} {already_replied} {matches_in_comment}")

    # don't reply twice and never reply to own comment to prevent possible loops
    if (matches_in_comment and already_replied is None and
            comment_data.author != 'MTGLardFetcher' and
            comment_data.link_title != exclusions):

        print("replying to unanswered comment " + comment_id)
        return matches_in_comment
    else:
        print("ignoring answered/uneligible comment " + comment_id)
        return False


def get_bracket_matches(text: str) -> list:
    double_bracket_matches = re.findall(r'\[\[([^\[\]]*?)\]\]', text)
    # matches = re.findall(r'\[\[(.*?)\]\]', text)
    return double_bracket_matches


def get_img_links(reddit) -> list:
    card_belcher = reddit.subreddit('MTGCardBelcher')
    img_candidates = ['https://www.reddit.com/media?url=https%3A%2F%2Fi.redd.it%2Ftwl36n1dil7d1.png']  # Pot of Greed
    for post in card_belcher.hot(limit=50):
        if "/r/MTGCardBelcher" not in post.url:
            if re.search('(i.redd.it|i.imgur.com)', post.url):
                img_candidates.append(post.url)
                print("found a valid post", post.url)
            else:
                print("not a valid post", post.url)

    return img_candidates


def bot_action(comment, text_matches, img_links, respond=False):

    creature_type = random.choice([
        "Horrors", "Kobolds", "Goblins", "Zombies", "Vampires"
    ])
    text = "The " + creature_type + " have found the cards you're looking for:\n\n"

    for match_str in text_matches:
        link = random.choice(img_links)
        text += "[" + match_str + "](" + link + ")\n"

    text += "\n\n*********\n\n"
    text += """^^^Submit ^^^your ^^^content ^^^at\nr/MTGCardBelcher"""

    if respond:
        try:
            comment.reply(text)
        except praw.exceptions.RedditAPIException:
            print("TOO_OLD or some other crap, going on")
        finally:
            cursor.execute('insert into replied (comment_id) values (?)', comment.id)
            conn.commit()


if __name__ == '__main__':

    me = singleton.SingleInstance()

    cursor.execute('''CREATE TABLE IF NOT EXISTS replied (comment_id text)''')
    conn.commit()

    UA = ('MTGCardBelcher, a MTGCardFetcher Parody bot for /r/magicthecirclejerking.'
          'Kindly direct complaints to /u/MustaKotka')

    r = praw.Reddit(
        user_agent=UA,
        client_id=os.getenv('CLIENT_ID'),
        client_secret=os.getenv('CLIENT_SECRET'),
        refresh_token=os.getenv('REFRESH_TOKEN')
    )

    last_refresh = int(time.time())
    links = get_img_links(r)
    target = 'magicthecirclejerking'

    for mtcj_comment in r.subreddit(target).stream.comments():
        matches = check_condition(mtcj_comment)
        if matches:
            now = int(time.time())
            if now - last_refresh > 60:
                links = get_img_links(r)
                last_refresh = now

            bot_action(mtcj_comment, matches, links, True)

    conn.close()
