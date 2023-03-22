
# app.py
from flask import Flask, jsonify, request, make_response
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'your_user'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'your_database'

mysql = MySQL(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'signin'

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    if user:
        return User(user[0], user[1], user[2])
    return None

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return make_response(jsonify({'message': 'Invalid data'}), 400)

    username = data['username']
    password = data['password']
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Account created'})

@app.route('/api/signin', methods=['POST'])
def signin():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return make_response(jsonify({'message': 'Invalid data'}), 400)

    username = data['username']
    password = data['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()

    if user and bcrypt.check_password_hash(user[2], password):
        login_user(User(user[0], user[1], user[2]))
        return jsonify({'message': 'Signed in', 'username': user[1]})
    else:
        return make_response(jsonify({'message': 'Invalid credentials'}), 401)

@app.route('/api/signout', methods=['POST'])
@login_required
def signout():
    logout_user()
    return jsonify({'message': 'Signed out'})

@app.route('/api/dashboard', methods=['GET'])
@login_required
def dashboard():
    return jsonify({'message': 'Welcome', 'username': current_user.username})

if __name__ == '__main__':
    app.run(debug=True)