import datetime
import re
import time
import pymongo
import pandas as pd
from flask import Flask, jsonify, abort, request
import json
from bson import ObjectId


client = pymongo.MongoClient(
    "mongodb+srv://dublo:Anton1993!@cluster0.wabpp.mongodb.net/cars?retryWrites=true&w=majority")
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
    model = request.args.get('model')
    max_price = request.args.get('max_price')
    res = collection.find({'Model': re.compile(
        model, re.IGNORECASE), 'Pris': {'$lt': max_price}})
    df = pd.DataFrame(list(res))
    print(df)
    print(model)
    print(max_price)
    result = {}
    for index, row in df.iterrows():
        # result[index] = row.to_json()
        result[index] = dict(row)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
