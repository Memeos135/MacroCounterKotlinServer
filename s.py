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

class FetchCredentials(object):
    email = ""
    password = ""
    token = ""

class FetchData(object):
    def __init__(self, protein_progress, carbs_progress, fats_progress):
        self.protein_progress = protein_progress
        self.carbs_progress = carbs_progress
        self.fats_progress = fats_progress

    def toJSON(self):
        return json.dumps(self.__dict__)

class LoginData(object):
    def __init__(self, ids, email, protein_goal, carbs_goal, fats_goal, protein_progress, carbs_progress, fats_progress):
        self.id = ids
        self.email = email
        self.protein_goal = protein_goal
        self.carbs_goal = carbs_goal
        self.fats_goal = fats_goal
        self.protein_progress = protein_progress
        self.carbs_progress = carbs_progress
        self.fats_progress = fats_progress

    def toJSON(self):
        return json.dumps(self.__dict__)
# -----------------------------------------------------------------------------------------#

# ROUTE METHODS ( NON SQLITE )
# -----------------------------------------------------------------------------------------#
def checkDate(token_expiry_unformat):
    token_expiry_formatted = token_expiry_unformat[0]
    expiry_datetime = datetime.strptime(token_expiry_formatted, "%Y-%m-%d %H:%M:%S.%f")

    if expiry_datetime > datetime.now():
        return True
    else:
        return False

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

def convertToObjectFromJsonFetch(data):
    user = FetchCredentials()
    loadedJson = json.loads(data)
    user.email = loadedJson["email"]
    user.password = loadedJson["password"]

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

        sql = ''' UPDATE userCreds SET token = ?, token_issue_date = ?, token_expiry_date = ? WHERE email = ?'''

        cur = conn.cursor()
        cur.execute(sql, userRecord)
        conn.commit()

        return True
    except Error as e:
        return False

def insertDailyDefaults(userData):
    try:
        database = "/home/ubuntu/macros.db"
        conn = create_connection(database)

        sql = ''' INSERT INTO dailyProgress(protein, carbs, fats, dates, user_id) VALUES (?, ?, ?, ?, ?) '''

        cur = conn.cursor()
        cur.execute(sql, userData)
        conn.commit()
        return cur.lastrowid

    except Error as e:
        return None

def insertUser(userRecord):
    try:
        database = "/home/ubuntu/macros.db"
        conn = create_connection(database)

        sql = ''' INSERT INTO userCreds(name, password, email, protein, carbs, fats, token, token_issue_date, token_expiry_date) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?) '''

        cur = conn.cursor()
        cur.execute(sql, userRecord)
        conn.commit()
        return cur.lastrowid

    except Error as e:
        return None

def select_goal_info(userData):
    database = "/home/ubuntu/macros.db"
    connection = create_connection(database)

    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT protein, carbs, fats FROM userCreds WHERE email like ? AND password like ?", ("%" + userData.email + "%", "%" + userData.password + "%"))

        rows = cursor.fetchall()
        myList = []

        for protein, carbs, fat in rows:
            myList.append(protein)
            myList.append(carbs)
            myList.append(fat)

        return myList

def select_user_id(userData):
    database = "/home/ubuntu/macros.db"
    connection = create_connection(database)

    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM userCreds WHERE email like ? AND password like ?", ("%" + userData.email + "%", "%" + userData.password + "%"))

        rows = cursor.fetchone()

        return rows

def select_token_expiry(userFetchData):
    database = "/home/ubuntu/macros.db"
    connection = create_connection(database)

    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT token_expiry_date FROM userCreds WHERE email like ? AND password like ?", ("%" + userFetchData.email + "%", "%" + userFetchData.password + "%"))

        rows = cursor.fetchone()
        return rows

def select_progress_info(userData, today):
    user_id = select_user_id(userData)[0]

    database = "/home/ubuntu/macros.db"
    connection = create_connection(database)

    if user_id != None:
        with connection:
            cursor = connection.cursor()
            cursor.execute("SELECT protein, carbs, fats FROM dailyProgress WHERE user_id like ? AND dates like ?", (user_id, "%" + today + "%"))

            rows = cursor.fetchall()
            myList = []

            for protein, carbs, fats in rows:
                myList.append(protein)
                myList.append(carbs)
                myList.append(fats)

            return myList
    else:
        return None

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
    protein integer NOT NULL DEFAULT 0,
    carbs integer NOT NULL DEFAULT 0,
    fats integer NOT NULL DEFAULT 0,
    dates text NOT NULL,
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
@app.route("/getSpecificDayProgress", methods=['POST'])
def getSpecificDayProgress():
    if(request.method == 'POST'):
        print("ON HOLD - GET SPECIFIC DAY")
    else:
        return jsonify({"message": "ERROR: Method not allowed."}), 405

@app.route("/postGoalUpdate", methods=['POST'])
def postGoalUpdate():
    if(request.method == 'POST'):
        print("ON HOLD - POST GOAL UPDATE")
    else:
        return jsonify({"message": "ERROR: Method not allowed."}), 405

@app.route("/postDailyProgress", methods=['POST'])
def postDailyProgress():
    if(request.method == 'POST'):
        print("ON HOLD - POST DAILY PROGRESS")
    else:
        return jsonify({"message": "ERROR: Method not allowed."}), 405

