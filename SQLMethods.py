import sqlite3
from sqlite3 import Error
import sys
import json
from Models import *

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
        print(e)
        return False

def updateGoalMacros(userRecord):
    try:
        database = "/home/ubuntu/macros.db"
        conn = create_connection(database)

        sql = ''' UPDATE userCreds SET protein = ?, carbs = ?, fats = ? WHERE email = ? AND password = ?'''
        cur = conn.cursor()
        cur.execute(sql, userRecord)
        conn.commit()

        return True
    except Error as e:
        print(e)
        return False

def update_protein(updateRecord):
    try:
        database = "/home/ubuntu/macros.db"
        conn = create_connection(database)

        sql = ''' UPDATE dailyProgress SET protein = ? WHERE dates = ? AND user_id = ?'''
        cur = conn.cursor()
        cur.execute(sql, updateRecord)
        conn.commit()

        return True
    except Error as e:
        print(e)
        return False

def update_carbs(updateRecord):
    try:
        database = "/home/ubuntu/macros.db"
        conn = create_connection(database)

        sql = ''' UPDATE dailyProgress SET carbs = ? WHERE dates = ? AND user_id = ?'''
        cur = conn.cursor()
        cur.execute(sql, updateRecord)
        conn.commit()

        return True
    except Error as e:
        print(e)
        return False

def update_fats(updateRecord):
    try:
        database = "/home/ubuntu/macros.db"
        conn = create_connection(database)

        sql = ''' UPDATE dailyProgress SET fats = ? WHERE dates = ? AND user_id = ?'''
        cur = conn.cursor()
        cur.execute(sql, updateRecord)
        conn.commit()

        return True
    except Error as e:
        print(e)
        return False

def insert_protein(record):
    try:
        database = "/home/ubuntu/macros.db"
        conn = create_connection(database)

        sql = ''' INSERT INTO dailyProgress(protein, carbs, fats, dates, user_id) VALUES (?, ?, ?, ?, ?) '''

        cur = conn.cursor()
        cur.execute(sql, record)
        conn.commit()
        return cur.lastrowid

    except Error as e:
        print(e)
        return None

def insert_carbs(record):
    try:
        database = "/home/ubuntu/macros.db"
        conn = create_connection(database)

        sql = ''' INSERT INTO dailyProgress(protein, carbs, fats, dates, user_id) VALUES (?, ?, ?, ?, ?) '''

        cur = conn.cursor()
        cur.execute(sql, record)
        conn.commit()
        return cur.lastrowid

    except Error as e:
        print(e)
        return None

def insert_email(record):
    try:
        database = "/home/ubuntu/emails.db"
        conn = create_connection(database)

        sql = ''' INSERT INTO emailTable(name, email, subject, body, dates) VALUES (?, ?, ?, ?, ?) '''

        cur = conn.cursor()
        cur.execute(sql, record)
        conn.commit()
        return cur.lastrowid

    except Error as e:
        print(e)
        return None

def insert_fats(record):
    try:
        database = "/home/ubuntu/macros.db"
        conn = create_connection(database)

        sql = ''' INSERT INTO dailyProgress(protein, carbs, fats, dates, user_id) VALUES (?, ?, ?, ?, ?) '''

        cur = conn.cursor()
        cur.execute(sql, record)
        conn.commit()
        return cur.lastrowid

    except Error as e:
        print(e)
        return None

def select_protein(category, date, user_id):
    database = "/home/ubuntu/macros.db"
    connection = create_connection(database)

    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT protein FROM dailyProgress WHERE dates like ? AND user_id like ?", ("%" + date + "%", user_id))

        rows = cursor.fetchone()

        return rows

def select_carbs(category, date, user_id):
    database = "/home/ubuntu/macros.db"
    connection = create_connection(database)

    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT carbs FROM dailyProgress WHERE dates like ? AND user_id like ?", ("%" + date + "%", user_id))

        rows = cursor.fetchone()

        return rows

def select_fats(category, date, user_id):
    database = "/home/ubuntu/macros.db"
    connection = create_connection(database)

    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT fats FROM dailyProgress WHERE dates like ? AND user_id like ?", ("%" + date + "%", user_id))

        rows = cursor.fetchone()

        return rows

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
        print(e)
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

def select_email():
    database = "/home/ubuntu/emails.db"
    connection = create_connection(database)

    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT email, name, subject, body, dates FROM emailTable")

        rows = cursor.fetchall()
        myList = []

        for row in rows:
            tempModel = EmailDatabaseModel()
            tempModel.email = row[0]
            tempModel.name = row[1]
            tempModel.subject = row[2]
            tempModel.body = row[3]
            tempModel.dates = row[4]

            tempString = json.dumps(tempModel.__dict__)
            myList.append(tempString)

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

def createEmailDatabaseAndTables():
    database = "/home/ubuntu/emails.db"

    create_emails_table = """ CREATE TABLE IF NOT EXISTS emailTable (id integer PRIMARY KEY,
    name text NOT NULL,
    email text NOT NULL,
    subject text NOT NULL,
    body text NOT NULL,
    dates text NOT NULL); """

    connection = create_connection(database)

    if connection is not None:
        create_table(connection, create_emails_table)
    else:
        print("Error: cannot create the database connection")
        sys.exit()
# -----------------------------------------------------------------------------------------#