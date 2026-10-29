import unittest
from app import app
from database import initialize_database

class AssistantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_database()
    def setUp(self):
        self.client=app.test_client()
    def test_health(self):
        self.assertEqual(self.client.get('/api/health').status_code,200)
    def test_total_revenue(self):
        r=self.client.post('/api/ask',json={'question':'What is the total revenue?'})
        self.assertEqual(r.status_code,200); self.assertIn('total_revenue',r.get_json()['data'])
    def test_top_product(self):
        r=self.client.post('/api/ask',json={'question':'Which product generated the highest revenue?'})
        self.assertEqual(r.status_code,200); self.assertTrue(r.get_json()['data'])
    def test_monthly_trend(self):
        r=self.client.post('/api/ask',json={'question':'Show the monthly revenue trend'})
        self.assertEqual(r.status_code,200); self.assertEqual(len(r.get_json()['data']),6)
    def test_compare_months(self):
        r=self.client.post('/api/ask',json={'question':'Compare revenue between January and February'})
        self.assertEqual(r.status_code,200); self.assertEqual(len(r.get_json()['data']),2)
    def test_unsupported_question(self):
        r=self.client.post('/api/ask',json={'question':'What is the weather today?'})
        self.assertEqual(r.status_code,400)
    def test_empty_question(self):
        r=self.client.post('/api/ask',json={'question':'   '})
        self.assertEqual(r.status_code,400)
    def test_bad_request_shape(self):
        r=self.client.post('/api/ask',json={})
        self.assertEqual(r.status_code,400)

if __name__=='__main__': unittest.main()
