"""Creature delivery text strings."""

import random


def random_creature(creatures: list) -> str:
    """
    Picks a random creature type to deliver the cards text string.
    :param creatures: A list of generic creature types.
    :return: A single random creature type delivery text string.
    """
    creature = random.choice(creatures)
    text = f"The {creature} have delivered the cards you're looking for:\n\n"
    return text


eldrazi = ("The Invasion annihilated the cards you were looking for.\n\n"
           "Nothing but ashes and pain remain. Somehow you survive.\n\n")

orangutan = ("Instead of looking for any cards you stop to admire the marvels of nature:\n\n"
             "[The Nature Is Wonderful](https://i.redd.it/cwhcrm1b74fd1.png)\n\n")

phyrexian = ("You find the cards you're looking for, "
             "but they're covered in that strange oil... It's probably nothing.\n\n")

licid = "The Licids have imprinted the cards you're looking for into your mind:\n\n"

dreadmaw = "You feel the ground quake. You see the cards you're looking for, but it's too late.\n\n"

yargle = ("The Frog Spirit had the cards... But it was hungry and ate them. "
          "Worry not, it tells you what they were: 'Gnshhagghkkapphribbit'.\n\n")

grumpy = ("You! Yes, you! I'm tired of your and your friends' crap. "
          "Go fetch. _Throws the cards on the floor:_\n\n")

generic_creature_types = [
    "Horrors", "Kobolds", "Goblins", "Zombies", "Vampires", "Werewolves", "Legitimate Businesspeople",
    "Brushwaggs", "Camarids", "Giants", "Devils", "Hydras", "Krakens", "Nightmares", "Dragons",
    "Cyclopes", "Skeletons", "Dreadnoughts", "Wurms", "Leviathans",
]

generic_creature = random_creature(generic_creature_types)
