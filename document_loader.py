import json
from pathlib import Path

BASE_DIR=Path(__file__).resolve().parent.parent
FILE_DIR=BASE_DIR / "document_ai" / "output.json"

with FILE_DIR.open("r", encoding=("utf-8")) as f:
    file = json.load(f)
if file:
    if not isinstance(file, list) or not isinstance(file[0], dict):
        raise TypeError(f"Zły format pliku: {type(file)} | {type(file[0])} Oczekiwany: list, dict")
    for page in file:    
        if not all(key in page for key in ['page', 'text']):
            raise ValueError("Nieprawidłowa struktura strony")
    for page in file:
        if not isinstance(page['page'], int):
            raise TypeError("Oczekiwany format dla page: int")
        if not isinstance(page['text'], str):
            raise TypeError("Oczekiwany format dla text: str")
else:
    raise ValueError("Plik jest pusty")