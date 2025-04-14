import unittest
from utils.publication_data_retrieval import PublicationDataRetrieval

class TestPublicationDataRetrieval(unittest.TestCase):

    def setUp(self):
        self.work_data = {
            "title": {'title': {'value': 'Exemplo de Publicação'}, 'subtitle': {'value': 'Um subtítulo interessante'}},
            "journal-title": {'value': 'Revista de Exemplo'},
            "external-ids": {
                "external-id": [
                    {
                        "external-id-type": "doi",
                        "external-id-value": "10.1000/xyz123",
                        "external-id-url": {"value": "http://example.com"}
                    }
                ]
            },
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
    
    def test_external_id_retrieval(self):
        expected_external_id = "10.1000/xyz123"
        external_id = self.publication_data_retrieval.get_external_id()
        self.assertEqual(expected_external_id, external_id)
    
if __name__ == "__main__":
    unittest.main()