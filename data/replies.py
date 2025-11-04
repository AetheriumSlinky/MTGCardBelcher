"""Reply text strings."""

import random

class ReplyHeaders:
    """Header text strings."""

    RASTAMON = "Rastamonliveup has delivered the cards you're looking for:\n\n"
    DREADMAW_WAIT = "Colossal Dreadmaw is nowhere to be _seen_.\n\n"
    STORMCROW_WAIT = "The sky is clear! Not even a single cloud!\n\n"
    NEGATE_WAIT = "They resolve:\n\n"

    @staticmethod
    def random_special_header():
        """
        A random special header.
        :return: Header text string.
        """
        phyrexian = ("You find the cards you're looking for, "
                     "but they're covered in that strange oil... It's probably nothing.\n\n")

        licid = "The Licids have imprinted the cards you're looking for into your mind:\n\n"

        dreadmaw = "You feel the ground quake. You see the cards you're looking for, but it's too late.\n\n"

        yargle = ("The Frog Spirit had the cards... But it was hungry and ate them. "
                  "Worry not, it tells you what they were: 'Gnshhagghkkapphribbit'.\n\n")

        grumpy = ("You! Yes, you! I'm tired of your and your friends' crap. "
                  "Go fetch. _Throws the cards on the floor:_\n\n")

        gruul = "Gruul? Gruul!\n\n"

        specials = [phyrexian, licid, dreadmaw, yargle, grumpy, gruul]
        return random.choice(specials)

    @staticmethod
    def random_creature_header() -> str:
        """
        Constructs the standard random creature type header text string.
        :return: A header text string.
        """
        generic_creature_types = [
            "Horrors", "Kobolds", "Goblins", "Zombies", "Vampires", "Werewolves", "Legitimate Businesspeople",
            "Brushwaggs", "Camarids", "Giants", "Devils", "Hydras", "Krakens", "Nightmares", "Dragons",
            "Cyclopes", "Skeletons", "Dreadnoughts", "Wurms", "Leviathans",
        ]
        creature = random.choice(generic_creature_types)
        return f"The {creature} have delivered the cards you're looking for:\n\n"


class ReplyFlavours:
    """
    Flavour texts of certain special card calls.
    """
    GYANDU = "_Tell the children the truth_\n\n"
    DREADMAW_WAIT = "_You feel the ground quake. Run!_\n\n"
    STORMCROW_WAIT = "_It tells you that the worst is coming. Do you listen?_\n\n"
    NEGATE_WAIT = "_You must draw cards in order to counter Negate!_\n\n"

class ReplyLinklessTexts:
    """Full reply texts of linkless specials."""

    @staticmethod
    def random_linkless_reply():
        """
        A random special linkless reply text string.
        :return: Full reply text string.
        """
        eldrazi = ("The Invasion annihilated the cards you were looking for.\n\n"
                   "Nothing but ashes and pain remain. Somehow you survive.\n\n")

        orangutan = ("Instead of looking for any cards you stop to admire the marvels of nature:\n\n"
                     "[The Nature Is Wonderful](https://i.redd.it/cwhcrm1b74fd1.png)\n\n")

        meandering = ("Turns out bottled mail takes forever to arrive...\n\n"
                      "[You See a Messenger in the Distance](https://i.redd.it/tzcajj1wcjed1.jpeg)\n\n")

        specials = [eldrazi, orangutan, meandering]
        return random.choice(specials)
