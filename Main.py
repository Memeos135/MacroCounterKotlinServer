from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
import flask
from flask import Response
import json
import uuid
import sqlite3
from sqlite3 import Error
import sys
import datetime
from datetime import datetime, timedelta
from Models import *
from NonSQLMethods import *
from SQLMethods import *
from ValidationMethods import *
from pyfcm import FCMNotification

app = Flask(__name__)
push_service = FCMNotification(api_key="AAAA9f2OtCs:APA91bFRHlfXYiYBZcITpflD6m8gj4l4-KzTA3c9r9QASgceYKpZlQGcQ6x3jjaJ5rsDOKeeIE_PkYxrlnltCHDd3gXzDoRySjBmSo1dVGmoaewe1yPIdukTVM78nok-OEUWuApQtzId")

# ROUTES
# -----------------------------------------------------------------------------------------#
@app.route("/API/getSpecificDayProgress", methods=['POST'])
def getSpecificDayProgress():
    if(request.method == 'POST'):
        userSpecificData = convertToObjectFromJsonSpecific(request.get_data().decode("utf-8"))
        tokenExpiryDate = select_token_expiry(userSpecificData)

        if tokenExpiryDate != None:
            # check token expiry date with today's date
            if(checkDate(tokenExpiryDate)):
                specificDayFormat = userSpecificData.year + "-" + userSpecificData.month + "-" + userSpecificData.day
                getProgressInfo = select_progress_info(userSpecificData, specificDayFormat)

                if getProgressInfo != []:
                    fetchData = FetchData(getProgressInfo[0], getProgressInfo[1], getProgressInfo[2])
                    return fetchData.toJSON()
                else:
                    return "{ \"protein_progress\": \"0\", \"carbs_progress\": \"0\", \"fats_progress\": \"0\" }"
            else:
                return jsonify({"message": "ERROR: Token expired."}), 401
        else:
            return jsonify({"message": "ERROR: User not found."}), 404
    else:
        return jsonify({"message": "ERROR: Method not allowed."}), 405

@app.route("/API/postGoalUpdate", methods=['POST'])
def postGoalUpdate():
    if(request.method == 'POST'):
        goalMacrosModel = convertToObjectFromJsonGoalUpdate(request.get_data().decode("utf-8"))
        goalMacrosModelUpdate = (goalMacrosModel.protein, goalMacrosModel.carbs, goalMacrosModel.fats, goalMacrosModel.email, goalMacrosModel.password)

        if(updateGoalMacros(goalMacrosModelUpdate) == True):
            return jsonify({"response": "{ \"protein\": \"" + str(goalMacrosModel.protein) + "\", \"carbs\": \"" + str(goalMacrosModel.carbs) + "\", \"fats\": \"" + str(goalMacrosModel.fats) + "\"}"}), 200
        else:
            return jsonify({"message": "ERROR: Internal Server Database Error."}), 500
    else:
        return jsonify({"message": "ERROR: Method not allowed."}), 405

