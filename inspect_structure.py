import json
import re
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = Path(r'data\kk.json')


def load_pages(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def inspect_structure(pages: list[dict]) -> None:
    full_text = "\n".join(page["text"] for page in pages)

    # Szukamy oznaczeń artykułów.
    article_pattern = re.compile(
        r"(?m)^\s*Art\.\s*\d+[a-zA-Z]?\s*\."
    )
    articles = list(article_pattern.finditer(full_text))

    # Szukamy oznaczeń paragrafów.
    paragraph_pattern = re.compile(
        r"(?m)^\s*§\s*\d+[a-zA-Z]?"
    )
    paragraphs = list(paragraph_pattern.finditer(full_text))

    # Szukamy nagłówków rozdziałów.
    chapter_pattern = re.compile(
        r"(?m)^\s*Rozdział\s+[IVXLCDM]+\b"
    )
    chapters = list(chapter_pattern.finditer(full_text))

    # Wykrywamy wyrazy rozdzielone łącznikiem na końcu wiersza.
    hyphenated_words = re.findall(
        r"(?m)\b[\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+-\s*\n\s*"
        r"[\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+",
        full_text,
    )

    # Wykrywamy podejrzanie częste puste linie.
    blank_lines = len(re.findall(r"\n\s*\n", full_text))

    print(f"Liczba wykrytych oznaczeń artykułów: {len(articles)}")
    print(f"Liczba wykrytych oznaczeń paragrafów: {len(paragraphs)}")
    print(f"Liczba wykrytych nagłówków rozdziałów: {len(chapters)}")
    print(f"Liczba podejrzanych podziałów wyrazów: {len(hyphenated_words)}")
    print(f"Liczba miejsc z pustą linią: {blank_lines}")

    print("\n--- PIERWSZE 15 WYKRYTYCH ARTYKUŁÓW ---")
    for match in articles[:15]:
        print(repr(match.group().strip()))

    print("\n--- PRZYKŁADOWE PODZIAŁY WYRAZÓW ---")
    for word in hyphenated_words[:15]:
        print(repr(word))

    print("\n--- PRZYKŁADOWE NAGŁÓWKI ROZDZIAŁÓW ---")
    for chapter in chapters[:10]:
        print(repr(chapter.group().strip()))


if __name__ == "__main__":
    pages = load_pages(DATA_PATH)
    inspect_structure(pages)
