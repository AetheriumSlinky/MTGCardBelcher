"""Colossal Dreadmaw special."""


class DreadmawObj:
    """
    Colossal Dreadmaw ASCII art object with the number of calls made to it.
    """
    def __init__(self):
        self.__logical_name = "colossal dreadmaw2"
        self.calls_count = 0
        self.art = self.get_art(self.calls_count)

    def get_art(self, count):
        """
        Gets the ASCII art associated with Colossal Dreadmaw.
        :param count: Number of times the bot has been called for Colossal Dreadmaw.
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
    | #{self.call_count_str(count)} C              \\  / 6 /|
    | XLN*EN  =>Jesper Ejsing      |
    \\______________________________/\n\n''')
        return art

    @classmethod
    def get_name(cls) -> str:
        """
        Gets the internal name of Colossal Dreadmaw. Used for checking and triggers.
        :return: Colossal Dreadmaw's logical name.
        """
        name = cls().__logical_name
        return name

    @staticmethod
    def call_count_str(count) -> str:
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


dreadmaw_holder = DreadmawObj()
