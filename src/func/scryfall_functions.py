"""Functions that communicate with Scryfall."""

import requests

from src.func.base_logger import logger
from src.configs import BotInfo


def get_scryfall_image(cardname: str) -> list:
    """
    Fetches the image URL that matches the cardname.
    :param cardname: A card's name.
    :return: A list of image URLs if an exact match(es) is found,
    empty list if no match is found or Scryfall can't be reached.
    """
    try:
        # Special characters in names confuse the query so just ... get rid of those
        fixed_cardname = cardname.replace("&", "")
        fixed_cardname = fixed_cardname.replace("//", "")

        cardname_json = requests.get(url=f'https://api.scryfall.com/cards/named?exact={fixed_cardname}',
                                     headers=BotInfo.SCRYFALL_USER_AGENT_HEADER)
        if cardname_json:

            # If cardname JSON has content warning ignore it
            if cardname_json.json().get('content_warning'):
                image_url = []

            # Catch SFCs
            elif (cardname_json.json()['layout'] in
                  ['split', 'flip', 'meld', 'leveler', 'class', 'case', 'saga', 'adventure', 'prepare',
                   'mutate', 'prototype', 'battle', 'planar', 'scheme', 'vanguard', 'token',
                   'emblem', 'augment', 'host']):
                print(fixed_cardname, cardname_json.json()['layout'])
                image_url = [cardname_json.json()['image_uris']['normal']]

            # Catch DFCs
            elif (cardname_json.json()['layout'] in
                  ['transform', 'modal_dfc', 'double_faced_token', 'art_series', 'reversible_card']):
                print(fixed_cardname, cardname_json.json()['layout'])
                image_url = [cardname_json.json()['card_faces'][0]['image_uris']['normal'],
                             cardname_json.json()['card_faces'][1]['image_uris']['normal']]

            # Otherwise the card should be single sided
            elif cardname_json.json()['layout'] in ['normal']:
                image_url = [cardname_json.json()['image_uris']['normal']]

            # If there is an unknown layout return nothing
            else:
                image_url = []

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
