import json
from pathlib import Path
from model_loader import model
import numpy as np
from sentence_transformers.util import cos_sim

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CHUNKS_DIR = DATA_DIR / "kk_chunks_with_chapters.json"
EMBEDDINGS_DIR = DATA_DIR / "kk_embeddings.npy"

embeddings = np.load(EMBEDDINGS_DIR)
with CHUNKS_DIR.open("r", encoding="utf-8") as file:
    kk_chunks = json.load(file)

text='§ 13. Postanowienia końcowe 1. Wszelkie zmiany umowy wymagają formy dokumentowej, chyba że przepisy prawa wymagają formy szczególnej. 2. W sprawach nieuregulowanych umową zastosowanie mają przepisy prawa polskiego. 3. Strony będą dążyć do polubownego rozwiązania sporów. W przypadku braku porozumienia spór zostanie poddany pod rozstrzygnięcie sądu właściwego zgodnie z przepisami prawa.'
text2='§ 13. Postanowienia końcowe 1. Wszelkie zmiany umowy wymagają formy dokumentoweJ, chyba że przepisy prawa wymagają formy szczególnej. 2. W sprawach nieuregUlowanych umową zastosowanie mają przepisy prawa polSkiego. 3. Strony będą dążyć do polubOwnego rozwiązania sporów. W przypadku braku porozumienia spór zoSstanie poddany pod rozstrzygnięcie sądu właścIwego zgodnie z przepisami praWa.'
emb1=model.encode(text, show_progress_bar=True)
emb2=model.encode(text2, show_progress_bar=True)
dist=cos_sim(emb1,emb2)
print(dist)