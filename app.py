from chalice import Chalice, Response
from src import *
import jwt
import datetime
import os
import hashlib

app = Chalice(app_name='rediscashing')

NoSQLdatabase = NoSQL(host=REDIS_HOST, password=REDIS_PASSWORD, port=REDIS_PORT)

FILE_ROUTE = '/auth'


#--------------------------------------------------------------------------------------------------#
#-----------------------------------------TEST ROUTE-----------------------------------------------#
#--------------------------------------------------------------------------------------------------#

@app.route('/', methods=['GET'])
def mainpage():
    @Utils.isUserWithArgs(app.current_request, NoSQLdatabase, SECRET)
    def f(user):
        return CustomResponse.responseFormat1(f'Hello {user}', status.success)
    return f()

#--------------------------------------------------------------------------------------------------#
#-------------------------------------USER SIGNIN-------------------------------------------------#
#--------------------------------------------------------------------------------------------------#

@app.route(FILE_ROUTE + '/signin', methods=["POST"])
def userSignin():
    @Utils.getBody(app.current_request, {'username' : (str, ), 'password' : (str, )})
    def f(inputDetails):
        data = NoSQLdatabase.getValue(inputDetails['username'])
        if data:
            new_key = hashlib.pbkdf2_hmac('sha256', inputDetails['password'].encode('utf-8'), bytes.fromhex(data[:64]), 100000)
            if new_key.hex() == data[64:]:
                payload = {'username' : inputDetails['username'], 'salt' : os.urandom(64).hex(), 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1)}
                token = jwt.encode(payload, SECRET, algorithm='HS256')
                if NoSQLdatabase.setValue(inputDetails['username'] + '_token', token):
                    return CustomResponse.responseFormat1(token, status.success)
                return CustomResponse.responseFormat1("Token storage error", status.error)
            return CustomResponse.responseFormat1("Password Missmatch", status.failure)
        return CustomResponse.responseFormat1("No user found", status.failure)
    return f()

#--------------------------------------------------------------------------------------------------#
#-------------------------------------USER SIGNIN-------------------------------------------------#
#--------------------------------------------------------------------------------------------------#

@app.route(FILE_ROUTE + '/signup', methods=["POST"])
def userSigninOuter():
    @Utils.getBody(app.current_request, {'username' : (str, ), 'password' : (str, )})
    def userSignin(data):
        existing = NoSQLdatabase.getValue(data['username'])
        if existing:
            return CustomResponse.responseFormat1("User Exists", status.failure)
        salt = os.urandom(32)
        new_key = hashlib.pbkdf2_hmac('sha256', data['password'].encode('utf-8'), salt, 100000)
        password = salt.hex() + new_key.hex() 
        if NoSQLdatabase.setValue(data['username'], password):
            return CustomResponse.responseFormat1('', status.success)
        return CustomResponse.responseFormat1("Database Storage error", status.error)
    return userSignin()

# #--------------------------------------------------------------------------------------------------#
# #--------------------------------------PASSWORD CHANGE---------------------------------------------#
# #--------------------------------------------------------------------------------------------------#

# password change
@app.route(FILE_ROUTE + '/passwordchange', methods=["POST"])
def passChangeOuter():
    @Utils.isUserWithArgsPOST(app.current_request, NoSQLdatabase, SECRET, {'password' : (str, )})
    def passChange(username, body):
        salt = os.urandom(32)
        newpass = hashlib.pbkdf2_hmac('sha256', body['password'].encode('utf-8'), salt, 100000)
        if NoSQLdatabase.setValue(username, salt.hex() + newpass.hex()):
            return CustomResponse.responseFormat1("", status.success)
        return CustomResponse.responseFormat1("No user found", status.failure)
    return passChange()

# #--------------------------------------------------------------------------------------------------#
# #------------------------------------ERROR HANDLERS------------------------------------------------#
# #--------------------------------------------------------------------------------------------------#

@app.middleware('all')
def handle_errors(event, get_response):
    try:
        return get_response(event)
    except Exception as e:
        return Response(status_code=500, body=str(e),
                        headers={'Content-Type': 'text/plain'})

#--------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------#