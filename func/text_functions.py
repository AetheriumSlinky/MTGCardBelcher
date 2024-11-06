"""Classes and functions that handle text formatting."""

import random
import re

from func.base_logger import logger
import data.creature_replies as creature_replies
import data.rastamon_cards as rastamon
import func.scryfall_functions as sf


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


def rastamon_card_name_and_link(name: str) -> tuple:
    """
    Provided with a suspected Rastamonliveup card name,
    it finds the corresponding proper name and link to the card image.
    :param name: A suspected card name, probably from a regex match.
    :return: A tuple(proper name, link to card image).
    """

    # If a match is found return proper name and link to card image
    for creature in rastamon.cards:
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
        reply.body = creature_replies.eldrazi
        logger.info("Easter egg Eldrazi Annihilation delivered.")

    elif choose_special == 0:  # Special shagging monkes, static image link only
        reply.body = creature_replies.orangutan
        logger.info("Easter egg Uktabi Orangutan delivered.")

    elif choose_special == 1:  # Special phyrexian oil
        reply.header = creature_replies.phyrexian
        logger.info("Easter egg Phyrexian oil delivered.")

    elif choose_special == 2:  # Special licid mind injection
        reply.header = creature_replies.licid
        logger.info("Easter egg Licids delivered.")

    elif choose_special == 3:  # Special Dreadmaw
        reply.header = creature_replies.dreadmaw
        logger.info("Easter egg Colossal Dreadmaw delivered.")

    elif choose_special == 4:  # Special hungery Yargle
        reply.header = creature_replies.yargle
        logger.info("Easter egg Yargle delivered.")

    elif choose_special == 5:  # Special grumpy bot
        reply.header = creature_replies.grumpy
        logger.info("Easter egg 'Sod Off' delivered.")

    else:  # The normal mode - determine a random creature type
        reply.header = creature_replies.generic_creature

    # If there is only a single card to fetch get a random flavour text from Scryfall
    if len(regex_matches) == 1:
        reply.flavour = f'''_{sf.get_scryfall_flavour()}_\n\n'''

    # If neither no-card links special mode was chosen execute normal mode
    if choose_special >= 1:

        # Attempt to fetch regex matches and associated exact card name match from Scryfall
        for cardname in regex_matches:
            scryfall_image = sf.get_scryfall_image(cardname)
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
