"""Colossal Dreadmaw special."""
import random

import praw

from func.timer import RefreshTimer
from data.configs import SpecialReplySettings


class CollectiblesTemplate:
    """
    Collectible card parent class.
    """

    def __init__(self, reddit: praw.Reddit | None):
        self.reddit = reddit
        self.timer = RefreshTimer(0, stopped=True)
        self.name = ""
        self.spellings = []

    def _previous_count(self, count_comment_id: str) -> int:
        """
        Fetches the current Dreadmaw call count from Reddit.
        :return: Number of times Dreadmaw has been called.
        """
        number = int(self.reddit.comment(count_comment_id).body)
        return number

    def _counter_comment_new_count(self, new_count: int, count_comment_id: str):
        """
        Edits the post on Reddit that contains Dreadmaw's call count and updates the count.
        """
        self.reddit.comment(count_comment_id).edit(str(new_count))

    def _new_response_delay(self):
        """
        Sets a new, random timer delay.
        """
        self.timer.new_expiry_time(random.randint(SpecialReplySettings.REPLY_MIN_TIMER,
                                                  SpecialReplySettings.REPLY_MAX_TIMER))

    def _reddit_counter_actions(self, counter_comment_id: str):
        """
        Increments the comment that keeps track of the number of calls made to an art. Updates a new, random delay.
        :param counter_comment_id: Reddit comment ID.
        :return: A new count as a string.
        """
        prev_count = self._previous_count(counter_comment_id)
        new_count = prev_count + 1
        self._counter_comment_new_count(new_count, counter_comment_id)
        self._new_response_delay()
        new_count_str = self._count_to_str(new_count)
        return new_count_str

    @staticmethod
    def _count_to_str(count) -> str:
        """
        Formats the number of calls into a string with a suitable number of characters.
        Raises ValueError if the number exceeds 9999.
        :param count: Number of times a call to the collectible has been made.
        :return: A string from an int with exactly four characters, filled with leading zeros.
        """
        if count < 10:
            return "000" + str(count)
        elif 10 <= count < 100:
            return "00" + str(count)
        elif 100 <= count < 1000:
            return "0" + str(count)
        elif 1000 <= count < 10000:
            return str(count)
        else:
            raise ValueError("Collector number has too many digits.")


class ColossalDreadmaw(CollectiblesTemplate):
    """
    Colossal Dreadmaw ASCII art object with the number of calls made to it.
    """
    NAME = "Colossal Dreadmaw"
    SPELLINGS = ["colossal dreadmaw"]
    COUNT_COMMENT_ID = "me0tbmp"

    def __init__(self, reddit: praw.Reddit):
        super().__init__(reddit)
        self.name = self.NAME
        self.spellings = self.SPELLINGS
        self.timer.stopped = False

    def art(self) -> str:
        """
        Fetches call count, updates it and returns ASCII art with a new collector number.
        :return: ASCII art.
        """
        art_counter_str = self._reddit_counter_actions(self.COUNT_COMMENT_ID)
        dreadmaw_art = self.__ascii_template(art_counter_str)
        return dreadmaw_art

    @staticmethod
    def __ascii_template(count_str) -> str:
        """
        The ASCII art associated with Colossal Dreadmaw.
        :param count_str: Number of times the bot has been called for Colossal Dreadmaw.
        :return: The art.
        """
        art = (f'''
     ______________________________
    /                              \\
    | Colossal Dreadmaw  (4)(Ψ)(Ψ) |
    |.____________________________.|
    ||  /    ______/_/|/^>>  \\    ||
    || |    /     o  ,    >>  \\   ||
    || |    \\WWW   _/| ,_>>    \\  ||
    ||/        \\__// |/|  \\___/V  ||
    ||            /  / |,  V/ \\   ||
    ||\\          /__/__/|      \\  ||
    ||_\\__________(____)________|_||
    | (Creature ── Dinosaur   M19) |
    |                              |
    |                              |
    | Trample                      |
    |                              |
    |                              |
    | You see its teeth.           |
    | It's too late.               |
    |                      / 6 /  \\|
    | #{count_str} C              \\  / 6 /|
    | M19•EN  ==>Jesper Ejsing     |
    \\______________________________/\n\n
*^(You are No. {count_str}! This content is best viewed by opening this reply directly.)*\n\n''')
        return art


