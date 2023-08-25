## Authenticating a Flask API Using JSON Web Tokens

Create a virtual environment for this project:
- mkdir <project folder>
- cd into folder
- python -m venv venv
- venv\Scripts\activate.bat // windows cmd line
- py -3 -m pip install flask  // path to python interpreter (version 3) must be added to env variables

! as a shortcut, if the file is named app.py or wsgi.py, you don’t have to use --app or set the FLASK_APP=api.py 

- set FLASK_APP=api.py // export for linux/unix based os
- py -3 api.py  (or:)  flask run  // by enabling debug mode, the server will automatically reload if code changes, and will show an interactive debugger in the browser if an error occurs during a request


Set up some routes:
  - "/login" (route for getting the token)
  - "/protected" route (that can only be seen if 
        you are authenticated/if you have the 
        correct and valid token)
  - "/unprotected" (anyone can visit this route)

Import a couple of modules from the flask package:
   - jsonify (..to return json objects, instead of HTML)
   - request (..to get the incoming request data, e.g. to get the login information and the token)
   - make_response (..to tell the browser or the api that Http Basic Auth is required for login)

Start with the login route (and ignore the other 2 routes for now)
  - first you need to get the authentication information
  ```sh
  def login():
     auth = request.authorization
  ```
  => that will pop up an alert box prompting
    username and password
  ```sh
     if auth and auth.password == 'password':
  ```
  ...skipping the real authentication and jst looking if the password is "password"

Installing JWT package
   > py -3 -m pip install jwt
   
   ```sh  
    token = jwt.encode({
        'user':auth.username, 
        'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=30)})
   ```

  => as for "constructing" the jwt: give it some payload (in this case just the username) and adding the time, when the jwt should expire (24h probs the most usual expiration time)\
  => another thing that is needed for JWT is the SECRET_KEY, created in the app configuration, for the sake of simplicity in the upper part of the api.py
  ```sh
  app.config['SECRET_KEY'] = 'thisisthesecretkey'
  ```
This secret key is the next argument after the payload of the JWT - so as a whole:
  ```sh
    token = jwt.encode({'user':auth.username, 'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
  ```

Now, having the token, you can return it to the user in a json object (using jsonify)
  ```sh
    return jsonify({'token' : token.decode('UTF-8')})
  ```
  ...and since it is python 3 this token is actually generated in byte, so you need to decode this token to be a regular string: what you are looking for (with python 2) is the b'<token> 

Check it out in the browser: 
> localhost:5000/login

Error! *grmpf \
AttributeError: module 'jwt' has no attribute 'encode'...actions:
1. py -3 -m pip list   // list all packages that have been installed
2. py -3 -m pip uninstall jwt
3. py -3 -m pip install pyjwt

Where was i? Right: Grab the generated token and go to jwt.io and paste it in there\
-> which decodes the jwt and you can see the user(name) and the expiration time in unix timestamp format\
-> also you see that it has an invalid signature due to the secret key\
-> take the key and paste in the box provided by jwt.io and the signature should be verified now

Now, having proven the validity of that token
- you can now easily protect multiple routes with it (that require the token to be available)
- conviently create a decorator, like:
```sh
def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
        ....
        return f(*args, **kwargs)
    return decorated
```

- in between/inside the wrapped fn: check and see if the token is along in the request, if it is: get it and make sure it is valid
- if it is valid then let the user continue onto the actual view function for that route
- if it is invalid then let the user know that 

=> for that decorator you need to import wraps from functools

=> use a try catch to make sure the JWT is valid, because jwt.decode() will raise an Exception if it is invalid

=> the token_required decorator can now be added to the protected routes
