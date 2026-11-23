import json
from pathlib import Path

DATA_PATH = Path(r"data\kk.json")


def load_pages(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        pages = json.load(file)

    if not isinstance(pages, list):
        raise TypeError("Oczekiwano listy stron.")

    for index, page in enumerate(pages):
        if not isinstance(page, dict):
            raise TypeError(f"Element {index} nie jest słownikiem.")

        if "page" not in page or "text" not in page:
            raise ValueError(
                f"Element {index} nie zawiera pola page lub text."
            )

        if not isinstance(page["page"], int):
            raise TypeError(f"Niepoprawny numer strony: {index}")

        if not isinstance(page["text"], str):
            raise TypeError(f"Tekst strony {page['page']} nie jest stringiem.")

    return pages


def audit_pages(pages: list[dict]) -> None:
    page_numbers = [page["page"] for page in pages]
    texts = [page["text"] for page in pages]

    print(f"Liczba stron: {len(pages)}")
    print(f"Liczba pustych stron: {sum(not text.strip() for text in texts)}")
    print(f"Unikalne numery stron: {len(set(page_numbers))}")
    print(f"Powtórzone numery stron: {len(page_numbers) - len(set(page_numbers))}")
    print(f"Łączna liczba znaków: {sum(len(text) for text in texts)}")

    for page in pages[:3]:
        print(f"\n--- STRONA {page['page']} ---")
        print(page["text"][:250])


if __name__ == "__main__":
    pages = load_pages(DATA_PATH)
    audit_pages(pages)