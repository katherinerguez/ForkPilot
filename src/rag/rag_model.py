from langchain_community.chat_models import ChatOllama
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document

class RAG:
    def __init__(self, collection_name="gastronomia", embedding_model="sentence-transformers/distiluse-base-multilingual-cased-v2", persist_directory="./chroma_lang"):
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

    def retrieve(self, query: str):
        retrieved_docs = self.vector_store.similarity_search_with_score(query)
        retrieved_docs.sort(key=lambda x: x[1], reverse=True)
        for doc, score in retrieved_docs:
            print(f" {doc.metadata['title']} - Relevancia: {score:.4f}")
            print(f" Acceda a  el aquí: {doc.metadata['url']}")
        return [doc for doc, score in retrieved_docs]

    def generate(self, query, context_docs: list[Document]):
        docs_content = "\n\n".join(doc.page_content for doc in context_docs)
        messages = self.prompt.invoke({"input": query, "context": docs_content})
        return self.llm.invoke(messages).content