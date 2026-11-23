import json
import re
from pathlib import Path

from text_cleaning import clean_text


# --------------------------------------------------
# 1. Ścieżki do danych
# --------------------------------------------------


SOURCE_PATH = Path(r"data\kk.json")
CHUNKS_PATH = Path(r"data\kk_chunks.json")
OUTPUT_PATH = Path(r"data\kk_chunks_with_chapters.json")


# --------------------------------------------------
# 2. Wzorce rozpoznające strukturę dokumentu
# --------------------------------------------------

CHAPTER_PATTERN = re.compile(
    r"(?m)^[ \t]*(Rozdział[ \t]+[IVXLCDM]+)[ \t]*\n([^\n]+)"
)

ARTICLE_PATTERN = re.compile(
    r"(?m)^[ \t]*Art\.[ \t]*(\d+[a-zA-Z]?)\."
)


# --------------------------------------------------
# 3. Wczytanie dokumentu źródłowego
# --------------------------------------------------

with SOURCE_PATH.open("r", encoding="utf-8") as file:
    pages = json.load(file)

with CHUNKS_PATH.open("r", encoding="utf-8") as file:
    chunks = json.load(file)


# --------------------------------------------------
# 4. Czyszczenie stron i odcięcie wstępu
# --------------------------------------------------

cleaned_pages = [
    {
        "page": page["page"],
        "text": clean_text(page["text"]),
    }
    for page in pages
]

start_page_index = None
start_offset = None

for index, page in enumerate(cleaned_pages):
    match = re.search(
        r"(?m)^[ \t]*USTAWA[ \t]*$",
        page["text"],
    )

    if match:
        start_page_index = index
        start_offset = match.start()
        break

if start_page_index is None:
    raise ValueError("Nie znaleziono początku ustawy.")

cleaned_pages = cleaned_pages[start_page_index:]

cleaned_pages[0]["text"] = (
    cleaned_pages[0]["text"][start_offset:]
)


# --------------------------------------------------
# 5. Połączenie tekstu stron
# --------------------------------------------------

document_text = "\n".join(
    page["text"]
    for page in cleaned_pages
)


# --------------------------------------------------
# 6. Wykrycie rozdziałów i artykułów
# --------------------------------------------------

chapters = list(CHAPTER_PATTERN.finditer(document_text))
articles = list(ARTICLE_PATTERN.finditer(document_text))

print(f"Wykryte rozdziały: {len(chapters)}")
print(f"Wykryte artykuły: {len(articles)}")


# --------------------------------------------------
# 7. Przypisanie rozdziału do każdego chunka
# --------------------------------------------------

chapter_index = 0
current_chapter = None

for chunk in chunks:

    # Znajdź początek artykułu w dokumencie.
    article_match = next(
        (
            match
            for match in articles
            if match.group(1) == chunk["article"].replace("Art. ", "")
        ),
        None,
    )

    if article_match is None:
        chunk["chapter"] = None
        chunk["chapter_title"] = None
        continue

    # Przejdź przez wszystkie rozdziały poprzedzające artykuł.
    while (
        chapter_index < len(chapters)
        and chapters[chapter_index].start() < article_match.start()
    ):
        chapter_match = chapters[chapter_index]

        current_chapter = {
            "chapter": chapter_match.group(1),
            "chapter_title": chapter_match.group(2).strip(),
        }

        chapter_index += 1

    # Zapisz aktualny rozdział w metadanych chunka.
    if current_chapter is None:
        chunk["chapter"] = None
        chunk["chapter_title"] = None
    else:
        chunk["chapter"] = current_chapter["chapter"]
        chunk["chapter_title"] = current_chapter["chapter_title"]


# --------------------------------------------------
# 8. Zapis nowego zbioru danych
# --------------------------------------------------

with OUTPUT_PATH.open("w", encoding="utf-8") as file:
    json.dump(chunks, file, ensure_ascii=False, indent=2)


# --------------------------------------------------
# 9. Kontrola wyników
# --------------------------------------------------

assigned = sum(
    1 for chunk in chunks
    if chunk["chapter"] is not None
)

unassigned = len(chunks) - assigned

print(f"Chunki z przypisanym rozdziałem: {assigned}")
print(f"Chunki bez rozdziału: {unassigned}")
print(f"Zapisano dane do: {OUTPUT_PATH}")

print("\n--- PRZYKŁADOWE METADANE ---")

for chunk in chunks[:5]:
    print(
        chunk["article"],
        "|",
        chunk["chapter"],
        "|",
        chunk["chapter_title"],
    )