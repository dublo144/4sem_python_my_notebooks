#!flask/bin/python
from flask import Flask, request, jsonify
import sqlalchemy as s_a

app = Flask(__name__)

DB_URL = 'mysql+mysqlconnector://root:root@db/ex_08'
engine = s_a.create_engine(DB_URL)
connection = engine.connect()


@app.route('/flask_app', methods=['GET'])
def hello_world():
    return "Hello World!"


@app.route('/api/employee/all', methods=['GET'])
def hello():
    query = 'SELECT * FROM People'
    ResultProxy = connection.execute(query)
    ResultSet = ResultProxy.fetchall()
    return jsonify([dict(row) for row in ResultSet])


@app.route('/api/employee/<string:firstName>/<string:lastName>', methods=['GET'])
def employee(firstName, lastName):
    query = 'SELECT * FROM People WHERE `First Name` LIKE \'{}\' AND `Last Name` LIKE \'{}\''.format(
        firstName, lastName)
    ResultProxy = connection.execute(query)
    ResultSet = ResultProxy.fetchall()
    return jsonify([dict(row) for row in ResultSet])


@app.route('/api/employee/add', methods=['POST'])
def create_empployee():
    data = request.get_json()
    person = {
        "First Name": data['First Name'],
        "Last Name": data['Last Name'],
        "Gender": data["Gender"],
        "Age": data["Age"],
        "email": data["Email"],
        "phone": data["Phone"],
        "Occupation": data["Occupation"],
        "Salary": data["Salary"]
    }
    return jsonify(person)


if __name__ == '__main__':
    app.run(debug=True)
