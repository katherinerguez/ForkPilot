from datetime import datetime
import numpy as np

class Recommender:
    def __init__(self, user_id, query_store, vector_store, n_recommendations=4, days_limit=7):
        self.user_id = user_id
        self.query_store = query_store  
        self.vector_store = vector_store  
        self.n_recommendations = n_recommendations
        self.days_limit = days_limit
        self.seen_docs = set()

    def store_query(self, query, used_docs):
            embedding = self.query_store._embedding_function.embed_query(query)
            self.query_store.add_texts(
                texts=[query],
                metadatas=[{
                    "user_id": self.user_id,
                    "query_text": query,
                    "date": str(datetime.now()),
                    "used_docs": ", ".join(used_docs)
                }],
                embeddings=[embedding]
            )
            self.seen_docs.update(used_docs)