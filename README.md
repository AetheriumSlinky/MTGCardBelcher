# What is this?

A joke bot for Reddit. See [/r/MTGCardBelcher](https://www.reddit.com/r/MTGCardBelcher/)
and the target audience [/r/magicthecirclejerking](https://www.reddit.com/r/magicthecirclejerking/).

# Features

- Regex matches double bracketed strings in posts and comments on a chosen subreddit.
- Replies with a random image post from another chosen subreddit.
- Ignores certain posts/comments in the chosen subbreddit (and itself).

# Requirements

Written in Python 3.12 and uses the 7.7.1 version of the [PRAW module](https://praw.readthedocs.io/en/stable/).

See requirements.txt for further information.

# How do I run it

    Create a text file containing your authentication information,
    each item separated by a line break.
        Client ID
        Secret
        Bot account password
        Bot user agent text
        Bot username

    Replace "oauth.txt" with your text file.

    Run:
    python MTGCardBelcher.py 
