from flask import Flask, request, jsonify, abort, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from flask_migrate import Migrate
import json
import sys
import os

from models import db,  DBHelper, Task, Series, Challenge
from auth import AuthError, requires_auth, AUTH0_AUTHORIZE_URL, AUTH0_LOGOUT

app = Flask(__name__)

database_name = "getoutdoors"
#database_path = os.environ['DATABASE_URL']
#database_path = "postgres://{}/{}".format('localhost:5432', database_name)
database_path = "postgres://tnuafhtklsvdlh:1176aa8def9e229bd09221139e01dfcfbd84a153ff0fd77a9787c310665a62a1@ec2-174-129-254-223.compute-1.amazonaws.com:5432/dfdpv7eca7i8b7"
app.config["SQLALCHEMY_DATABASE_URI"] = database_path
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
db.app = app # this needs to be inserted
#db.create_all()
#migrate
migrate =  Migrate(app, db)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route('/')
def index():
  return '<a href="'+AUTH0_AUTHORIZE_URL+'">Login</a>'

@app.route('/logout')
def logout():
    return redirect(AUTH0_LOGOUT) 


@app.route('/login-results', methods=['GET'])
def login_results():
    return (jsonify({'message': 'successful login'}))

@app.route('/tasks', methods=['GET'])
@requires_auth()
def get_tasks(jwt):
    tasks = Task.query.all()

    result = []
    for task in tasks:
        result.append({
            'id': task.id,
            'name': task.name,
            'state': task.state,
            'country': task.country
        })
    
    return jsonify({
                'tasks':result
             })

@app.route('/tasks', methods=['POST'])
@requires_auth('post:tasks:series:challenges')
def create_task(jwt):
    data = request.get_json()
    error = False
    try:
        task = Task(name=data["name"],
                state=data["state"],
                country=data["country"])
    
        isTest = False
        if "isTest" in data:
            isTest = data["isTest"]
    
        DBHelper.insert(task, isTest)
    except:
        DBHelper.rollback()
        error = True
    finally:
        DBHelper.close()
    
    if error:
        abort(404)
    return jsonify({
      "success": True
    })


@app.route('/task/<task_id>', methods=['GET'])
@requires_auth()
def get_task(jwt, task_id):
    error = False

    task = Task.query.get(task_id)
    if task is None:
        abort(404)

    return jsonify({
            'id': task.id,
            'name': task.name,
            'state': task.state,
            'country': task.country
        })

@app.route('/task/<task_id>', methods=['PATCH'])
@requires_auth('patch:tasks:series:challenges')
def update_task(jwt, task_id):
    data = request.get_json()
    error = False
    try:
        task = Task.query.get(task_id)
        if task is None:
            error = True
        else:
            if "name" in data:
                task.name = data["name"]
            if "state" in data:
                task.state = data["state"]
            if "country" in data:
                task.country = data["country"]
            DBHelper.update()
    except:
        print(sys.exc_info())
        DBHelper.rollback()
        error = True
    finally:
        DBHelper.close()
    if error:
        abort(404)
    return jsonify({
      "success": True
    })

@app.route('/task/<task_id>', methods=['DELETE'])
@requires_auth('delete:tasks:series:challenges')
def delete_task(jwt, task_id):
    error = False
    try:
        task = Task.query.get(task_id)
        if task is None:
            error = True
        else:
            DBHelper.delete(task)
    except:
        DBHelper.rollback()
        erro = True
    finally:
        DBHelper.close()
    if error:
        abort(404)
    return jsonify({
      "success": True
    })






@app.route('/series', methods=['GET'])
@requires_auth()
def get_series(jwt):
    series = Series.query.all()

    result = []
    for s in series:
        result.append({
            'id': s.id,
            'name': s.name,
            'description': s.description
        })
    return jsonify({
            'series':result
        })

