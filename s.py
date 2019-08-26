from flask import Flask
from flask import jsonify
from flask import request
import json
import uuid
import sqlite3
from sqlite3 import Error
import sys
import datetime
from datetime import datetime, timedelta

app = Flask(__name__)

# MODELS
# -----------------------------------------------------------------------------------------#
class Data(object):
    def __init__(self, name, age, height, gender, job):
        self.name = name
        self.age = age
        self.height = height
        self.gender = gender
        self.job = job

    def toJSON(self):
        return json.dumps(self.__dict__)

class LoginCredentials(object):
    email = ""
    password = ""
    token = ""

class RegisterCredentials(object):
    name = ""
    password = ""
    email = ""
    protein = ""
    carbs = ""
    fats = ""
    token = ""
    token_expiry = ""
    token_issue = ""
# -----------------------------------------------------------------------------------------#

# ROUTE METHODS ( NON SQLITE )
# -----------------------------------------------------------------------------------------#
def convertToObjectFromJsonLogin(data, headers):
    user = LoginCredentials()
    loadedJson = json.loads(data)
    user.email = loadedJson["email"]
    user.password = loadedJson["password"]

    if ("Authorization" in headers):
    	user.token = headers["Authorization"]
    	return user
    else:
    	return user

def convertToObjectFromJsonRegister(data):
        user = RegisterCredentials()
        loadedJson = json.loads(data)
        user.name = loadedJson["name"]
        user.email = loadedJson["email"]
        user.password = loadedJson["password"]
        user.protein = loadedJson["protein"]
        user.carbs = loadedJson["carbohydrates"]
        user.fats = loadedJson["fats"]

        return user

def userExistsRegister(userData):
    database = "/home/ubuntu/macros.db"
    connection = create_connection(database)

    with connection:
        if(select_user_register(connection, userData)):
        	return True
        else:
        	return False

def userExistsLogin(userData):
	database = "/home/ubuntu/macros.db"
	connection = create_connection(database)

	with connection:
		if(select_user_login(connection, userData)):
			return True
		else:
			return False
# -----------------------------------------------------------------------------------------#

# ROUTE METHODS ( SQLITE )
# -----------------------------------------------------------------------------------------#
def updateRecordToken(userRecord):

	try:
		database = "/home/ubuntu/macros.db"
		conn = create_connection(database)

		sql = ''' UPDATE userCreds SET token = ?, token_expiry_date = ?, token_issue_date = ? WHERE email = ?'''

		cur = conn.cursor()
		cur.execute(sql, userRecord)
		conn.commit()

		return True
	except Error as e:
		return False

def insertUser(userRecord):
	database = "/home/ubuntu/macros.db"
	conn = create_connection(database)

	sql = ''' INSERT INTO userCreds(name, password, email, protein, carbs, fats, token, token_issue_date, token_expiry_date) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?) '''

	cur = conn.cursor()
	cur.execute(sql, userRecord)
	conn.commit()

	return cur.lastrowid

def select_user_login(connection, userData):
	cursor = connection.cursor()
	cursor.execute("SELECT * FROM userCreds WHERE email like ? AND password like ?", ("%" + userData.email + "%", "%" + userData.password + "%"))

	rows = cursor.fetchall()

	if len(rows) > 0:
		return True
	else:
		return False

def select_user_register(connection, userData):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM userCreds WHERE email=?", (userData.email,))

    rows = cursor.fetchall()

    if len(rows) > 0:
        return True
    else:
        return False

def create_connection(database_file):
    try:
        conn = sqlite3.connect(database_file)
        return conn
    except Error as e:
        print(e)
        sys.exit()

    return None

def create_table(connection, create_table_sql):
    try:
        c = connection.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
        sys.exit()

