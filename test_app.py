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
    'user@abc.com': 'user123&'
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

        series = Series.query.filter(Series.name.contains("test"))
        for serie in series:
            DBHelper.delete(serie)

        tasks = Task.query.filter(Task.isTest == True).filter(Series.name.contains("test"))
        for task in tasks:
            DBHelper.delete(task)

        asks = Task.query.filter(Task.name.contains("test"))
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

    '''
    Create dummy tasks series challenges
    '''
    def createTask(self, name="testTask2"):
        task = Task(name=name, state= "AZ", country="USA")
        return self.createEntity(task)
    
    def  createSeries(self, name="testSeries"):
        series = Series(name=name, description= "abc")
        return self.createEntity(series)

    def createChallenge(self):
        task = self.createTask()
        series = self.createSeries()
        challenge = Challenge(task_id = task["id"], series_id = series["id"])
        return self.createEntity(challenge)

    # unauthorized user = failed
    # user must be logged in
    def test_get_tasks_unauthorized(self):
        res = self.client.get("/tasks")
        self.assertEqual(res.status_code, 401)


    # get tasks
    def test_get_tasks_admin_authorized(self):
        print('get tasks by admin')
        self.client.environ_base['HTTP_AUTHORIZATION'] = getUserTokenHeaders()['authorization']
        res = self.client.get("/tasks")
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        self.assertNotEqual(data["tasks"], [])

    def test_get_tasks_authorized_user(self):
        print('get tasks by user')
        # positive
        self.client.environ_base['HTTP_AUTHORIZATION'] = getUserTokenHeaders('user@abc.com')['authorization']
        res = self.client.get("/tasks")
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        self.assertNotEqual(data["tasks"], [])

    def test_get_task_authorized(self):
        print('get task by id')

        task = self.createTask()
    
        self.client.environ_base['HTTP_AUTHORIZATION'] = getUserTokenHeaders()['authorization']
        res = self.client.get("/task/"+str(task["id"]),)
        self.assertEqual(res.status_code, 200)

        
        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["name"], "testTask2")
        self.assertEqual(data["state"], "AZ")
        self.assertEqual(data["country"], "USA")
    
    def test_create_tasks_user_unauthorized(self):
        print('create task user negative')
        # positive
        self.client.environ_base['HTTP_AUTHORIZATION'] = getUserTokenHeaders('user@abc.com')['authorization']
        res = self.client.post("/tasks",
                                data=json.dumps({
                                    "name": "testTask",
                                    "state": "testState",
                                    "country": "testCountry",
                                    "isTest": True
                                }),  content_type="application/json")
        # user cannot create
        # they must see a 403 permission error
        self.assertEqual(res.status_code, 403)
       
    def test_create_tasks_authorized(self):
        print('create task')
        # positive
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

        # failure
        res = self.client.post("/tasks",
                                data=json.dumps({ # no name
                                    "country": "testCountry",
                                    "isTest": True
                                }),  content_type="application/json")
        self.assertEqual(res.status_code, 404)
       
        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], False)

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

        #negative
        res = self.client.patch("/task/-1",
                                data=json.dumps({
                                    "name": "Aggasiz"
                                }),  content_type="application/json")
        self.assertEqual(res.status_code, 404)

        
        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], False)

    
    def test_delete_task_authorized(self):
        self.client.environ_base['HTTP_AUTHORIZATION'] = getUserTokenHeaders()['authorization']

        print('delete task')
        task =  self.createTask()
        res = self.client.delete("/task/"+str(task["id"]))

        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], True)
        self.assertEqual(len(Task.query.filter(Task.id == task["id"]).all()), 0)

        # negative
        res = self.client.delete("/task/-1")
        self.assertEqual(res.status_code, 404)

        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], False)
 
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
                                    "description": "testState",
                                    "isTest": True
                                }),  content_type="application/json")
        self.assertEqual(res.status_code, 200)
       
        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], True)

        # negative
        res = self.client.post("/series",
                                data=json.dumps({
                                    "description": "testState"
                                }),  content_type="application/json")
        self.assertEqual(res.status_code, 404)
       
        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], False)

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


        #negative
        res = self.client.patch("/series/-1",
                                data=json.dumps({
                                    "name": "World Mountain"
                                }),  content_type="application/json")
        self.assertEqual(res.status_code, 404)

        
        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], False)

  
    def test_delete_series_authorized(self):
        print('delete series')
        series =  self.createSeries()
        self.client.environ_base['HTTP_AUTHORIZATION'] = getUserTokenHeaders()['authorization']
        res = self.client.delete("/series/"+str(series["id"]))

        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], True)
        self.assertEqual(len(Series.query.filter(Series.id == series["id"]).all()), 0)

        # negative
        res = self.client.delete("/series/-1")

        data = json.loads(res.data)
        #verify response data
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_create_challenge_authorized(self):
        print('create challenge')

        task =  self.createTask()
        series =  self.createSeries()

        self.client.environ_base['HTTP_AUTHORIZATION'] = getUserTokenHeaders()['authorization']

        res = self.client.post("/challenges",
                                data=json.dumps({
                                    "task_id": str(task["id"]),
                                    "series_id": str(series["id"]),
                                    "isTest": True
                                }),  content_type="application/json")
        self.assertEqual(res.status_code, 200)
       
        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], True)

        # negative
        res = self.client.post("/challenges",
                                data=json.dumps({
                                    "series_id": str(series["id"])
                                }),  content_type="application/json")
        self.assertEqual(res.status_code, 404)
       
        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], False)

    def test_patch_challenge_authorized(self):
        print('patch challenge')
        challenge =  self.createChallenge()

        orgChallenge = Challenge.query.get(challenge["id"])
        self.client.environ_base['HTTP_AUTHORIZATION'] = getUserTokenHeaders()['authorization']

        self.assertEqual(orgChallenge.task.name, "testTask2")
        orgSeriesId = orgChallenge.series_id

        # update the task in the challenge
        newTask = self.createTask("UpdatedTask")

        
        res = self.client.patch("/challenge/"+str(challenge["id"]),
                                data=json.dumps({
                                    "task_id": str(newTask["id"]),
                                    "series_id": str(orgSeriesId)
                                }),  content_type="application/json")
        self.assertEqual(res.status_code, 200)

        
        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], True)

        updatedChallenge = Challenge.query.get(challenge["id"])
        self.assertEqual(updatedChallenge.task.name, "UpdatedTask")

        # negative
        res = self.client.patch("/challenge/-1",
                                data=json.dumps({
                                    "series_id": str(orgSeriesId)
                                }),  content_type="application/json")
        self.assertEqual(res.status_code, 404)

        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], False)


    def test_delete_challenge_authorized(self):
        print('delete challenge')
        challenge =  self.createChallenge()
        self.client.environ_base['HTTP_AUTHORIZATION'] = getUserTokenHeaders()['authorization']
        res = self.client.delete("/challenge/"+str(challenge["id"]))

        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], True)
        self.assertEqual(len(Challenge.query.filter(Challenge.id == challenge["id"]).all()), 0)

        res = self.client.delete("/challenge/-1")
        self.assertEqual(res.status_code, 404)

        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], False)
        self.assertEqual(len(Challenge.query.filter(Challenge.id == challenge["id"]).all()), 0)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()