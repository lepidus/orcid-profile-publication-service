import unittest
from unittest.mock import patch, Mock
from orcid_client import OrcidClient

class TestOrcidClient(unittest.TestCase):

    def setUp(self):
        self.client = OrcidClient("fake_client_id", "fake_client_secret", "http://localhost/redirectUrlExample")
    
    @patch('orcid_client.requests.post')
    def test_get_orcid_id_and_access_token_with_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "fake_token",
            "orcid": "0000-0000-0000-0000"
        }
        mock_post.return_value = mock_response

        token_info = self.client.get_orcid_id_and_access_token("mock_auth_code")

        self.assertEqual(token_info["access_token"], "fake_token")
        self.assertEqual(token_info["orcid"], "0000-0000-0000-0000")
    
if __name__ == "__main__":
    unittest.main()