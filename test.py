import unittest
import os
import json
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from models import setup_db, Cases, Donations, Donors, Services
from app import create_app



class TestCapstone(unittest.TestCase):
    aministrator_token = os.environ['aministrator_token']
    donor_token = os.environ['donor_token']
    case = {"issuer": "Dallah",
                    "services": [
                    {"description":"test1",
                    "amount":200,"quantity":1},
                    {"description":"test3","amount":100,
                    "quantity":1}],
                    "number": "98709",
                    "total_amount": 300.0
                    }

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = os.environ['TEST_DATABASE_URL']
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.drop_all()
            # create all tables
            self.db.create_all()

    
    def tearDown(self):
        pass
    
    def test_admin_add_case(self):
        response = self.client().post('/cases',  headers={'authorization': 'Bearer ' + self.aministrator_token}, json=self.case)
        data = json.loads(response.data)
        added_case = Cases.query.filter_by(number=self.case['number']).first()
        # print(data)
        self.assertTrue(data['success'])
        self.assertTrue(added_case)

    
    def test_donor_add_case(self):
        response = self.client().post('/cases',  headers={'authorization': 'Bearer ' + self.donor_token}, json=self.case)
        data = json.loads(response.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 403)
    

    def test_get_cases(self):
        response = self.client().get('/cases')
        data = json.loads(response.data)
        self.assertEqual(data['success'], True)
    
    def test_get_case_by_id(self):
        response = self.client().get('/cases/1', headers={'authorization': 'Bearer ' + self.aministrator_token})
        data = json.loads(response.data)
        self.assertEqual(data['success'], True)
    
    def test_not_found_get_case_by_id(self):
        case = Cases.query.get(1000)
        if case is None:
            response = self.client().get('/cases/1000', headers={'authorization': 'Bearer ' + self.aministrator_token})
            data = json.loads(response.data)
            self.assertEqual(data['success'], False)
            self.assertEqual(data['message'], 'resource is not found')
            self.assertEqual(response.status_code, 404)

    def test_admin_get_donations(self):
        response = self.client().get('/donations', headers={'authorization': 'Bearer ' + self.aministrator_token})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)

    
    def test_donor_get_donations(self):
        response = self.client().get('/donations', headers={'authorization': 'Bearer ' + self.donor_token})
        data = json.loads(response.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 403)
    
    def test_not_found_patch_case(self):
        case = Cases.query.get(1000)
        if case is None:
            response = self.client().patch('/cases/1000',  headers={'authorization': 'Bearer ' + self.donor_token}, json={"amount":'200'})
            data = json.loads(response.data)
            self.assertEqual(data['success'], False)
            self.assertEqual(data['message'], "resource is not found")
            self.assertEqual(response.status_code, 404)
    
    def test_successed_patch_case(self):
        case = Cases.query.get(1)
        if case is None:
            response = self.client().patch('/cases/1',  headers={'authorization': 'Bearer ' + self.donor_token})
            data = json.loads(response.data)
            self.assertEqual(data['success'], True)
            self.assertEqual(response.status_code, 200)
    
    def test_not_found_delete_case(self):
        case = Cases.query.get(1000)
        if case is None:
            response = self.client().delete('/cases/1000',  headers={'authorization': 'Bearer ' + self.aministrator_token})
            data = json.loads(response.data)
            self.assertEqual(data['success'], False)
            self.assertEqual(data['message'], "resource is not found")
            self.assertEqual(response.status_code, 404)
    
    def test_successed_delete_case(self):
        case = Cases.query.get(2)
        if case is None:
            response = self.client().delete('/cases/2',  headers={'authorization': 'Bearer ' + self.aministrator_token})
            data = json.loads(response.data)
            self.assertEqual(data['success'], True)
            self.assertEqual(response.status_code, 200) 


if __name__ == "__main__":
    unittest.main()
