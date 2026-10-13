import unittest
from src.ingestion.chunker import chunk_text


class ChunkerTests(unittest.TestCase):
    def test_empty_text(self):
        self.assertEqual(chunk_text("   "), [])

    def test_chunks_cover_text(self):
        text = "palavra " * 100
        chunks = chunk_text(text, chunk_size=80, overlap=10)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(chunks))

    def test_invalid_overlap(self):
        with self.assertRaises(ValueError):
            chunk_text("texto", chunk_size=10, overlap=10)


if __name__ == "__main__":
    unittest.main()
