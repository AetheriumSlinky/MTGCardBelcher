"""Classes and functions that handle text formatting."""

import random
import re

from src.configs import SpecialReplySettings
from src.func.base_logger import logger
from src.data.collectibles import ColossalDreadmaw, StormCrow, Negate
from src.data.rastamon_cards import Rastamon, RastamonCard
from src.data import replies
import src.func.scryfall_functions as sf


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
        Adds / appends a text string to the body attribute.
        :param text: A string of text to be added to the text body attribute.
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
    reply_text.header = replies.ReplyHeaders.DREADMAW_WAIT
    reply_text.body_add_text(f'''[{cardname}](https://i.redd.it/bvjzb0rfaike1.png)\n\n''')
    reply_text.flavour = replies.ReplyFlavours.DREADMAW_WAIT
    return reply_text


def set_stormcrow_waiting(reply_text: BotReplyText, cardname: str) -> BotReplyText:
    """
    Sets the bot reply text elements for the special Storm Crow reply.
    """
    reply_text.header = replies.ReplyHeaders.STORMCROW_WAIT
    reply_text.body_add_text(f'''[{cardname}](https://i.redd.it/ykxjrafd13te1.png)\n\n''')
    reply_text.flavour = replies.ReplyFlavours.STORMCROW_WAIT
    return reply_text


def set_negate_waiting(reply_text: BotReplyText, cardname: str) -> BotReplyText:
    """
    Sets the bot reply text elements for the special Negate reply.
    """
    reply_text.header = replies.ReplyHeaders.NEGATE_WAIT
    reply_text.body_add_text(f'''[{cardname}](https://i.redd.it/ebgrvw7grwzd1.png)\n\n''')
    reply_text.flavour = replies.ReplyFlavours.NEGATE_WAIT
    return reply_text


def set_revel_link_to_negate(reply_text: BotReplyText, cardname: str) -> BotReplyText:
    """
    Sets the bot reply text elements for the special Revel in Riches reply.
    """
    reply_text.body_add_text(f'''[{cardname}](https://i.redd.it/7jkequbnkrzd1.png)\n\n''')
    return reply_text


def set_rastamon(reply_text: BotReplyText, rastamon_card: RastamonCard) -> BotReplyText:
    """
    Sets the bot reply text elements for the special Rastamonliveup reply.
    """
    reply_text.header = replies.ReplyHeaders.RASTAMON

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
        reply_text.flavour = replies.ReplyFlavours.GYANDU  # 'Tell the children the truth' flavour

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
    if ([item.casefold() for item in regex_matches if item in ColossalDreadmaw.SPELLINGS]
            and SpecialReplySettings.NFT_REPLIES_ON):

        # Bypass everything, print this particular response if Dreadmaw is mentioned even once
        choose_special = -1
        reply = set_dreadmaw_waiting(reply, ColossalDreadmaw.NAME)
        logger.info(f"A waiting {ColossalDreadmaw.NAME} was delivered.")

    # Some overrides for Storm Crow
    elif ([item.casefold() for item in regex_matches if item in StormCrow.SPELLINGS]
          and SpecialReplySettings.NFT_REPLIES_ON):

        # Bypass everything, print this particular response if Storm Crow is mentioned even once
        choose_special = -1
        reply = set_stormcrow_waiting(reply, StormCrow.NAME)
        logger.info(f"A waiting {StormCrow.NAME} was delivered.")

    # Some overrides for Negate
    elif ([item.casefold() for item in regex_matches if item in Negate.SPELLINGS]
          and SpecialReplySettings.NFT_REPLIES_ON):

        # Bypass everything, print this particular response if Negate is mentioned even once
        choose_special = -1
        reply = set_negate_waiting(reply, Negate.NAME)
        logger.info(f"A waiting {Negate.NAME} was delivered.")

    # Determines whether a regular reply is delivered or if one of the special modes is chosen instead
    else:
        choose_special = random.randint(0, 1001)

    if choose_special == 0:  # Text-only replies, no links
        reply.body = replies.ReplyLinklessTexts.random_linkless_reply()
        logger.confirmation("Easter egg with no image links delivered. Please investigate reception. Link below.")

    elif choose_special == 1:  # Special delivery line, yes links
        reply.header = replies.ReplyHeaders.random_special_header()
        logger.info("Easter egg header reply delivered.")

    elif choose_special > 1:  # The normal mode - determine a random creature type
        reply.header = replies.ReplyHeaders.random_creature_header()

    # If a reply with a header chosen add links and all
    if choose_special >= 1:

        # For each regex match loop de loop
        for cardname in regex_matches:
            scryfall_image = sf.get_scryfall_image(cardname)
            rastamon_card = Rastamon.find_card(cardname)

            # Some overrides for Revel in Riches
            if cardname.casefold() == "revel in riches":
                reply = set_revel_link_to_negate(reply, cardname)

            # Some overrides for Rastamonliveup cards
            elif rastamon_card.proper_name:
                reply = set_rastamon(reply, rastamon_card)
                logger.info("Tell the children the truth. (A Rastamon reply was delivered.)")

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
