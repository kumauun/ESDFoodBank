from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://admin:rootroot@db-savood.c0hav88yk9mq.us-east-1.rds.amazonaws.com:3306/test"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

CORS(app)

class Student(db.Model):
    __tablename__ = 'student'

    sid = db.Column(db.String(5), primary_key=True)
    sname = db.Column(db.String(64), nullable=False)

    def __init__(self, sid, sname):
        self.sid = sid
        self.sname = sname

    def json(self):
        return {"sid": self.sid, "sname": self.sname}


@app.route("/students")
def get_all():
    studentlist = Student.query.all()
    if len(studentlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "students": [student.json() for student in studentlist]
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