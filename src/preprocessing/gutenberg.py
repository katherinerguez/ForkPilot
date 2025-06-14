import re
import unicodedata

def normalize_unicode(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")