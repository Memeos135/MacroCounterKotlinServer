from SQLMethods import *

# VALIDATION METHODS ( SQLITE )
# -----------------------------------------------------------------------------------------#
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