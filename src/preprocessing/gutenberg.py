import re
import unicodedata

def normalize_unicode(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")

def remove_spaces(text):
    return re.sub(r"\s+", " ", text).strip()

def remove_special_characters(text):
    return re.sub(r"[^\w\s,.:\-]", "", text)

def remove_headers(text):
    text=text.lower()
    for i in [r'.*?preface\s*', r'.*?table of contents\s*', r'.*?contents\s*']:
        text = re.sub(i, '', text, 1)
    return text

def remove_footer(text):
    text=re.sub(r'\bsection\s*\d+', '', text)
    return re.sub(r'\bgeneral information about project gutenberg\b.*', '', text)