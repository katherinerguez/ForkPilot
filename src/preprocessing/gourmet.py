import re
import unicodedata

def normalize_unicode(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")

def remove_social_links(text):
    patterns = [
        r"https?://[^\s]+",
        r"@gourmetjournal"
    ]
    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return text

def remove_extra_whitespace(text):
    return re.sub(r"\s+", " ", text).strip()

def remove_special_characters(text):
    return re.sub(r"[^\w\s,.:\-]", "", text)

def clean_promotions(text):
    return re.sub(r"(P\.D\.|Descubre más en|Síguenos en|Visita nuestro sitio web|Ver:|).*", "", text, flags=re.IGNORECASE)

def restructure_text(text):
    text = re.sub(r"\n\s*\n", "\n", text) 
    return text

def clean_text(text):
    text = clean_promotions(text)
    text = normalize_unicode(text)
    text = remove_social_links(text)
    text = remove_extra_whitespace(text)
    text = remove_special_characters(text)
    text = restructure_text(text)
    return text