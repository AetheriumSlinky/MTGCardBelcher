"""Classes and functions that handle text formatting."""

import random
import re

from func.base_logger import logger
from func.timer import RefreshTimer
from data.dreadmaw import DreadmawObj
from data.rastamon_cards import RastamonCard, rastamon_list
import data.replies as replies
import func.scryfall_functions as sf


class BotReplyText:
    """
    A class to represent a bot reply text divided into text elements.
    """
    def __init__(self, header: str = "", body: str = "",
                 flavour: str = "", footer: str = ""):
        """
        Constructs the bot reply text object elements.
        :param header: Element that contains the entity delivering the cards.
        :param body: Element that contains the card links.
        :param flavour: Element that contains the optional flavour text.
        :param footer: Element that contains the standard footer text.
        """
        self.header = header
        self.body = body
        self.flavour = flavour
        self.footer = footer

    def __str__(self):
        return f"Attributes: {self.__dict__}"

    def body_add_text(self, text: str):
        """
        Adds / appends a text string to the body parameter.
        :param text: A string of text to be added to the text body parameter.
        """
        self.body += text


def get_regex_bracket_matches(text: str) -> list:
    """
    Regex searches for double square brackets (bot call) in text. Accommodates old/mobile/new Reddit.
    :param text: String to search.
    :return: A list of all matches.
    """
    browser_double_bracket_matches = re.findall(r'''\\\[\\\[([^\\\[\]]+)\\]\\]''', text)
    mobile_double_bracket_matches = re.findall(r'''\[\[([^\[\]]+)]]''', text)
    all_matches = browser_double_bracket_matches + mobile_double_bracket_matches  # Pray for no doubles
    return all_matches

def set_dreadmaw_waiting(reply_text: BotReplyText, cardname: str) -> BotReplyText:
    """
    Sets the bot reply text elements for the special Colossal Dreadmaw reply.
    """
    reply_text.header = "Colossal Dreadmaw is nowhere to be _seen_.\n\n"
    reply_text.body_add_text(f'''[{cardname}](https://i.redd.it/bvjzb0rfaike1.png)\n\n''')
    reply_text.flavour = "_You feel the ground quake. Run!_\n\n"
    return reply_text


def set_revel(reply_text: BotReplyText, cardname: str) -> BotReplyText:
    """
    Sets the bot reply text elements for the special Revel in Riches reply.
    """
    reply_text.body_add_text(f'''[{cardname}](https://i.redd.it/7jkequbnkrzd1.png)\n\n''')
    return reply_text


def set_negate(reply_text: BotReplyText, cardname: str) -> BotReplyText:
    """
    Sets the bot reply text elements for the special Negate reply.
    """
    reply_text.header = replies.negate_header
    reply_text.body_add_text(f'''[{cardname}](https://i.redd.it/ebgrvw7grwzd1.png)\n\n''')
    reply_text.flavour = replies.negate_flavour
    return reply_text


def set_rastamon(reply_text: BotReplyText, rastamon_card: RastamonCard) -> BotReplyText:
    """
    Sets the bot reply text elements for the special Rastamonliveup reply.
    """
    reply_text.header = replies.rastamon_header

    if rastamon_card.proper_name == "Kuka Beyo":
        reply_text.body_add_text(f'''[{rastamon_card.proper_name}]'''
                                 f'''({rastamon_card.image}) :)\n\n''')  # Override to add the smiley

    elif rastamon_card.proper_name == "Tell the children the truth":  # Triggered off of Galatians 4:16
        reply_text.body_add_text(f'''[*{rastamon_card.proper_name}*]'''  # Proper name is Sebi Gyandu flavour
                                 f'''({rastamon_card.image})\n\n''')  # Image links to Sebi Gyandu

    else:
        reply_text.body_add_text(f'''[{rastamon_card.proper_name}]'''  # Cardname with proper spelling
                                 f'''({rastamon_card.image})\n\n''')  # Card image

    if rastamon_card.proper_name == "Sebi Gyandu":
        reply_text.flavour = "_Tell the children the truth_\n\n"  # 'Tell the children the truth' flavour

    else:
        reply_text.flavour = "\n"

    return reply_text


def generate_reply_text(regex_matches: list, links: list) -> str:
    """
    Generates the text that the bot will attempt to reply with.
    :param regex_matches: The regex matches from a comment or a submission.
    :param links: A list of joke image link candidates.
    :return: Fully formatted reply text.
    """
    reply = BotReplyText()

    # Some overrides for Colossal Dreadmaw
    if DreadmawObj.call_name in [item.casefold() for item in regex_matches]:
        # Bypass the entire randomly generated procedure
        # and only print this particular response if Dreadmaw is mentioned even once
        choose_special = -1
        reply = set_dreadmaw_waiting(reply, "Colossal Dreadmaw")

    # Determines whether a regular reply is delivered or if one of the special modes is chosen instead
    else:
        choose_special = random.randint(0, 1001)

    if choose_special == 0:  # Text-only replies, no links
        reply.body = random.choice(replies.special_replies)
        logger.warning("Easter egg with no image links delivered. Please investigate reception.")

    elif choose_special == 1:  # Special delivery line, yes links
        reply.header = random.choice(replies.special_types)
        logger.info("Easter egg header reply delivered.")

    elif choose_special > 1:  # The normal mode - determine a random creature type
        reply.header = replies.random_creature_header(replies.generic_types)

    # If a reply with a header chosen add links and all
    if choose_special >= 1:

        # For each regex match loop de loop
        for cardname in regex_matches:
            scryfall_image = sf.get_scryfall_image(cardname)
            rastamon_card = RastamonCard.find_card(cardname, rastamon_list)

            # Some overrides for Revel in Riches
            if cardname.casefold() == "revel in riches":
                reply = set_revel(reply, cardname)

            # Some overrides for Negate copypasta / Has a day passed since last call?
            elif cardname.casefold() in replies.negate_spellings and negate_timer.single_timer():
                negate_timer.new_expiry_time(60 * 60 * 24)  # Set new expiry in a day from now
                reply = set_negate(reply, cardname)
                logger.info("Negate flavour used up for today. See you tomorrow!")

            # Some overrides for Rastamonliveup cards
            elif rastamon_card.proper_name:
                reply = set_rastamon(reply, rastamon_card)
                logger.info("Tell the children the truth.")

            # If a real cardname matches the regex make a Scryfall link
            elif scryfall_image:
                reply.body_add_text(f'''[{cardname}]({random.choice(links)})'''
                                    f''' - ([SF]({scryfall_image}))\n\n''')

            # No real cardname matches, no Scryfall link
            else:
                reply.body_add_text(f'''[{cardname}]({random.choice(links)})\n\n''')

        # If there is only a single card to fetch get a random flavour text from Scryfall
        # Also check if a flavour already exists from an override
        if len(regex_matches) == 1 and not reply.flavour:
            reply.flavour = f'''_{sf.get_scryfall_flavour()}_\n\n'''

    # Add the standard footer text
    reply.footer = "*********\n\nSubmit your content at: r/MTGCardBelcher"

    reply_text = f'''{reply.header}{reply.body}{reply.flavour}{reply.footer}'''

    return reply_text


# This timer is set for the Negate special flavour so that it's not called too often (once a day)
# Starts at 0 so that the reply is available immediately after each bot restart
negate_timer = RefreshTimer(0)

# This time is set for the special Colossal Dreasmaw text so that it's not called too often (variable cooldown)
# Starts at 0 so that the reply is available immediately after each bot restart.
dreadmaw_timer = RefreshTimer(0)
