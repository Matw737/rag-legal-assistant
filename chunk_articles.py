import json
import re
from pathlib import Path
from text_cleaning import clean_text

DATA_PATH = Path(r"data\kk.json")
OUTPUT_PATH = Path(r"data\kk_chunks.json")

ARTICLE_PATTERN = re.compile(
    r"(?m)^[ \t]*Art\.\s*(\d+[a-zA-Z]?)\.[ \t]*"
)

def load_pages(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        pages = json.load(file)
    if not isinstance(pages, list):
        raise TypeError("Oczekiwano listy stron.")
    for page in pages:
        if(
            not isinstance(page, dict)
            or not isinstance(page.get("page"), int)
            or not isinstance(page.get("text"), str)
        ):
            raise ValueError("Nieprawidłowa struktura strony.")
    return pages

def extract_article_chunks(pages: list[dict]) -> list[dict]:
    cleaned_pages = [
        {
            "page": page["page"],
            "text": clean_text(page["text"]),
        }
        for page in pages
    ]

    # Znajdź początek właściwego tekstu ustawy.
    start_page_index = None
    start_offset = None

    for page_index, page in enumerate(cleaned_pages):
        match = re.search(
            r"(?m)^[ \t]*USTAWA[ \t]*$",
            page["text"],
        )

        if match:
            start_page_index = page_index
            start_offset = match.start()
            break

    if start_page_index is None:
        raise ValueError("Nie znaleziono początku ustawy.")

    # Odetnij wstęp poprzedzający ustawę.
    cleaned_pages = cleaned_pages[start_page_index:]
    cleaned_pages[0]["text"] = cleaned_pages[0]["text"][start_offset:]

    # Połącz tekst stron i zapamiętaj zakresy znaków każdej strony.
    document_parts = []
    page_ranges = []
    position = 0

    for page in cleaned_pages:
        text = page["text"]

        page_start = position
        document_parts.append(text)
        position += len(text)
        page_end = position

        page_ranges.append({
            "page": page["page"],
            "start": page_start,
            "end": page_end,
        })

        # Separator między stronami.
        document_parts.append("\n")
        position += 1

    document_text = "".join(document_parts)

    # Wykryj początki artykułów w całym dokumencie.
    article_pattern = re.compile(
        r"(?m)^[ \t]*Art\.[ \t]*(\d+[a-zA-Z]?)\.[ \t]*"
    )

    article_starts = list(article_pattern.finditer(document_text))

    if not article_starts:
        raise ValueError("Nie znaleziono żadnych artykułów.")

    chunks = []

    for index, match in enumerate(article_starts):
        chunk_start = match.start()

        if index + 1 < len(article_starts):
            chunk_end = article_starts[index + 1].start()
        else:
            chunk_end = len(document_text)

        chunk_text = document_text[chunk_start:chunk_end].strip()

        if not chunk_text:
            continue

        # Ustal strony, na których znajduje się ten artykuł.
        overlapping_pages = [
            page_range["page"]
            for page_range in page_ranges
            if page_range["start"] < chunk_end
            and page_range["end"] > chunk_start
        ]

        if not overlapping_pages:
            continue

        article_number = match.group(1)

        chunks.append({
            "id": f"kk_art_{article_number}",
            "source": "Kodeks karny",
            "article": f"Art. {article_number}",
            "page_start": overlapping_pages[0],
            "page_end": overlapping_pages[-1],
            "text": chunk_text,
        })

    return chunks

def main()-> None:
    pages = load_pages(DATA_PATH)
    chunks = extract_article_chunks(pages)
    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=2,
        )
    print(f"Liczba stron wejściowych: {len(pages)}")
    print(f"Liczba chunków: {len(chunks)}")
    print(f"Zapisano do {OUTPUT_PATH}")

    print("\n--- PIERWSZE 3 CHUNKI ---")
    for chunk in chunks[:3]:
        print(
            f"\n{chunk['article']} | "
            f"strony {chunk['page_start']} - {chunk['page_end']}"
        )
        print(chunk["text"][:500])
if __name__ == "__main__":
    main()