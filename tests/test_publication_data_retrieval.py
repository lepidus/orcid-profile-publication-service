import unittest
import json
import os
from orcid.publication_data_retrieval import PublicationDataRetrieval

class TestPublicationDataRetrieval(unittest.TestCase):

    def setUp(self):
        self.work_data = {
            "title": {'title': {'value': 'Exemplo de Publicação'}, 'subtitle': {'value': 'Um subtítulo interessante'}},
            "journal-title": {'value': 'Revista de Exemplo'}
        }
        self.publication_data_retrieval = PublicationDataRetrieval(self.work_data)
    
    def test_publication_title_retrieval(self):
        expected_title = "Exemplo de Publicação"
        publication_title = self.publication_data_retrieval.get_publication_title()
        self.assertEqual(expected_title, publication_title)
    
    def test_journal_title_retrieval(self):
        expected_title = "Revista de Exemplo"
        journal_title = self.publication_data_retrieval.get_journal_title()
        self.assertEqual(expected_title, journal_title)
    
if __name__ == "__main__":
    unittest.main()