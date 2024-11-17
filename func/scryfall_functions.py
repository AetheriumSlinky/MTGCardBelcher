"""Functions that communicate with Scryfall."""

import requests

from func.base_logger import logger
from data.configs import sf_headers


def get_scryfall_image(cardname: str) -> str:
    """
    Fetches the image URL that matches the cardname.
    :param cardname: Cardname.
    :return: Image URL if an exact match is found, empty string if no match is found or Scryfall can't be reached.
    """
    try:
        cardname_match = requests.get(url=f'https://api.scryfall.com/cards/named?exact={cardname}',
                                      headers=sf_headers)
        if cardname_match:
            if cardname_match.json().get('content_warning'):  # Don't append the forbidden cards
                image_url = ""
            else:
                image_url = cardname_match.json()['image_uris']['normal']
        else:
            image_url = ""

    # Lazy Except because Scryfall isn't that important, just skip this if it doesn't work
    except Exception as scryfall_e:
        image_url = ""
        logger.warning("Something went wrong with Scryfall. Ignoring Scryfall: " + str(scryfall_e))

    return image_url


def get_scryfall_flavour() -> str:
    """
    Fetches a random flavour text from Scryfall.
    :return: A random flavour text, a standard funny error text string if Scryfall can't be reached.
    """
    try:
        random_flavour_card = requests.get(url='https://api.scryfall.com/cards/random?q=has%3Aflavor',
                                           headers=sf_headers)
        random_flavour = random_flavour_card.json()['flavor_text']
    # Lazy except because Scryfall isn't that important, just skip it if it doesn't work
    except Exception as scryfall_e:
        logger.warning("Something went wrong with Scryfall. Ignoring Scryfall: " + str(scryfall_e))
        random_flavour = "Sometimes, rarely, Scryfall is not there and the world is out of flavour."

    return random_flavour
