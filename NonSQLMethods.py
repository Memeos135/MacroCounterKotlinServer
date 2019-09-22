import json
import datetime
from Models import *
from datetime import datetime, timedelta

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

def convertToObjectFromJsonDailyUpdate(data):
    info = MacroUpdateCredentials()
    loadedJson = json.loads(data)

    info.category = loadedJson["category"]
    info.value = loadedJson["updatedValue"]
    info.email = loadedJson["email"]
    info.password = loadedJson["password"]
    info.date = loadedJson["date"]

    return info

def convertToObjectFromJsonGoalUpdate(data):
    info = GoalUpdateCredentials()
    loadedJson = json.loads(data)

    info.email = loadedJson["email"]
    info.password = loadedJson["password"]
    info.protein = loadedJson["protein"]
    info.carbs = loadedJson["carbs"]
    info.fats = loadedJson["fats"]

    return info

def convertToObjectFromJsonSpecific(data):
    specificData = SpecificCredentials()
    loadedJson = json.loads(data)
    specificData.email = loadedJson["email"]
    specificData.password = loadedJson["password"]
    specificData.year = loadedJson["year"]
    specificData.month = loadedJson["month"]
    specificData.day = loadedJson["day"]

    return specificData
# -----------------------------------------------------------------------------------------#