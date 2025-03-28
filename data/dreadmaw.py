"""Colossal Dreadmaw special."""

import praw


class Dreadmaw:
    """
    Colossal Dreadmaw ASCII art object with the number of calls made to it.
    """
    DREADMAW_CALLNAME = "colossal dreadmaw"

    def __init__(self, reddit: praw.Reddit):
        self.reddit = reddit

    def dreadmaw_ascii_art(self) -> str:
        """
        Fetches call count, updates it and returns ASCII art with a new collector number.
        :return: ASCII art.
        """
        count = self.__dreadmaw_count()
        self.__dreadmaw_count_increment(count)
        count_str = self.__call_count_str(count)
        art = self.__ascii_art(count_str)
        return art

    def __dreadmaw_count(self) -> int:
        """
        Fetches the current Dreadmaw call count from Reddit.
        :return: Number of times Dreadmaw has been called.
        """
        number = int(self.reddit.comment("me0tbmp").body)
        return number

    def __dreadmaw_count_increment(self, old_count: int):
        """
        Edits the post on Reddit that contains Dreadmaw's call count and updates the count.
        """
        new_count: int = old_count + 1
        self.reddit.comment("me0tbmp").edit(str(new_count))

    @staticmethod
    def __call_count_str(count) -> str:
        """
        Formats the number of calls into a string with a suitable number of characters.
        Raises a ValueError if the number exceeds 9999.
        :param count: Number of times a call to Colossal Dreadmaw has been made.
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
            raise ValueError("Colossal Dreadmaw collector number has too many digits.")

    @staticmethod
    def __ascii_art(count_str) -> str:
        """
        Gets the ASCII art associated with Colossal Dreadmaw.
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
    | (Creature ── Dinosaur    ۞) |
    |                              |
    |                              |
    | Trample                      |
    |                              |
    | You see its teeth.           |
    | It's too late.               |
    |                              |
    |                      / 6 /  \\|
    | #{count_str} C              \\  / 6 /|
    | XLN*EN  =>Jesper Ejsing      |
    \\______________________________/\n\n''')
        return art
