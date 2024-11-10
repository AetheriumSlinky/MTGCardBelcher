"""Creature delivery text strings."""

import random


def random_creature_header(creatures: list) -> str:
    """
    Constructs the standard random creature type header text string.
    :param creatures: A list of generic creature types.
    :return: A single random creature type delivery text string.
    """
    creature = random.choice(creatures)
    text = f"The {creature} have delivered the cards you're looking for:\n\n"
    return text


# Special Rastamonliveup header
rastamon_header = "Rastamonliveup has delivered the cards you're looking for:\n\n"

# Special Negate header
negate_header = "Desolatormagic is fuming at you and your stupid cards:\n\n"

# Special Negate flavour
negate_flavour = (
    "_Before this gets deleted by reddit admins, this asshole took it completely out of context. "
    "First of all, the idiot thinks it was a marionette deck. It wasn't. That card's not even in the deck. "
    "He was running counterspell draw, this was approximately turn 25, "
    "every single creature and spell I cast was countered or removed up until that point "
    "and this dumbass who copied his deck from MTG Salvation or Goldfish used one of his last copies of negate "
    "to counter a Revel in Riches when he had 0 creatures on the field and I had 0 treasures in play, "
    "thus the 'this spell does literally nothing' and he should have let it resolve. "
    "I love it when people copy a deck and have no idea how to run it or play MTG. "
    "I was just throwing it out because I had 5 mana and it was the only card left in my hand "
    "and the game was already over anyway. "
    "So on the way out I let him know what an idiot he was for countering a spell "
    "that does nothing in the current board state. "
    "NOBODY wants to watch a recording of a game where I cast something "
    "and he counters it or removes it x30 turns. That's idiotic. "
    "I should have left the game the second I saw what he was running. "
    "This was the 5th attempt at getting a recording of something resembling watchable MTG gameplay "
    "and 5 people in a row were playing Karn draw control loop "
    "or free cast torrential graveyard resurrection control or approach control loop. "
    "So yeah, I was pissed and he was an asshole for playing this. "
    "He's one of those idiots who doesn't care about the other players one bit, it's all about winning. "
    "So running 35 control spells seems reasonable because NOTHING matters but winning. "
    "Thanks for not showing the board state with library counts or the full log, asshole. "
    "Enjoy your temporary ban from reddit._\n\n"
)


# Special no links replies (body)

eldrazi = ("The Invasion annihilated the cards you were looking for.\n\n"
           "Nothing but ashes and pain remain. Somehow you survive.\n\n")

orangutan = ("Instead of looking for any cards you stop to admire the marvels of nature:\n\n"
             "[The Nature Is Wonderful](https://i.redd.it/cwhcrm1b74fd1.png)\n\n")

meandering = ("Turns out bottled mail takes forever to arrive...\n\n"
              "[You See a Messenger in the Distance](https://i.redd.it/tzcajj1wcjed1.jpeg)\n\n")

# List of special no links replies
special_replies = [eldrazi, orangutan, meandering,]

# Special headers

phyrexian = ("You find the cards you're looking for, "
             "but they're covered in that strange oil... It's probably nothing.\n\n")

licid = "The Licids have imprinted the cards you're looking for into your mind:\n\n"

dreadmaw = "You feel the ground quake. You see the cards you're looking for, but it's too late.\n\n"

yargle = ("The Frog Spirit had the cards... But it was hungry and ate them. "
          "Worry not, it tells you what they were: 'Gnshhagghkkapphribbit'.\n\n")

grumpy = ("You! Yes, you! I'm tired of your and your friends' crap. "
          "Go fetch. _Throws the cards on the floor:_\n\n")

gruul = "Gruul? Gruul!\n\n"

# List of special headers
special_types = [phyrexian, licid, dreadmaw, yargle, grumpy, gruul,]

# Generic header creature types
generic_types = [
    "Horrors", "Kobolds", "Goblins", "Zombies", "Vampires", "Werewolves", "Legitimate Businesspeople",
    "Brushwaggs", "Camarids", "Giants", "Devils", "Hydras", "Krakens", "Nightmares", "Dragons",
    "Cyclopes", "Skeletons", "Dreadnoughts", "Wurms", "Leviathans",
]

