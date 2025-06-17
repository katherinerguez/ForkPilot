from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import os      
from gourmet import cleaned_text

vector_store = Chroma(
    collection_name="gastronomia",
    embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/distiluse-base-multilingual-cased-v2"),
    persist_directory="./chroma_gastronomy"
)

folder_path = "saved_articles"
documents = []

for file_name in os.listdir(folder_path):
    file_path = os.path.join(folder_path, file_name)
    if file_name.endswith(".txt") and os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
            clean_text = cleaned_text(raw_text)
            documents.append(Document(page_content = clean_text.lower(),metadata={"source": file_path}))

print(f"Se cargaron {len(documents)} documentos correctamente.")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
split_docs = text_splitter.split_documents(documents)

batch_size = 1000
for i in range(0, len(split_docs), batch_size):
    batch = split_docs[i:i+batch_size]
    vector_store.add_documents(batch)
    print(f"Se añadieron documentos del batch {i} al {i+len(batch)}")

print("Vectores añadidos correctamente.")