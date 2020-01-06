# APP ON HEROKU
https://outdoorschallenge.herokuapp.com/
https://outdoorschallenge.herokuapp.com/login-results

https://outdoorschallenge.herokuapp.com/logout



Tasks
- A collection of mountains that people can summit
example: mount washington, mount everest, katahdin, ....

Series
- A collection of tasks
- tasks could belong to multiple series

Tasks and Series are associated by relationships through the postgres table Challenges

Tables are Tasks, Series and Challenges



# ROLES
username, password
'admin@abc.com', 'admin123&' {Can create, read, update, delete tasks, series and challenges}

'user@abc.com', 'user123&' {can get tasks and series} No Permissions required but they still need to be authenticated with a valid token to get the tasks and sereis


# POSTMAN Collection
GetOutdoors.postman_collection.json
has all the requests. You may need to pass in the correct token


# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 


## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application.
