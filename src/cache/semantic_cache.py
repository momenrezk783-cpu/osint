import hashlib
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Optional

class SemanticCache:
    def __init__(self, similarity_threshold=0.92):
        self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        self.cache_keys = []
        self.embeddings = None
        self.norms = None
        self.responses = []
        self.threshold = similarity_threshold

    def _embed(self, text: str):
        return self.model.encode(text)

    def get(self, query: str) -> Optional[str]:
        if self.embeddings is None or len(self.cache_keys) == 0:
            return None

        query_emb = self._embed(query)
        query_norm = np.linalg.norm(query_emb)
        if query_norm == 0:
            return None

        # Vectorized cosine similarity
        sims = np.dot(self.embeddings, query_emb) / (self.norms * query_norm)

        best_idx = np.argmax(sims)
        if sims[best_idx] >= self.threshold:
            return self.responses[best_idx]

        return None

    def set(self, query: str, response: str):
        key = hashlib.sha256(query.encode()).hexdigest()
        if key in self.cache_keys:
            return

        emb = self._embed(query)
        norm = np.linalg.norm(emb)

        self.cache_keys.append(key)
        self.responses.append(response)

        if self.embeddings is None:
            self.embeddings = np.array([emb])
            self.norms = np.array([norm])
        else:
            self.embeddings = np.vstack([self.embeddings, emb])
            self.norms = np.append(self.norms, norm)
