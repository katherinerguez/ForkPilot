from langchain_community.chat_models import ChatOllama
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from datetime import datetime
from src.crawler.cookpad import CookpadCrawler
from dateutil.parser import isoparse
import time

class RAG:
    def __init__(self, collection_name="gastronomia", embedding_model="sentence-transformers/distiluse-base-multilingual-cased-v2", persist_directory="./chroma_lan"):
        """
        Inicializar RAG 
        """
        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=HuggingFaceEmbeddings(model_name=embedding_model),
            persist_directory=persist_directory
        )
        self.llm = ChatOllama(model="mistral")
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Usa el siguiente contexto para responder la pregunta. Solo responde basado en los documentos. Si no sabes la respuesta, informa educadamente.\n\nContexto: {context}"),
            ("human", "{input}")
        ])

    def get_stored_urls(self) -> set:
        """
        Obtiene los urls de los documentos almacenados en el vector store
        """
        results = self.vector_store.get(include=["metadatas"])
        return set(meta["url"] for meta in results["metadatas"] if "url" in meta)

    
    def retrieve(self, query: str, k = 5, min_score: float = 0.5, min_date: str = "2000-06-01", verbose = True):
        """ 
        Obtiene los documentos que mejor se ajustan a la query
        """
        retrieved = self.vector_store.similarity_search_with_score(query)
        retrieved.sort(key=lambda x: x[1], reverse=True)
        min_dt = datetime.fromisoformat(min_date)

        filtered = []
        for doc, score in retrieved:
            pub_date = doc.metadata.get("publication_date")
            try:
                pub_dt = isoparse(pub_date)
            except:
                pub_dt = None

            if pub_dt:
                pub_dt = pub_dt.replace(tzinfo=None)

            if score >= min_score and pub_dt and pub_dt >= min_dt:
                if verbose: 
                    print(f"{doc.metadata.get('title')} - Relevancia: {score:.4f}")
                    print(f"{doc.metadata.get('url')}")
                filtered.append(doc)
            if len(filtered) >= k:
                break

        return filtered

    def generate(self, query: str, k = 5, max_crawls = 3, verbose = True):
        """
        Obtiene los documentos que mejor se ajustan a la query y genera un texto basado
        en los documentos obtenidos
        """
        filtered_docs = self.retrieve(query, k=k)
        if filtered_docs:
            print(f"Se encontraron {len(filtered_docs)} documentos relevantes. Omitiendo crawler.")
        else:
            print("No se encontraron documentos relevantes. Ejecutando crawler…")

        for attempt in range(max_crawls):
            if len(filtered_docs) >= k:
                break
            
            crawler = CookpadCrawler(query=query, min_new=k, exclude_ids=self.get_stored_urls())
            crawler.search()
            new_docs = [d for d in crawler.documents if d.page_content.strip()]
            if not new_docs:
                print(f"Crawl {attempt+1} no encontro recetas válidas. Siguiente intento.")
                continue

            self.vector_store.add_documents(new_docs)
            print(f"Añadidos {len(new_docs)} docs tras crawl #{attempt+1}")

            filtered_docs = self.retrieve(query, k=k)

        unique_docs = []
        seen = set()
        for doc in filtered_docs:
            url = doc.metadata.get("url")
            if url not in seen:
                unique_docs.append(doc)
                seen.add(url)
        context = "\n\n".join(d.page_content for d in unique_docs)
        messages = self.prompt.invoke({"input": query, "context": context})
        response = self.llm.invoke(messages).content
        return response, unique_docs[:k]