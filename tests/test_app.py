import unittest
from app import app

class AppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Git Repository Analysis', response.data)

    def test_config_route(self):
        response = self.app.get('/config')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Config Management', response.data)

if __name__ == '__main__':
    unittest.main()
