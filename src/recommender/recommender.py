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