@app.route("/getDailyProgress", methods=['POST'])
def getDailyProgress():
    if(request.method == 'POST'):
        # get email/password/token in object format
        # compare received token with DB token expiry date - if not expired, proceed. Else, refuse.
        # return the new token + the dailyProgress values
        userFetchData = convertToObjectFromJsonFetch(request.get_data().decode("utf-8"))
        tokenExpiryDate = select_token_expiry(userFetchData)

        if tokenExpiryDate != None:
            # check token expiry date with today's date
            if(checkDate(tokenExpiryDate)):
                today = datetime.now()
                getProgressInfo = select_progress_info(userFetchData, today.strftime('%Y-%m-%d').__str__())

                if getProgressInfo != []:
                    fetchData = FetchData(getProgressInfo[0], getProgressInfo[1], getProgressInfo[2])
                    return fetchData.toJSON()
                else:
                    user_id = select_user_id(userFetchData)
                    dailyProgressUserRecord = (0, 0, 0, today.strftime('%Y-%m-%d').__str__(), user_id[0])

                    if(insertDailyDefaults(dailyProgressUserRecord) == None):
                        return jsonify({"message": "ERROR: Internal Server Database Error."}), 500
                    else:
                        getProgressInfo = select_progress_info(userFetchData, today.strftime('%Y-%m-%d').__str__())

                        if getProgressInfo != []:
                            fetchData = FetchData(getProgressInfo[0], getProgressInfo[1], getProgressInfo[2])
                            return fetchData.toJSON()
                        else:
                            return jsonify({"message": "ERROR: Internal Server Database Error."}), 500
            else:
                unique_id = uuid.uuid4().__str__()
                today = datetime.now()
                today_plus_seven = today + timedelta(days = 7)
                updateRecord = (unique_id, today.__str__(), today_plus_seven.__str__(), userFetchData.email)

                if updateRecordToken(updateRecord) == True:
                    getProgressInfo = select_progress_info(userFetchData, today.strftime('%Y-%m-%d').__str__())

                    if getProgressInfo != []:
                        fetchData = FetchData(getProgressInfo[0], getProgressInfo[1], getProgressInfo[2])
                        return fetchData.toJSON()
                    else:
                        user_id = select_user_id(userFetchData)
                        dailyProgressUserRecord = (0, 0, 0, today.strftime('%Y-%m-%d').__str__(), user_id[0])

                        if(insertDailyDefaults(dailyProgressUserRecord) == None):
                            return jsonify({"message": "ERROR: Internal Server Database Error."}), 500
                        else:
                            getProgressInfo = select_progress_info(userFetchData, today.strftime('%Y-%m-%d').__str__())

                            if getProgressInfo != []:
                                fetchData = FetchData(getProgressInfo[0], getProgressInfo[1], getProgressInfo[2])
                                return fetchData.toJSON()
                            else:
                                jsonify({"message": "ERROR: Internal Server Database Error."}), 500
                else:
                    return jsonify({"message": "ERROR: Internal Server Database Error."}), 500
    else:
        return jsonify({"message": "ERROR: Method not allowed."}), 405

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
                getGoalInfo = select_goal_info(userLoginData);
                getProgressInfo = select_progress_info(userLoginData, today.strftime('%Y-%m-%d').__str__())

                if getGoalInfo != []:
                    if getProgressInfo != []:
                        loginData = LoginData(unique_id, userLoginData.email, getGoalInfo[0], getGoalInfo[1], getGoalInfo[2], getProgressInfo[0], getProgressInfo[1], getProgressInfo[2])
                        return loginData.toJSON()
                    else:
                        user_id = select_user_id(userLoginData)
                        dailyProgressUserRecord = (0, 0, 0, today.strftime('%Y-%m-%d').__str__(),user_id[0])

                        if(insertDailyDefaults(dailyProgressUserRecord) == None):
                            return jsonify({"message": "ERROR: Internal Server Database Error."}), 500
                        else:
                            getProgressInfo = select_progress_info(userLoginData, today.strftime('%Y-%m-%d').__str__())

                            if getProgressInfo != []:
                                loginData = LoginData(unique_id, userLoginData.email, getGoalInfo[0], getGoalInfo[1], getGoalInfo[2], getProgressInfo[0], getProgressInfo[1], getProgressInfo[2])
                                return loginData.toJSON()
                            else:
                                jsonify({"message": "ERROR: Internal Server Database Error."}), 500
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
                user_id = select_user_id(userRegistrationData)
                dailyProgressUserRecord = (0, 0, 0, today.strftime('%Y-%m-%d').__str__(),user_id[0])

                if(insertDailyDefaults(dailyProgressUserRecord) == None):
                    return jsonify({"message": "ERROR: Internal Server Database Error."}), 500
                else:
                    getGoalInfo = select_goal_info(userRegistrationData);
                    getProgressInfo = select_progress_info(userRegistrationData, today.strftime('%Y-%m-%d').__str__())

                    if getGoalInfo != [] and getProgressInfo != []:
                        loginData = LoginData(unique_id, userRegistrationData.email, getGoalInfo[0], getGoalInfo[1], getGoalInfo[2], getProgressInfo[0], getProgressInfo[1], getProgressInfo[2])
                        return loginData.toJSON()
                    else:
                        jsonify({"message": "ERROR: Internal Server Database Error."}), 500
    else:
        return jsonify({"message": "ERROR: Method not allowed."}), 405

@app.route("/")
def hello():
    return "Welcome to the testing server - Mohammed Bokhari<br><br>There are three available routes:<br><br>35.154.196.173/getJSONTest [GET only]<br>35.154.196.173/getUniqueID [POST only]<br>35.154.196.173/ [GET only]<br><br>Build the Android app using Kotlin"
# -----------------------------------------------------------------------------------------#

# MAIN
# -----------------------------------------------------------------------------------------#
if __name__ == "__main__":
    createDatabaseAndTables()
    app.run("172.26.3.65", "80")
# -----------------------------------------------------------------------------------------#
