from flask import Flask, redirect, url_for
import json
from server.server.Utils import Connection, and_cond
from server.server.models import Products, CartItem, User
import flask_login
app = Flask(__name__)

conn = Connection(local=False)


def extract_dict_list_from_query(*query):
    ret = []
    for item in query:
        item_dict = item.__dict__
        item_dict.pop("_sa_instance_state")
        ret.append(item_dict)

    return ret


def extract_dict_list_from_query_list(query_list):
    return extract_dict_list_from_query(*query_list)


@app.route("/")
def index():
    return redirect(url_for('items'))


@app.route("/items")
def items():
    query = conn.get(Products).all()

    if not query:
        return json.dumps(dict(data="no items where found", status_code=500))

    res = dict(status_code=200,
               data=extract_dict_list_from_query_list(query))

    return json.dumps(res)


@app.route("/cart/<customer_id>")
def cart(customer_id=None):
    query = conn.get(CartItem, CartItem.customer_id == customer_id).all()

    if not query:
        return json.dumps(dict(data="your cart is empty!", status_code=400))

    ret = dict(status_code=200,
               data=extract_dict_list_from_query_list(query))

    return json.dumps(ret)


if __name__ == '__main__':
    app.run()
