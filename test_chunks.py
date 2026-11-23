import json
import re
from pathlib import Path

CHUNKS_PATH = Path(r"data\kk_chunks.json")


def main():
    with CHUNKS_PATH.open("r", encoding="utf-8") as file:
        chunks = json.load(file)

    print(f"Liczba chunków: {len(chunks)}")

    # 1. Sprawdź unikalność identyfikatorów.
    ids = [chunk["id"] for chunk in chunks]
    duplicate_ids = len(ids) - len(set(ids))

    print(f"Duplikaty ID: {duplicate_ids}")

    # 2. Sprawdź puste chunki.
    empty_chunks = [
        chunk for chunk in chunks
        if not chunk["text"].strip()
    ]

    print(f"Puste chunki: {len(empty_chunks)}")

    # 3. Sprawdź zgodność metadanych z początkiem tekstu.
    mismatches = []

    for chunk in chunks:
        match = re.match(
            r"Art\.\s*(\d+[a-zA-Z]?)\.",
            chunk["text"]
        )

        if not match:
            mismatches.append(chunk["id"])
            continue

        actual_article = f"Art. {match.group(1)}"

        if actual_article != chunk["article"]:
            mismatches.append(chunk["id"])

    print(f"Niezgodne oznaczenia artykułów: {len(mismatches)}")

    if mismatches:
        print("Przykłady:", mismatches[:10])

    # 4. Sprawdź długość chunków.
    lengths = [len(chunk["text"]) for chunk in chunks]

    if lengths:
        print(f"Najkrótszy chunk: {min(lengths)} znaków")
        print(f"Najdłuższy chunk: {max(lengths)} znaków")
        print(f"Średnia długość: {sum(lengths) / len(lengths):.1f} znaków")

        long_chunks = [
            chunk for chunk in chunks
            if len(chunk["text"]) > 5000
        ]

        print(f"Chunki dłuższe niż 5000 znaków: {len(long_chunks)}")

        for chunk in long_chunks[:5]:
            print(
                f"  {chunk['article']}: "
                f"{len(chunk['text'])} znaków"

            )

    # 5. Ręczna kontrola skrajnych przypadków.
    shortest = min(chunks, key=lambda chunk: len(chunk["text"]))
    longest = max(chunks, key=lambda chunk: len(chunk["text"]))

    for label, chunk in [
        ("NAJKRÓTSZY CHUNK", shortest),
        ("NAJDŁUŻSZY CHUNK", longest),
    ]:
        print(f"\n--- {label} ---")
        print(f"Artykuł: {chunk['article']}")
        print(f"Długość: {len(chunk['text'])} znaków")
        print(f"Strony: {chunk['page_start']}-{chunk['page_end']}")
        print(chunk["text"][:1500])



if __name__ == "__main__":
    main()

