"""Colossal Dreadmaw special."""

import praw


class CollectibleCards:
    """
    All 'collectible' card objects.
    """
    TIMER_MIN = 300
    TIMER_MAX = 7200

    def __init__(self, reddit: praw.Reddit):
        self.reddit = reddit

    def __previous_count(self, count_comment_id: str) -> int:
        """
        Fetches the current Dreadmaw call count from Reddit.
        :return: Number of times Dreadmaw has been called.
        """
        number = int(self.reddit.comment(count_comment_id).body)
        return number

    def __increment_count(self, old_count: int, count_comment_id: str):
        """
        Edits the post on Reddit that contains Dreadmaw's call count and updates the count.
        """
        new_count: int = old_count + 1
        self.reddit.comment(count_comment_id).edit(str(new_count))

    @staticmethod
    def __count_to_str(count) -> str:
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


class StormCrow(CollectibleCards):
    """
    Storm Crow ASCII art object with the number of calls made to it.
    """
    NAME = "Storm Crow"
    COUNT_COMMENT = "mlnqxci"

    def __init__(self, reddit: praw.Reddit):
        super().__init__(reddit)

    def stormcrow_ascii_art(self) -> str:
        """
        Fetches call count, updates it and returns ASCII art with a new collector number.
        :return: ASCII art.
        """
        prev_count = self.__previous_count(self.COUNT_COMMENT)
        self.__increment_count(prev_count, self.COUNT_COMMENT)
        count_str = self.__count_to_str(prev_count)
        art = self.__ascii_template(count_str)
        return art

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
    | (Creature ── Bird         \\9/|
    |                              |
    |                              |
    | Flying                       |
    |                              |
    |                              |
    | Descending,                  |
    | Winter unending.             |
    |                      / 1 /  \\|
    |                             \\  / 2 /|
    | ==>John Matson      #{count_str}    |
    \\______________________________/\n\n""")
        return art


class ColossalDreadmaw(CollectibleCards):
    """
    Colossal Dreadmaw ASCII art object with the number of calls made to it.
    """
    NAME = "Colossal Dreadmaw"
    COUNT_COMMENT = "me0tbmp"

    def __init__(self, reddit: praw.Reddit):
        super().__init__(reddit)

    def dreadmaw_ascii_art(self) -> str:
        """
        Fetches call count, updates it and returns ASCII art with a new collector number.
        :return: ASCII art.
        """
        prev_count = self.__previous_count(self.COUNT_COMMENT)
        self.__increment_count(prev_count, self.COUNT_COMMENT)
        count_str = self.__count_to_str(prev_count)
        art = self.__ascii_template(count_str)
        return art

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
    \\______________________________/\n\n''')
        return art