class StormCrow(CollectiblesTemplate):
    """
    Storm Crow ASCII art object with the number of calls made to it.
    """
    NAME = "Storm Crow"
    SPELLINGS = ["storm crow"]
    COUNT_COMMENT_ID = "mlnqxci"

    def __init__(self, reddit: praw.Reddit):
        super().__init__(reddit)
        self.name = self.NAME
        self.spellings = self.SPELLINGS
        self.timer.stopped = False

    def art(self) -> str:
        """
        Fetches call count, updates it and returns ASCII art with a new collector number.
        :return: ASCII art.
        """
        art_counter_str = self._reddit_counter_actions(self.COUNT_COMMENT_ID)
        stormcrow_art = self.__ascii_template(art_counter_str)
        return stormcrow_art

    @staticmethod
    def __ascii_template(count_str):
        """
        The ASCII art associated with Storm Crow.
        :param count_str: Number of times the bot has been called for Storm Crow.
        :return: The art.
        """
        art = (f"""
     ______________________________
    /                              \\
    | Storm Crow            (1)(ô) |
    |.____________________________.|
    ||                ,-`'´.      ||
    ||               /    .'      ||
    ||    '--....__ /____/_       ||
    ||     ``''''>__)    _°Ì>     ||
    ||     ..-''´ __..--´         ||
    ||    ´´´´ ```^^              ||
    ||____________________________||
    | (Creature ── Bird)        \\9/|
    |                              |
    |                              |
    | Flying                       |
    |                              |
    |                              |
    | Descending,                  |
    | Winter unending.             |
    |                      / 1 /  \\|
    |                      \\  / 2 /|
    | ==>John Matson      #{count_str}    |
    \\______________________________/\n\n
*^(You are No. {count_str}! This content is best viewed by opening this reply directly.)*\n\n""")
        return art


class Negate(CollectiblesTemplate):
    """
    Negate ASCII art object with the number of calls made to it.
    """
    NAME = "Negate"
    SPELLINGS = ["negate", "naegate", "negaete", "naegaete", "nægate", "negæte", "nægæte"]
    COUNT_COMMENT_ID = "nn1eyru"

    def __init__(self, reddit: praw.Reddit):
        super().__init__(reddit)
        self.name = self.NAME
        self.spellings = self.SPELLINGS
        self.timer.stopped = False

    def art(self) -> str:
        """
        Fetches call count, updates it and returns ASCII art with a new collector number.
        :return: ASCII art.
        """
        art_counter_str = self._reddit_counter_actions(self.COUNT_COMMENT_ID)
        negate_art = self.__ascii_template(art_counter_str)
        return negate_art

    @staticmethod
    def __ascii_template(count_str) -> str:
        """
        The ASCII art associated with Negate.
        :param count_str: Number of times the bot has been called for Negate.
        :return: The art.
        """
        art = (f"Desolatormagic is furious:\n\n"
                "_Before this gets deleted by reddit admins, this asshole took it completely out of context. "
                "First of all, the idiot thinks it was a marionette deck. It wasn't. "
                "That card's not even in the deck. "
                "He was running counterspell draw, this was approximately turn 25, "
                "every single creature and spell I cast was countered or removed up until that point "
                "and this dumbass who copied his deck from MTG Salvation or Goldfish used one "
                "of his last copies of negate "
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
                "*********\n\n"
                f"*^(You are No. {count_str} to counter Negate!)*\n\n"
)
        return art


class Collectibles:
    """
    Holds the collectible objects based on CollectibleTemplate.
    """
    def __init__(self, reddit: praw.Reddit):
        self._colossal_dreadmaw = ColossalDreadmaw(reddit)
        self._storm_crow = StormCrow(reddit)
        self._negate = Negate(reddit)
        self._empty = CollectiblesTemplate(None)  # The collectible reply action needs a dummy timer
        self.objects = {
            "Colossal Dreadmaw": self._colossal_dreadmaw,
            "Storm Crow": self._storm_crow,
            "Negate": self._negate,
            "Empty": self._empty,
        }

    def find_matching_collectible(self, regex_matches: list) -> CollectiblesTemplate:
        """
        Finds a collectible object based on RegEx matches.
        :param regex_matches: RegEx matches in a bot call.
        :return: Collectible object if a match is found, otherwise False.
        """
        for match in regex_matches:
            for name, collectible in self.objects.items():
                if match in collectible.spellings:
                    return self.objects[name]
        return self.objects["Empty"]