@app.route("/API/postDailyProgress", methods=['POST'])
def postDailyProgress():
    if(request.method == 'POST'):
        updatedMacroModel = convertToObjectFromJsonDailyUpdate(request.get_data().decode("utf-8"))
        user_id = select_user_id(updatedMacroModel)
        tokenExpiryDate = select_token_expiry(updatedMacroModel)

        ## FIRST CHECK IF TOKEN IS NOT EXPIRED, THEN CHECK IF MACROS EXIST FOR THIS PARTICULAR DAY
        ## IF MACROS EXIST, DO UPDATE
        ## ELSE, CREATE A NEW RECORD FOR THIS DAY AND INSERT INTO IT

        if tokenExpiryDate != None:
            # check token expiry date with today's date
            if(checkDate(tokenExpiryDate)):
                # Token is not expired
                # Check what category is requested (PROTEIN)
                if(updatedMacroModel.category.lower().startswith("p")):
                    # Check if macros exist for this particular user in the requested date
                    if(select_protein(updatedMacroModel.category, updatedMacroModel.date, user_id[0]) == None):
                        # No macros exist, create a record and return a success message
                        insertRecord = (updatedMacroModel.value, 0, 0, updatedMacroModel.date, user_id[0])
                        if(insert_protein(insertRecord) != None):
                            return jsonify({"response": "SUCCESSFUL: Record successfully created."}), 200
                        else:
                            return jsonify({"message": "ERROR: Internal Server Database Error."}), 500
                    else:
                        # Macros exist, update the current existing macros
                        updateProteinRecord = (int(updatedMacroModel.value), updatedMacroModel.date, user_id[0])
                        if(update_protein(updateProteinRecord) == True):
                            return jsonify({"response": "SUCCESSFUL: Record successfully created."}), 200
                        else:
                            return jsonify({"message": "ERROR: Internal Server Database Error."}), 500
                # Check what category is requested (CARBS)
                elif(updatedMacroModel.category.lower().startswith("c")):
                    # Check if macros exist for this particular user in the requested date
                    if(select_carbs(updatedMacroModel.category, updatedMacroModel.date, user_id[0]) == None):
                        # No macros exist, create a record and return a success message
                        insertRecord = (0, updatedMacroModel.value, 0, updatedMacroModel.date, user_id[0])
                        if(insert_carbs(insertRecord) != None):
                           return jsonify({"response": "SUCCESSFUL: Record successfully created."}), 200
                        else:
                            return jsonify({"message": "ERROR: Internal Server Database Error."}), 500
                    else:
                        # Macros exist, update the current existing macros
                        updateCarbsRecord = (int(updatedMacroModel.value), updatedMacroModel.date, user_id[0])
                        if(update_carbs(updateCarbsRecord) == True):
                            return jsonify({"response": "SUCCESSFUL: Record successfully created."}), 200
                        else:
                            return jsonify({"message": "ERROR: Internal Server Database Error."}), 500
                # Check what category is requested (FATS)
                else:
                    # Check if macros exist for this particular user in the requested date
                    if(select_fats(updatedMacroModel.category, updatedMacroModel.date, user_id[0]) == None):
                        # No macros exist, create a record and return a success message
                        insertRecord = (0, 0, updatedMacroModel.value, updatedMacroModel.date, user_id[0])
                        if(insert_fats(insertRecord) != None):
                            return jsonify({"response": "SUCCESSFUL: Record successfully created."}), 200
                        else:
                            return jsonify({"message": "ERROR: Internal Server Database Error."}), 500
                    else:
                        # Macros exist, update the current existing macros
                        updateFatsRecord = (int(updatedMacroModel.value), updatedMacroModel.date, user_id[0])
                        if(update_fats(updateFatsRecord) == True):
                            return jsonify({"response": "SUCCESSFUL: Record successfully created."}), 200
                        else:
                            return jsonify({"message": "ERROR: Internal Server Database Error."}), 500
            else:
                return jsonify({"message": "ERROR: Token expired."}), 401
        else:
            return jsonify({"message": "ERROR: User not found."}), 404
    else:
        return jsonify({"message": "ERROR: Method not allowed."}), 405

@app.route("/API/getDailyProgress", methods=['POST'])
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
                    return "{ \"protein_progress\": \"0\", \"carbs_progress\": \"0\", \"fats_progress\": \"0\" }"
            else:
                return jsonify({"message": "ERROR: Token expired."}), 401
        else:
            return jsonify({"message": "ERROR: User not found."}), 404
    else:
        return jsonify({"message": "ERROR: Method not allowed."}), 405

@app.route("/API/getJSONTest", methods = ['GET'])
def jsonifiedDataTest():
    if request.method == 'GET':
        testData = Data("Mohammed", "23", "173", "Male", "Android Developer")
        return testData.toJSON()

    else:
        return jsonify({"message": "ERROR: Method not allowed."}), 405

