import re
import unicodedata
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings

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

def split_text_semantically(text, breakpoint_type="gradient"):
    # Usar embeddings locales gratuitos
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    text_splitter = SemanticChunker(embeddings, breakpoint_threshold_type=breakpoint_type)
    docs = text_splitter.create_documents([text])
    return [doc.page_content for doc in docs]

def main(document_content):
 
    # Dividir el texto utilizando el tipo de umbral elegido (percentil)
    tipo_umbral = "gradient"
    fragments = split_text_semantically(document_content, breakpoint_type=tipo_umbral)
    chuncks=[]
    for i, fragment in enumerate(fragments):
        chuncks.append(fragment)
    return chuncks

def clean_text(text):
    """
    Esta función se encarga de aplicar al texto cada una de las funciones del preprocesamiento."""
    text = normalize_unicode(text)
    text = remove_headers(text)         
    text = remove_footer(text)
    text = remove_special_characters(text)
    text = remove_spaces(text)
    text= main(text)
    return text