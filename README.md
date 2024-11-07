# What is this?

A joke bot for Reddit. See [/r/MTGCardBelcher](https://www.reddit.com/r/MTGCardBelcher/)
and the target audience [/r/magicthecirclejerking](https://www.reddit.com/r/magicthecirclejerking/).

RIP [original /u/MTGLardFetcher](https://github.com/MTGLardFetcher/MTGLardFetcher) :(

# Features

- Regex matches double bracketed strings in posts and comments on a chosen subreddit.
- Replies with a random image post from another chosen subreddit.
- Adds a Scryfall card image link if linked card name exact matches a real card name.
- Adds a random Scryfall flavour text if there is only one card to link.
- Links to u/Rastamonliveup's r/custommagic cards when called by exact name instead of a random card.
- Ignores certain posts/comments in the chosen subbreddit (and itself).
- Tries to restore connection to Reddit if Reddit is experiencing internal problems.
- Logs info and errors.

# Requirements

Written in Python 3.12 and uses the 7.8.1 version of the [PRAW module](https://praw.readthedocs.io/en/stable/).

See requirements.txt for further information.

# How do I run it

    Create a text file containing your authentication information,
    each item separated by a line break.
        Client ID
        Secret
        Bot account password
        Bot user agent text
        Bot username

    Replace "oauth.txt" in /data/configs.py with your text file.

    Run:
    python MTGCardBelcher.py 
