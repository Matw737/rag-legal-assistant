from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
import json
from pathlib import Path
import numpy as np

OUTPUT_PATH = Path(r"data\kk_chunks_embeded.json")
EMBEDDINGS_PATH = Path(r"data\kk_embeddings.npy")
model = SentenceTransformer(
    "OPI-PIB/PolDense-400M",
    device="cuda"
)

tokenizer = AutoTokenizer.from_pretrained(
    "OPI-PIB/PolDense-400M"
)
path = Path(r"data\kk_chunks_with_chapters.json")
with path.open('r',encoding="utf-8") as file:
    pages = json.load(file)
texts=[page['text'] for page in pages]
embeddings = model.encode(texts, batch_size=16, show_progress_bar=True)
print(f"Shape: {embeddings.shape} | dtype: {embeddings.dtype}")
for i, art in enumerate(pages):
    pages[i]["vector"]=embeddings[i,:].tolist()
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(pages, f, indent=4, ensure_ascii=False)
np.save(EMBEDDINGS_PATH, embeddings)