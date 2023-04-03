from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import requests

app = Flask(__name__)
app.secret_key = 'zhongli'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://admin:rootroot@db-savood.c0hav88yk9mq.us-east-1.rds.amazonaws.com:3306/user"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

CORS(app, supports_credentials=True, resources={r"/logout": {"origins": "*"}, r"*": {"origins": "*"}})

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(255), unique=True, nullable=False)
    user_type = db.Column(db.Enum('restaurant', 'foodbank', 'driver'), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return self.user_id

@login_manager.user_loader
def load_user(user_id):
    print('Received user_id:', user_id)
    return User.query.get(int(user_id))

@app.route('/')
def hello_world():
    return 'Halloooooooo'

@app.route('/login', methods=['GET'])
def show_login_form():
    return jsonify({'message': 'Please send a POST request to log in'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(user_email=user_email).first()
    if user and user.check_password(password):
        login_user(user)
        print(user)
        return jsonify({
            'message': 'Logged in successfully', 
            'user_id': user.user_id, 
            'user_type' : user.user_type,
            'username': user.username
            })
    else:
        abort(401)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    user_email = data.get('user_email')
    user_type = data.get('user_type')
    phone_number = data.get('phone_number')
    region = data.get('region')
    postal_code = data.get('postal_code')
    address = data.get('address')
    password = data.get('password')
    username = data.get('username')

    # Check if the user_email or username already exists
    existing_email = User.query.filter_by(user_email=user_email).first()
    existing_username = User.query.filter_by(username=username).first()

    if existing_email or existing_username:
        return jsonify({
            'code': 409,
            'message': 'Email or username already exists'
        }), 409

    # Create a new user
    new_user = User(user_email=user_email, user_type=user_type, username=username)
    new_user.set_password(password)
    

    # Save the new user to the database
    db.session.add(new_user)
    db.session.commit()

    if new_user.user_type == 'restaurant':

        payload = {
            'restaurant_id': new_user.user_id,
            'restaurant_name': username,
            'phone_number': phone_number,
            'address': address,
            'postal_code': postal_code,
            'region': region,
        }

         # Send a POST request to the other microservice
        print("About to send a post req to resto table")
        url = "http://restaurant:5001/new_restaurant"
        response = requests.post(url, json=payload)

    elif new_user.user_type == 'foodbank':

        payload = {
            'foodbank_id': new_user.user_id,
            'foodbank_name': username,
            'phone_number': phone_number,
            'address': address,
            'postal_code': postal_code,
            'region': region,
        }

        url = "http://foodbank:5002/new_foodbank"
        response = requests.post(url, json=payload)

    elif new_user.user_type == 'driver':

        payload = {
            'driver_id': new_user.user_id,
            'driver_name': username,
            'phone_number': phone_number,
            'region': region,
            'availability': True
        }

        url = "http://driver:5003/new_driver"
        response = requests.post(url, json=payload)


    if response.status_code != 201:
        return jsonify({
            'code': 500,
            'message': 'Error communicating with the other microservice'
        }), 500

    # Log the user in
    login_user(new_user, remember=True)

    return jsonify({
        'code': 201,
        'message': 'User created successfully', 
        'user_id': new_user.user_id,
        'user_type' : new_user.user_type,
        'username': new_user.username  }), 201

@app.route('/logout')
@login_required
def logout():
    print('masuk sini')
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5006, debug=True)
