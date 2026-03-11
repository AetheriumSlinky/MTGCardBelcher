"""Functions that communicate with Scryfall."""

import requests

from src.func.base_logger import logger
from src.configs import BotInfo


def get_scryfall_image(cardname: str) -> list:
    """
    Fetches the image URL that matches the cardname.
    :param cardname: Cardname.
    :return: Image URL if an exact match is found, empty string if no match is found or Scryfall can't be reached.
    """
    try:
        cardname_match = requests.get(url=f'https://api.scryfall.com/cards/named?exact={cardname}',
                                      headers=BotInfo.SCRYFALL_USER_AGENT_HEADER)
        if cardname_match:
            if cardname_match.json().get('content_warning'):  # Don't append the forbidden cards
                image_url = []
            elif 'card_faces' in cardname_match.json().keys():
                image_url = [cardname_match.json()['card_faces'][0]['image_uris']['normal'],
                             cardname_match.json()['card_faces'][1]['image_uris']['normal']]
            else:
                image_url = [cardname_match.json()['image_uris']['normal']]
        else:
            image_url = []

    # Lazy Except because Scryfall isn't that important, just skip this if it doesn't work
    except Exception as scryfall_e:
        image_url = []
        logger.info("Something went wrong with Scryfall. Ignoring Scryfall: " + str(scryfall_e))

    return image_url


def get_scryfall_flavour() -> str:
    """
    Fetches a random flavour text from Scryfall.
    :return: A random flavour text, a standard funny error text string if Scryfall can't be reached.
    """
    try:
        random_flavour_card = requests.get(url='https://api.scryfall.com/cards/random?q=has%3Aflavor',
                                           headers=BotInfo.SCRYFALL_USER_AGENT_HEADER)
        random_flavour = random_flavour_card.json()['flavor_text']
    # Lazy except because Scryfall isn't that important, just skip it if it doesn't work
    except Exception as scryfall_e:
        logger.info("Something went wrong with Scryfall. Ignoring Scryfall: " + str(scryfall_e))
        random_flavour = "Sometimes, rarely, Scryfall is not there and the world is out of flavour."

    return random_flavour
