import re
import unicodedata

def normalize_unicode(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")

def remove_spaces(text):
    return re.sub(r"\s+", " ", text).strip()

def remove_special_characters(text):
    return re.sub(r"[^\w\s,.:\-]", "", text)