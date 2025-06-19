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
            
    def get_user_embedding(self):
        user_queries = self.query_store.get(where={"user_id": self.user_id}, include=["metadatas", "embeddings"])
        if not user_queries["metadatas"]:
            return None

        recent_embeddings = []
        for metadata, emb in zip(user_queries["metadatas"], user_queries["embeddings"]):
            query_date = datetime.fromisoformat(metadata["date"])
            if (datetime.now() - query_date).days <= self.days_limit:
                recent_embeddings.append(emb)

        if not recent_embeddings:
            return None

        return np.mean(recent_embeddings, axis=0)
    
    def recommend(self):
        user_profile = self.get_user_embedding()
        if user_profile is None:
            return []

        all_docs = self.vector_store.similarity_search_by_vector(user_profile.tolist(), k=100)
        recommendations = []
        seen_sources = self.seen_docs

        for doc in all_docs:
            src = doc.metadata.get("source")
            if src not in seen_sources:
                similarity = doc.metadata.get("score", None)
                recommendations.append((doc, similarity))
            if len(recommendations) >= self.n_recommendations:
                break

        if len(recommendations) < self.n_recommendations:
            remaining = self.n_recommendations - len(recommendations)
            fallback = [
                (doc, doc.metadata.get("score", None)) for doc in all_docs
                if doc.metadata.get("source") not in [d.metadata.get("source") for d, _ in recommendations]
            ][:remaining]
            recommendations.extend(fallback)

        self.seen_docs.update(doc.metadata["source"] for doc, _ in recommendations)
        return recommendations