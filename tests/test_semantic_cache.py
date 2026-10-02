import unittest
from unittest.mock import patch, MagicMock
import numpy as np

from src.cache.semantic_cache import SemanticCache

class TestSemanticCache(unittest.TestCase):
    @patch('src.cache.semantic_cache.SentenceTransformer')
    def setUp(self, mock_transformer):
        self.mock_model_instance = MagicMock()
        mock_transformer.return_value = self.mock_model_instance
        self.cache = SemanticCache(similarity_threshold=0.90)

    def test_get_empty_cache(self):
        self.assertIsNone(self.cache.get("test query"))

    def test_set_and_get_exact_match(self):
        self.mock_model_instance.encode.side_effect = [
            np.array([1.0, 0.0, 0.0]),  # set embedding
            np.array([1.0, 0.0, 0.0])   # get embedding
        ]

        self.cache.set("query 1", "response 1")

        result = self.cache.get("query 1")
        self.assertEqual(result, "response 1")

    def test_set_and_get_similar_match(self):
        self.mock_model_instance.encode.side_effect = [
            np.array([1.0, 0.0, 0.0]),  # set embedding
            np.array([0.95, 0.1, 0.0])  # get embedding
        ]

        self.cache.set("query 1", "response 1")

        result = self.cache.get("similar query 1")
        self.assertEqual(result, "response 1")

    def test_set_and_get_miss(self):
        self.mock_model_instance.encode.side_effect = [
            np.array([1.0, 0.0, 0.0]),  # set embedding
            np.array([0.0, 1.0, 0.0])   # get embedding (orthogonal, similarity 0)
        ]

        self.cache.set("query 1", "response 1")

        result = self.cache.get("different query")
        self.assertIsNone(result)

    def test_set_duplicate_key(self):
        self.mock_model_instance.encode.side_effect = [
            np.array([1.0, 0.0, 0.0])  # Only called once
        ]

        self.cache.set("duplicate query", "response 1")
        self.cache.set("duplicate query", "response 2")

        self.assertEqual(len(self.cache.cache_keys), 1)
        self.assertEqual(self.cache.responses, ["response 1"])
        self.assertEqual(self.mock_model_instance.encode.call_count, 1)

    def test_get_zero_norm_query(self):
        self.mock_model_instance.encode.side_effect = [
            np.array([1.0, 0.0, 0.0]),  # set embedding
            np.array([0.0, 0.0, 0.0])   # get embedding with zero norm
        ]

        self.cache.set("query 1", "response 1")

        result = self.cache.get("zero norm query")
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
