from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer

model = SentenceTransformer(
    "OPI-PIB/PolDense-400M",
    device="cuda"
)