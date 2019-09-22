import json

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

class SpecificCredentials(object):
    email = ""
    password = ""
    year = ""
    month = ""
    day = ""

class FetchData(object):
    def __init__(self, protein_progress, carbs_progress, fats_progress):
        self.protein_progress = protein_progress
        self.carbs_progress = carbs_progress
        self.fats_progress = fats_progress

    def toJSON(self):
        return json.dumps(self.__dict__)

class GoalUpdateCredentials(object):
    email = ""
    password = ""
    protein = ""
    carbs = ""
    fats = ""

class MacroUpdateCredentials(object):
    category = ""
    value = ""
    email = ""
    password = ""
    date = ""

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
