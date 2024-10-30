"""Rastamonliveup class and card data."""


class RastamonCard:
    """
    A class to represent a Rastamonliveup card.
    """
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

    def find_name(self, suspect_name: str):
        """
        Finds the proper name of the Rastamonliveup card from the pool of alternate spellings.
        :param suspect_name: Suspected Rastamonliveup cardname.
        :return: Proper name or empty string if no match is found.
        """
        if suspect_name in self.spellings:
            return self.proper_name
        else:
            return ""


# Create all Rastamonliveup cards
simbaba = RastamonCard("Simbaba",
    ["simbaba"],
    "https://i.redd.it/3acfd9iryqjd1.png")

japudi = RastamonCard("Japudi",
    ["japudi"],
    "https://i.redd.it/ln92vcaxjnfa1.jpg")

kuka_beyo = RastamonCard("Kuka Beyo",
    ["kuka beyo"],
    "https://i.redd.it/7tg9y2u7mvfa1.jpg")

tobo_dibi = RastamonCard("Tōbō Dibi",
    ["tobo dibi", "tōbō dibi"],
    "https://i.redd.it/his9093feaga1.jpg")

bosgwan = RastamonCard("Bôsgwan",
    ["bosgwan", "bôsgwan"],
    "https://i.redd.it/b8ti2tcf9wga1.jpg")

mwabdi = RastamonCard("Mwabdi",
    ["mwabdi"],
    "https://i.redd.it/v7tpor93xuha1.jpg")

kadyoba = RastamonCard("Kadÿoba",
    ["kadyoba", "kadÿoba"],
    "https://i.redd.it/on1zb0bu42ja1.jpg")

komdege_swigu = RastamonCard("Komdegé Swígu",
    ["komdege swigu", "komdegé swigu", "komdege swígu", "komdegé swígu"],
    "https://i.redd.it/kte28a4yk8ka1.jpg")

dodonbe_dugdjita = RastamonCard("Dodonbè Dugdjita",
    ["dodonbe dugdjita", "dodonbè dugdjita"],
    "https://i.redd.it/p5ywsh4yk8ka1.jpg")

sembizi_wamdeyo = RastamonCard("Sembizi Wamdeyo",
    ["sembizi wamdeyo"],
    "https://i.redd.it/q3ybd1udokra1.jpg")

sebi_gyandu = RastamonCard("Sebi Gyandu",
    ["sebi gyandu"],
    "https://i.redd.it/uvqqezzgp4dd1.jpeg")

# List-ify cards for searching
cards = [simbaba, japudi, kuka_beyo, tobo_dibi, bosgwan, mwabdi,
         kadyoba, komdege_swigu, dodonbe_dugdjita, sembizi_wamdeyo, sebi_gyandu]