@app.route('/series', methods=['POST'])
@requires_auth('post:tasks:series:challenges')
def create_series(jwt):
    data = request.get_json()
    error = False
    try:
        series = Series(name=data["name"],
                  description=data["description"]
                )
        isTest = False
        if "isTest" in data:
            isTest = data["isTest"]
        DBHelper.insert(series)
    except:
        DBHelper.rollback()
        error = True
    finally:
        DBHelper.close()
    if error:
        abort(404)
    return jsonify({
      "success": True
    })

@app.route('/serie/<series_id>', methods=['GET'])
@requires_auth()
def get_serie(series_id):
    serie = Series.query.get(series_id)
    if serie is None:
        abort(404)
    result = []
    challenges = serie.challenges

    tasks = []
    for challenge in challenges:
        task = challenge.task
        tasks.append({
            "id": task.id,
            "name": task.name,
            "state": task.state,
            "country": task.country
        })

    return jsonify({
            'id': serie.id,
            'name': serie.name,
            'description': serie.description,
            'tasks' : tasks
        })

@app.route('/series/<series_id>', methods=['PATCH'])
@requires_auth('patch:tasks:series:challenges')
def update_series(jwt, series_id):
    error = False
    data = request.get_json()
    try:
        series = Series.query.get(series_id)
        if series is None:
            error = True
        else:
            if "name" in data:
                series.name = data["name"]
            if "description" in data:
                series.state = data["description"]

        DBHelper.update()
    except:
        print(sys.exc_info())
        DBHelper.rollback()
        error = True
    finally:
        DBHelper.close()
    if error:
        abort(404)
    return jsonify({
      "success": True
    })

@app.route('/series/<series_id>', methods=['DELETE'])
@requires_auth('delete:tasks:series:challenges')
def delete_series(jwt, series_id):
    error = False
    try:
        series = Series.query.get(series_id)
        if series is None:
            error = True
        else:
            DBHelper.delete(series)
    except:
        DBHelper.rollback()
        error = True
    finally:
        DBHelper.close()
    if error:
        abort(404)
    return jsonify({
      "success": True
    })

@app.route('/challenges', methods=['POST'])
@requires_auth('post:tasks:series:challenges')
def create_challenge(jwt):
    data = request.get_json() 
    error = False
    try:
        challenge = Challenge(task_id=data["task_id"],
                         series_id=data["series_id"]
                )
        isTest = False
        if "isTest" in data:
            isTest = data["isTest"]
        DBHelper.insert(challenge)
    except:
        DBHelper.rollback()
        error = True
    finally:
        DBHelper.close()
    if error:
        abort(404)
    return jsonify({
      "success": True
    })

@app.route('/challenge/<challenge_id>', methods=['PATCH'])
@requires_auth('patch:tasks:series:challenges')
def update_challenge(jwt, challenge_id):
    data = request.get_json()
    error = False
    try:
        challenge = Challenge.query.get(challenge_id)
        if challenge is None:
            error = True
        else:
            if "task_id" in data and "series_id" in data:
                challenge.task_id = data["task_id"]
                challenge.series_id = data["series_id"]

            DBHelper.update()
    except:
        print(sys.exc_info())
        DBHelper.rollback()
        error = True
    finally:
        DBHelper.close()
    if error:
        abort(404)
    return jsonify({
      "success": True
    })

@app.route('/challenge/<challenge_id>', methods=['DELETE'])
@requires_auth('delete:tasks:series:challenges')
def delete_challenge(jwt, challenge_id):
    error = False
    try:
        challenge = Challenge.query.get(challenge_id)
        if challenge is None:
            error = True
        else:
            DBHelper.delete(challenge)
    except:
        DBHelper.rollback()
        error = True
    finally:
        DBHelper.close()
    if error:
        abort(404)
    return jsonify({
      "success": True
    })


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404


@app.errorhandler(AuthError)
def processAuthError(error):
    message = [str(x) for x in error.args]
    status_code = error.status_code

    return jsonify({
                    "success": False, 
                    "error": status_code,
                    "message": message
                    }), status_code

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''