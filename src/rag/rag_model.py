from langchain_community.chat_models import ChatOllama
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from datetime import datetime
from src.crawler.cookpad import CookpadCrawler


class RAG:
    def __init__(self, collection_name="gastronomia", embedding_model="sentence-transformers/distiluse-base-multilingual-cased-v2", persist_directory="./chroma_lan"):
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

    def get_stored_ids(self) -> set:
        results = self.vector_store.get(include=["metadatas"])
        return set(meta["id"] for meta in results["metadatas"] if "id" in meta)

    
    def retrieve(self, query: str, min_score: float = 0.5, min_date: str = "2000-06-01"):
        retrieved = self.vector_store.similarity_search_with_score(query)
        retrieved.sort(key=lambda x: x[1], reverse=True)
        min_dt = datetime.fromisoformat(min_date)

        filtered = []
        for doc, score in retrieved:
            pub_date = doc.metadata.get("publication_date")
            try:
                pub_dt = datetime.fromisoformat(pub_date) if pub_date else None
            except:
                pub_dt = None

            if pub_dt:
                pub_dt = pub_dt.replace(tzinfo=None)

            if score >= min_score and pub_dt and pub_dt >= min_dt:
                print(f"{doc.metadata.get('title')} - Relevancia: {score:.4f}")
                print(f"{doc.metadata.get('url')}")
                filtered.append(doc)

        return filtered

    def generate(self, query: str, k = 5, max_crawls = 3):
        attempts = 0
        filtered_docs = self.retrieve(query)

        while len(filtered_docs) < k and attempts < max_crawls:
            print(f"Solo se encontraron {len(filtered_docs)} documentos válidos. Ejecutando crawler (intento {attempts + 1})...\n")
            exclude_ids = self.get_stored_ids()
            crawler = CookpadCrawler(query=query, min_new=5, exclude_ids=exclude_ids)
            crawler.search()

            if crawler.documents:
                new_docs = [doc for doc in crawler.documents if doc.metadata["id"] not in exclude_ids]
                self.vector_store.add_documents(new_docs)

            filtered_docs = self.retrieve(query)
            attempts += 1

        filtered_docs = filtered_docs[:k]
        context = "\n\n".join(doc.page_content for doc in filtered_docs)
        messages = self.prompt.invoke({"input": query, "context": context})
        return self.llm.invoke(messages).content