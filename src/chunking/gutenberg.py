import os
from langchain_chroma import Chroma
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from gutenberg import cleaned_text
 
def split_text_semantically(text, breakpoint_type="gradient"):
    """
    Esta función es para realizar la fragmentacón semántica."""
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    text_splitter = SemanticChunker(embeddings, breakpoint_threshold_type=breakpoint_type)
    docs = text_splitter.create_documents([text])
    return [doc.page_content for doc in docs]

def main(document_content):
    """
    Esta función es para tomar el texto y llamar a una función para realizarle la fragmentacón semántica."""
    # Dividir el texto utilizando el tipo de umbral 
    tipo_umbral = "gradient"
    fragments = split_text_semantically(document_content, breakpoint_type=tipo_umbral)
    chunks = []
    for i, fragment in enumerate(fragments):
        chunks.append(fragment)
    return chunks

# Configuración del vector 
vector_store = Chroma(
    collection_name="gastronomia",
    embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/distiluse-base-multilingual-cased-v2"),
    persist_directory="./chroma_gastronomy"
)

folder_path = "saved_articles"
documents = []
#cargar los archivos y procesarlos
for file_name in os.listdir(folder_path):
    file_path = os.path.join(folder_path, file_name)
    if file_name.endswith(".txt") and os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
            clean_text = cleaned_text(raw_text)
            
            text_fragments = main(clean_text)
            for fragment in text_fragments:
                
                doc = Document(page_content=fragment, metadata={"source": file_path})
                documents.append(doc)

print(f"Se cargaron {len(documents)} fragmentos correctos.")

batch_size = 100  
for i in range(0, len(documents), batch_size):
    batch = documents[i : i + batch_size]
    vector_store.add_documents(batch)
    print(f"Se añadieron documentos del batch {i} al {i+len(batch)}")

print("Vectores añadidos correctamente.")
