from flask import Flask, jsonify, request, make_response

import jwt
import datetime
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisisthesecretkey'

def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = request.args.get('token') # sth like: http://127.0.0.1:5000/route?token=eyJhbGciOiJIUzI1..

		if not token:
			return jsonify({'message':'Token is missing'}), 403

		# make sure that the token is valid
		try:			
			data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])

		except:
			return jsonify({'message':'Token is invalid'}), 403

		return f(*args, **kwargs)

	return decorated

@app.route("/login")
def login():
	auth = request.authorization

	if auth and auth.password == 'password':
		# create jwt token; payload with the logged in user, the expiration and the secret key
		token = jwt.encode({'user':auth.username, 'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

		return jsonify({'token': token})

	return make_response('Couldnt verify', 401, {'WWW-Authenticate':'Basic realm="Login Required"'})

@app.route("/protected")
@token_required
def protected():
	return jsonify({'message':'This site is only available for ppl with valid tokens!'}), 200


@app.route("/unprotected")
def unprotected():
	return jsonify({'message':'Anyone can see this! (no jwt required)'}), 200


if __name__ == "__main__":
	app.run(debug=True)
