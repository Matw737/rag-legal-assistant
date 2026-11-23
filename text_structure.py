from document_loader import file
import re
from transformers import AutoTokenizer

# article, paragraph, numbered, paragraph_text, continous, heading, attachment, mixed

def format_page_text(lines, gap_threshold=0.25):
    if not lines:
        return ""

    formatted = [lines[0]["text"]]

    for i, line in enumerate(lines[:-1]):
        next_line = lines[i + 1]

        if line["gap_ratio"] > gap_threshold:
            formatted.append("\n\n")
        else:
            formatted.append("\n")

        formatted.append(next_line["text"])

    return "".join(formatted)


def structure_detector(file):
    text = ""
    pages = []

    for p in file:
        page_text = format_page_text(p["lines"])

        text += f"<<<PAGE_{int(p['page'])}>>>\n"
        start = len(text)
        text += page_text + "\n"
        end = len(text)

        pages.append({
            "page": p["page"],
            "start": start,
            "end": end
        })

    return text, pages

document_text, mapping = structure_detector(file)

STRUCTURE_PATTERNS = {
    'article':r"(?m)^[ \t]*\b(art\.?|artykuł|artykul)[ \t]*\d+[a-z]?(?:\.\d+[a-z]?)*[.:)]?",
    'paragraph':r"(?m)^[ \t]*§[ \t]*\d+[a-z]?(?:\.\d+[a-z]?)*[.:)]?",
    'numbered':r"(?m)^[ \t]*(\d+|[a-z])(?:\.\d+[a-z]?)*[.:)]+[ \t]+",
    'paragraph_text':r"\n[ \t]*\n+",
}
def document_processor(text, pages):
    structure_detected={structure_type:[] for structure_type in STRUCTURE_PATTERNS}
    for p, i in STRUCTURE_PATTERNS.items():
        m = re.finditer(i, text, re.IGNORECASE)
        for match in m:
            page_number = None
            for page in pages:
                if page['start'] <= match.start() < page['end']:
                    page_number=page['page']
                    break
            d={
                'marker': match.group(),
                'start': match.start(),
                'end': match.end(),
                'page': page_number,
                }
            structure_detected[p].append(d)
    return structure_detected
structure_detected=document_processor(document_text, mapping)
all_markers = sorted(
    [
        marker
        for markers in structure_detected.values()
        for marker in markers
    ],
    key=lambda x: x['start']
)
def len_add(structure, document_text):
    for structure_type, markers in structure.items():
        for i, marker in enumerate(markers):
            if marker:
                if i + 1 < len(markers):
                    marker["len"] = markers[i+1]['start'] - marker['start']
                else:
                    marker["len"] = len(document_text) - marker['start']
    return structure
full_structure = len_add(structure_detected, document_text)
tokenizer = AutoTokenizer.from_pretrained(
    "OPI-PIB/PolDense-400M"
)
def add_tokens_len(structure, document_text):
    for _, markers in structure.items():
        for marker in markers:
            text = document_text[marker["start"]:marker["start"]+marker["len"]]
            tokens = len(tokenizer.encode(text, add_special_tokens=False))
            marker['tokens_len']=tokens
    return structure
full_structure = add_tokens_len(full_structure, document_text)
def chunk_choose(structure, document_text):
    limit = 2000
    start = []
    end = []
    chunks = {}
    

