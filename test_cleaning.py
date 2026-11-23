import json
import re
from pathlib import Path

from text_cleaning import clean_text


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = Path(r"data\kk.json")


def main() -> None:
    with DATA_PATH.open("r", encoding="utf-8") as file:
        pages = json.load(file)

    original_text = "\n".join(page["text"] for page in pages)
    cleaned_text = clean_text(original_text)

    print("Oryginalna liczba znaków:", len(original_text))
    print("Po czyszczeniu:", len(cleaned_text))
    print("Usunięte znaki:", len(original_text) - len(cleaned_text))

    remaining_splits = re.findall(
        r"(?m)\b[\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+-[ \t]*\n[ \t]*"
        r"[\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+",
        cleaned_text,
    )

    print("Pozostałe podejrzane podziały:", len(remaining_splits))

    print("\n--- TEST PRZYKŁADOWY ---")
    sample = "praw-\nnego przepisu"
    print("Przed:", repr(sample))
    print("Po:", repr(clean_text(sample)))


if __name__ == "__main__":
    main()
