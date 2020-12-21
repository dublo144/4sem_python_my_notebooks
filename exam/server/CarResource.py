import datetime
import re
import time
import pymongo
import pandas as pd
from flask import Flask, jsonify, abort, request
import json
from bson import ObjectId


client = pymongo.MongoClient(
    "mongodb+srv://python:exam123@cluster0.wabpp.mongodb.net/cars?retryWrites=true&w=majority")
db = client.python_exam
collection = db.cars


class JSONEncoder(json.JSONEncoder):
    ''' extend json-encoder class'''

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.json_encoder = JSONEncoder


def to_json_response(dataframe):
    result = {}
    for index, row in dataframe.iterrows():
        result[index] = dict(row)
    return jsonify(result)


@app.route('/api/cars/all', methods=['GET'])
def read_from_db():
    # Make a query to the specific DB and Collection
    cursor = collection.find({})

    # Expand the cursor and construct the DataFrame
    df = pd.DataFrame(list(cursor))
    print(df.head(2))

    return to_json_response(df)


@app.route('/api/cars/get', methods=['GET'])
def read_model_from_db():
    make = request.args.get('make')
    max_price = request.args.get('max_price')
    res = collection.find({'Make': re.compile(
        make, re.IGNORECASE), 'Pris': {'$lt': max_price}})
    df = pd.DataFrame(list(res))
    result = {}
    for index, row in df.iterrows():
        # result[index] = row.to_json()
        result[index] = dict(row)
    return jsonify(result)


@app.route('/api/manufactorcount', methods=['GET'])
def return_manufactor_count():
    query = collection.aggregate([
        {
            "$match": {
                "Make": {"$not": {"$size": 0}}
            }
        },
        {"$unwind": "$Make"},
        {
            "$group": {
                "_id": {"$toLower": "$Make"},
                "count": {"$sum": 1}
            }
        },
        {
            "$match": {
                "count": {"$gte": 2}
            }
        },
        {"$sort": {"count": -1}},
        {"$limit": 100}
    ])
    df = pd.DataFrame(list(query))
    result = to_json_response(df)
    print(df)
    return result


@app.route('/api/pricemiles', methods=['GET'])
def return_price_miles():
    query = collection.find(
        {}, {"Kilometer": 1, "Pris": 1, "_id": 0, }).limit(500)
    df = pd.DataFrame(list(query))
    result = to_json_response(df)
    return result


@app.route('/api/pricemiles/make', methods=['GET'])
def return_price_miles_from_make():
    manufactor = request.args.get('make')
    res = collection.find({'Make': re.compile(
        manufactor, re.IGNORECASE)}, {"Kilometer": 1, "Pris": 1, "_id": 0, }).limit(500)

    df = pd.DataFrame(list(res))
    result = to_json_response(df)
    print(result)
    return result


@app.route('/api/dummy', methods=['GET'])
def return_dummy_res():
    print('hgey')
    return jsonify({'Msg': 'HelloWorld'})


if __name__ == '__main__':
    app.run(debug=True)