@app.route("/API/getTokenLogin", methods = ['POST'])
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
                        return "{ \"id\": \"" + unique_id + "\", \"email\": \"" + userLoginData.email + "\", \"protein_goal\": \"" + str(getGoalInfo[0]) +"\", \"carbs_goal\": \"" + str(getGoalInfo[1]) +"\", \"fats_goal\": \"" + str(getGoalInfo[2]) +"\",  \"protein_progress\": \"0\", \"carbs_progress\": \"0\", \"fats_progress\": \"0\" }"
            else:
                return jsonify({"message": "ERROR: Internal Server Database Error."}), 500
        else:
            return jsonify({"message": "ERROR: User not found."}), 404
    else:
        return jsonify({"message": "ERROR: Method not allowed."}), 405

@app.route("/API/signup", methods = ['POST'])
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
                return "{ \"id\": \"" + unique_id + "\", \"email\": \"" + userRegistrationData.email + "\", \"protein_goal\": \"" + userRegistrationData.protein +"\", \"carbs_goal\": \"" + userRegistrationData.carbs +"\", \"fats_goal\": \"" + userRegistrationData.fats +"\",  \"protein_progress\": \"0\", \"carbs_progress\": \"0\", \"fats_progress\": \"0\" }"
    else:
        return jsonify({"message": "ERROR: Method not allowed."}), 405

@app.route("/API/")
def hello():
    return "Welcome to the testing server - Mohammed Bokhari<br><br>There are eight available routes:<br><br>13.232.209.99/getJSONTest<br>13.232.209.99/signup<br>13.232.209.99/getTokenLogin<br>13.232.209.99/getDailyProgress<br>13.232.209.99/postDailyProgress<br>13.232.209.99/postGoalUpdate<br>13.232.209.99/getSpecificDayProgress<br>13.232.209.99/API<br>13.232.209.99/"

@app.route("/", methods=['GET'])
def webPage():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        return jsonify({"message": "ERROR: Method not allowed."}), 405

@app.route("/processEmail", methods=['POST'])
def sendEmail():
    if request.method == 'POST':
        emailObject = convertToObjectFromJsonContact(request.get_data().decode("utf-8"))
        today = datetime.now()

        emailRecord = (emailObject.name, emailObject.email, emailObject.subject, emailObject.body, today.__str__())

        insertionId = insert_email(emailRecord)
        if(insertionId != None):

            with open('fcmToken.txt', 'r') as file:
                data = file.read().replace('\n', '')

            loadedJson = json.loads(data)

            registration_id = loadedJson["token"].__str__()
            message_title = "Email received from: " + emailObject.email
            message_body = emailObject.body
            result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)

            return jsonify({"message": "Success: Your email has been successfully received."}), 200
    else:
        return jsonify({"message": "ERROR: Method not allowed."}), 405

@app.route("/fcmToken", methods=['POST'])
def saveFCMToken():
    if request.method == 'POST':
        file = open("fcmToken.txt", "w+")
        file.write(request.get_data().decode("utf-8").__str__())
        file.close()

        return jsonify({"message": "SUCCESS: Token has been saved."}), 200
    else:
        return jsonify({"message": "ERROR: Method not allowed."}), 405

@app.route("/getEmails", methods=['GET'])
def getEmails():
    if request.method == 'GET':
        emails = select_email()
        if(len(emails) > 0):

            responseString = "{ \"emailList\": ["
            for item in emails:
                responseString += item.encode("utf-8").decode("unicode-escape") + ","

            return responseString
        else:
            return jsonify({"message": "ERROR: Internal Server Database Error."}), 500
    else:
        return jsonify({"message": "ERROR: Method not allowed."}), 405
# -----------------------------------------------------------------------------------------#

# MAIN
# -----------------------------------------------------------------------------------------#
if __name__ == "__main__":
    createDatabaseAndTables()
    createEmailDatabaseAndTables()
    app.run("172.26.4.166", "80")
# -----------------------------------------------------------------------------------------#
