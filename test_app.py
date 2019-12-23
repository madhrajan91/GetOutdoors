import os
import unittest
import json
import sys
import requests
from flask_sqlalchemy import SQLAlchemy

from app import app
from models import db, DBHelper, Task, Series, Challenge


testingUsers = {
    'admin@abc.com': 'admin123&',
    'challengecreator@abc.com': 'challenger123&'
}


def getUserToken(userName):
    # client id and secret come from LogIn (Test Client)! which has password enabled under "Client > Advanced > Grant Types > Tick Password"
    url = 'https://dev-identityaccess.auth0.com/authorize/oauth/token' 
    headers = {'content-type': 'application/json'}
    password = testingUsers[userName]
    parameter = { "client_id":"7r6p7YLCRNJnQeuOk5zMqwPrsJeDDQMo", 
                  "client_secret": "DraGIpcwxdHrTtkbS-reRT0wTIC_D368oQB3Wx7sOsWQeruqLbX_bqGub1h1fhzN",
                  "audience": 'outdoors',
                  "connection":"Username-Password-Authentication",
                  "grant_type": "password",
                  "username": userName,
                  "password": password, "scope": "openid" } 
    # do the equivalent of a CURL request from https://auth0.com/docs/quickstart/backend/python/02-using#obtaining-an-access-token-for-testing
    responseDICT = json.loads(requests.post(url, json=parameter, headers=headers).text)
    return responseDICT['access_token']

#@memoize # memoize code from: https://stackoverflow.com/a/815160
def getUserTokenHeaders(userName='admin@abc.com'):
    return { 'authorization': "Bearer " + getUserToken(userName)} 

class GetOutdoorsCase(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = self.app.test_client()

    def tearDown(self):

        challenges = Challenge.query.filter(Challenge.isTest == True)
        for challenge in challenges:
            DBHelper.delete(challenge)
        
        series = Series.query.filter(Series.isTest == True)
        for serie in series:
            DBHelper.delete(serie)

        tasks = Task.query.filter(Task.isTest == True)
        for task in tasks:
            DBHelper.delete(task)
    
    def createEntity(self, entity):
        result = {}
        try:
            DBHelper.insert(entity, True)
            result  = {
                        "id": entity.id
                      }
        except:
            DBHelper.rollback()
            print(sys.exc_info())
        finally:
            DBHelper.close()
        return result

    
    def createTask(self, name="testTask2"):
        task = Task(name= name, state= "AZ", country="USA")
        return self.createEntity(task)
    
    def  createSeries(self, name="testSeries"):
        series = Series(name= name, description= "abc")
        return self.createEntity(series)


    def test_get_tasks_unauthorized(self):
        res = self.client.get("/tasks")
        self.assertEqual(res.status_code, 401)



    def test_get_tasks_authorized(self):
        self.client.environ_base['HTTP_AUTHORIZATION'] = getUserTokenHeaders()['authorization']
        res = self.client.get("/tasks")
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)

    def test_create_tasks_authorized(self):
        print('create task')
        self.client.environ_base['HTTP_AUTHORIZATION'] = getUserTokenHeaders()['authorization']
        res = self.client.post("/tasks",
                                data=json.dumps({
                                    "name": "testTask",
                                    "state": "testState",
                                    "country": "testCountry",
                                    "isTest": True
                                }),  content_type="application/json")
        self.assertEqual(res.status_code, 200)
       
        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], True)
        

    def test_patch_task_authorized(self):
        print('patch task')
        task = self.createTask()
    
        self.client.environ_base['HTTP_AUTHORIZATION'] = getUserTokenHeaders()['authorization']
        res = self.client.patch("/task/"+str(task["id"]),
                                data=json.dumps({
                                    "name": "Aggasiz"
                                }),  content_type="application/json")
        self.assertEqual(res.status_code, 200)

        
        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], True)

        updatedTask = Task.query.get(task["id"])
        self.assertEqual(updatedTask.name,"Aggasiz")
    
    def test_delete_task_authorized(self):
        self.client.environ_base['HTTP_AUTHORIZATION'] = getUserTokenHeaders()['authorization']

        print('delete task')
        task =  self.createTask()
        res = self.client.delete("/task/"+str(task["id"]))

        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], True)
        self.assertEqual(len(Task.query.filter(Task.id == task["id"]).all()), 0)

    def test_get_series(self):
        self.client.environ_base['HTTP_AUTHORIZATION'] = getUserTokenHeaders()['authorization']
        res = self.client.get("/series")
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)


    def test_create_series_authorized(self):
        print('create series')
        self.client.environ_base['HTTP_AUTHORIZATION'] = getUserTokenHeaders()['authorization']

        res = self.client.post("/series",
                                data=json.dumps({
                                    "name": "testSeries",
                                    "description": "testState"
                                }),  content_type="application/json")
        self.assertEqual(res.status_code, 200)
       
        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], True)

    def test_patch_series_authorized(self):
        print('patch series')
        series =  self.createSeries()
        self.client.environ_base['HTTP_AUTHORIZATION'] = getUserTokenHeaders()['authorization']

        res = self.client.patch("/series/"+str(series["id"]),
                                data=json.dumps({
                                    "name": "World Mountain"
                                }),  content_type="application/json")
        self.assertEqual(res.status_code, 200)

        
        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], True)

        updatedSeries = Series.query.get(series["id"])
        self.assertEqual(updatedSeries.name,"World Mountain")

  
    def test_delete_series_authorized(self):
        print('delete series')
        series =  self.createSeries()
        self.client.environ_base['HTTP_AUTHORIZATION'] = getUserTokenHeaders()['authorization']
        res = self.client.delete("/series/"+str(series["id"]))

        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], True)
        self.assertEqual(len(Series.query.filter(Series.id == series["id"]).all()), 0)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()