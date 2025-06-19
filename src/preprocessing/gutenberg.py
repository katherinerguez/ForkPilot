import re
import unicodedata

def normalize_unicode(text):
    """
    Esta función es para normalizar el texto"""
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")

def remove_spaces(text):
    """
    Esta función es para eliminar los espacis extras y los saltos de líneas."""
    return re.sub(r"\s+", " ", text).strip()

def remove_special_characters(text):
    """
    Esta función es para eliminar los caracteres especiales.
    returns: solo caracter alfanumérico, signos de puntuación y la barra invertida.
    """
    
    return re.sub(r"[^\w\s,.:\-]", "", text)

def remove_headers(text):
    """
    Esta función es para eliminar los encabezados.
    returns: todo lo que se encuentra despues de preface, table of contents or contents.
    """
    text=text.lower()
    for i in [r'.*?preface\s*', r'.*?table of contents\s*', r'.*?contents\s*']:
        text = re.sub(i, '', text, 1)
    return text

def remove_footer(text):
    """
    Esta función es para eliminar los pie de página.
    returns: hasta que se encuentre end of the project gutenberg ebook or start: full license
    """
    text=re.sub(r'\bsection\s*\d+', '', text)
    text=re.sub(r'\bend of the project gutenberg ebook\b.*', '', text)
    return re.sub(r'\bstart: full license\b.*', '', text)


def clean_text(text):
    """
    Esta función se encarga de aplicar al texto cada una de las funciones del preprocesamiento."""
    text = normalize_unicode(text)
    text = remove_headers(text)         
    text = remove_footer(text)
    text = remove_special_characters(text)
    text = remove_spaces(text)
    
    return text