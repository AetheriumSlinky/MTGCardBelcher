"""Rastamonliveup class and card data."""


class RastamonCard:
    """Holds a Rastamonliveup card's attributes."""
    def __init__(self, proper_name: str, spellings: list, image: str):
        """
        Constructs the Rastamonliveup card object that contains the names and links of the card.
        :param proper_name: Proper spelling of the card.
        :param spellings: Most common alternative (incorrect) spellings.
        :param image: Link to card image.
        """
        self.proper_name = proper_name
        self.spellings = spellings
        self.image = image

    def __str__(self):
        return f"Attributes: {self.__dict__}"


class Rastamon:
    """Contains all RastamonCard objects."""

    SIMBABA = RastamonCard("Simbaba",
    ["simbaba"],
    "https://i.redd.it/3acfd9iryqjd1.png")

    JAPUDI = RastamonCard("Japudi",
    ["japudi"],
    "https://i.redd.it/ln92vcaxjnfa1.jpg")

    KUKA_BEYO = RastamonCard("Kuka Beyo",
    ["kuka beyo"],
    "https://i.redd.it/7tg9y2u7mvfa1.jpg")

    TOBO_DIBI = RastamonCard("Tōbō Dibi",
    ["tobo dibi", "tōbō dibi"],
    "https://i.redd.it/his9093feaga1.jpg")

    BOSGWAN = RastamonCard("Bôsgwan",
    ["bosgwan", "bôsgwan"],
    "https://i.redd.it/b8ti2tcf9wga1.jpg")

    MWABDI = RastamonCard("Mwabdi",
    ["mwabdi"],
    "https://i.redd.it/v7tpor93xuha1.jpg")

    KADYOBA = RastamonCard("Kadÿoba",
    ["kadyoba", "kadÿoba"],
    "https://i.redd.it/on1zb0bu42ja1.jpg")

    KOMDEGE_SWIGU = RastamonCard("Komdegé Swígu",
    ["komdege swigu", "komdegé swigu", "komdege swígu", "komdegé swígu"],
    "https://i.redd.it/kte28a4yk8ka1.jpg")

    DODONBE_DUGDJITA = RastamonCard("Dodonbè Dugdjita",
    ["dodonbe dugdjita", "dodonbè dugdjita"],
    "https://i.redd.it/p5ywsh4yk8ka1.jpg")

    SEMBIZI_WAMDEYO = RastamonCard("Sembizi Wamdeyo",
    ["sembizi wamdeyo"],
    "https://i.redd.it/q3ybd1udokra1.jpg")

    SEBI_GYANDU = RastamonCard("Sebi Gyandu",
    ["sebi gyandu"],
    "https://i.redd.it/uvqqezzgp4dd1.jpeg")

    GALATIANS = RastamonCard("Tell the children the truth",
    ["gal 4:16", "gal. 4:16", "galatians 4:16", "4:16"],
    "https://i.redd.it/uvqqezzgp4dd1.jpeg")

    CARDS = [
        SIMBABA, JAPUDI, KUKA_BEYO, TOBO_DIBI, BOSGWAN, MWABDI, KADYOBA,
        KOMDEGE_SWIGU, DODONBE_DUGDJITA, SEMBIZI_WAMDEYO, SEBI_GYANDU, GALATIANS,
    ]

    @classmethod
    def find_card(cls, suspect_name: str) -> "RastamonCard":
        """
        Finds the proper name of the Rastamonliveup card from the pool of alternate spellings.
        :param suspect_name: Suspected Rastamonliveup cardname.
        :return: Corresponding RastamonCard object if a match is found, an empty RastamonCard if no match.
        """
        for card in cls.CARDS:
            if suspect_name.casefold() in card.spellings:
                return card
        return RastamonCard("", [], "")
