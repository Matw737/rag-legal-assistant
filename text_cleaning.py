import re


def clean_text(text: str) -> str:
    """
    Czyści tekst OCR przed chunkingiem.

    Zachowuje strukturę prawną dokumentu,
    usuwa typowe artefakty formatowania.
    """

    # Ujednolicenie zakończeń wierszy.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Naprawa wyrazów rozdzielonych łącznikiem
    # na końcu wiersza, np.:
    # "praw-\nnego" -> "prawnego"
    #
    # Nie usuwamy łączników występujących
    # wewnątrz zwykłych wyrażeń.
    text = re.sub(
        r"(?<=[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż])"
        r"-[ \t]*\n[ \t]*"
        r"(?=[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż])",
        "",
        text,
    )

    # Usunięcie spacji na początku i końcu wiersza.
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[ \t]+", "", text, flags=re.MULTILINE)

    # Ograniczenie serii wielu spacji i tabulatorów.
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text
