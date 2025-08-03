import hashlib
import flask
from flask import request, make_response


app = flask.Flask(__name__)
app.config["DEBUG"] = True


p = hashlib.new('sha256')
p.update(b'password')  # user password
print(p.hexdigest())  # hash password

mUser = 'user'  # username
mPass = 'password'  # hashed password


@app.route('/api/login', methods=['GET'])
def user_login():
    if request.authorization:
        upass = request.authorization.password.encode()
        hashed = hashlib.sha256(upass)
        if request.authorization.username == mUser and hashed.hexdigest() == mPass:
            return 'Login successful'
    return make_response('Error: Failed to login', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


app.run()
