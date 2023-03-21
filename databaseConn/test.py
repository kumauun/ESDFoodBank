from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://admin:rootroot@db-savood.c0hav88yk9mq.us-east-1.rds.amazonaws.com:3306/order"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

CORS(app)

class Order(db.Model):
    __tablename__ = 'orders'

    order_id = db.Column(db.Integer, primary_key=True)
    foodbank_id = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, nullable=False)
    dish_id = db.Column(db.Integer, nullable=False)
    quantity_check = db.Column(db.SmallInteger, nullable=False)
    status = db.Column(db.Enum, nullable=False)

    def __init__(self, order_id, foodbank_id, restaurant_id, dish_id, quantity_check, status):
        self.order_id = order_id
        self.foodbank_id = foodbank_id
        self.restaurant_id = restaurant_id
        self.dish_id = dish_id
        self.quantity_check = quantity_check
        self.status = status
        

    def json(self):
        return {"order_id": self.order_id, "foodbank_id": self.foodbank_id, "restaurant_id": self.restaurant_id, "dish_id": self.dish_id, "quantity_check": self.quantity_check, "status": self.status}


@app.route("/orders")
def get_all():
    orderList = Order.query.all()
    if len(orderList):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "orders": [order.json() for order in orderList]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no students."
        }
    ), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)