def createDatabaseAndTables():
    database = "/home/ubuntu/macros.db"

    create_user_credentials_table = """ CREATE TABLE IF NOT EXISTS userCreds (id integer PRIMARY KEY, 
    name text NOT NULL, 
    password text NOT NULL, 
    email text NOT NULL,
    protein integer NOT NULL, 
    carbs integer NOT NULL, 
    fats integer NOT NULL, 
    token text NOT NULL, 
    token_issue_date date NOT NULL, 
    token_expiry_date date NOT NULL); """

    create_progress_table = """ CREATE TABLE IF NOT EXISTS dailyProgress (id integer PRIMARY KEY, 
    protein integer NOT NULL, 
    carbs integer NOT NULL, 
    fats integer NOT NULL, 
    user_id integer NOT NULL,
    FOREIGN KEY (user_id) REFERENCES userCreds (id)); """

    connection = create_connection(database)

    if connection is not None:
    	create_table(connection, create_user_credentials_table)
    	create_table(connection, create_progress_table)
    else:
    	print("Error: cannot create the database connection")
    	sys.exit()
# -----------------------------------------------------------------------------------------#
# ROUTES
# -----------------------------------------------------------------------------------------#
@app.route("/getJSONTest", methods = ['GET'])
def jsonifiedDataTest():
    if request.method == 'GET':
    	testData = Data("Mohammed", "23", "173", "Male", "Android Developer")
    	return testData.toJSON()

    else:
    	return jsonify({"message": "ERROR: Method not allowed."}), 405

@app.route("/getTokenLogin", methods = ['POST'])
def login():
    if request.method == 'POST':
        userLoginData = convertToObjectFromJsonLogin(request.get_data().decode("utf-8"), request.headers)
        # check if user exists or not >> update records
        if userExistsLogin(userLoginData):
            # get today's date, date after one week, and a unique ID
			unique_id = uuid.uuid4().__str__()
			today = datetime.now()
			today_plus_seven = today + timedelta(days = 7)
			updateRecord = (unique_id, today.__str__(), today_plus_seven.__str__(), userLoginData.email)

			if updateRecordToken(updateRecord) == True:
				return unique_id
			else:
				return jsonify({"message": "ERROR: Internal Server Database Error."}), 500
        else:
            return jsonify({"message": "ERROR: User not found."}), 404
    else:
        return jsonify({"message": "ERROR: Method not allowed."}), 405

@app.route("/signup", methods = ['POST'])
def registration():
    if request.method == 'POST':
        userRegistrationData = convertToObjectFromJsonRegister(request.get_data().decode("utf-8"))
        if(userExistsRegister(userRegistrationData)):
            return jsonify({"message": "ERROR: User already exists."}), 409
        else:
        	# get today's date, date after one week, and a unique ID
            today = datetime.now()
            today_plus_seven = today + timedelta(days = 7)
            unique_id = uuid.uuid4().__str__()
            
            # create a user record
            userRecord = (userRegistrationData.name, 
            	userRegistrationData.password, 
            	userRegistrationData.email, 
            	int(userRegistrationData.protein), 
            	int(userRegistrationData.carbs), 
            	int(userRegistrationData.fats), 
            	unique_id, 
            	today.__str__(), 
            	today_plus_seven.__str__())

            # insert user record
            if insertUser(userRecord) == None:
            	return jsonify({"message": "ERROR: Internal Server Database Error."}), 500
            else:
            	# on successful insertion, return the unique ID
            	return unique_id
    else:
        return jsonify({"message": "ERROR: Method not allowed."}), 405

@app.route("/")
def hello():
    return "Welcome to the testing server - Mohammed Bokhari<br><br>There are three available routes:<br><br>13.235.198.182/getJSONTest [GET only]<br>13.235.198.182/getUniqueID [POST only]<br>13.235.198.182/ [GET only]<br><br>Build the Android app using Kotlin"
# -----------------------------------------------------------------------------------------#

# MAIN
# -----------------------------------------------------------------------------------------#
if __name__ == "__main__":
    createDatabaseAndTables()
    app.run("172.26.3.65", "80")
# -----------------------------------------------------------------------------------------#
     