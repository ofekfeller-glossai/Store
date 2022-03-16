from flask import Flask, redirect, url_for, session, request, render_template, Response
import json
from server.server.Utils import Connection, and_cond, dict_to_html_table, extract_dict_list_from_query
from server.server.models import Products, CartItem, User, Customer
from werkzeug.wrappers.response import Response
app = Flask(__name__)

app.secret_key = "any random string"

conn = Connection(local=False)

back_button = "</br></br><a href='/'>Back</a>"


def query_decorator(func):
    def wrapper(*args, **kwargs):

        try:

            ret_dict = func(*args, **kwargs)

            if not ret_dict["data"]:
                ret_dict['status_code'] = 500

            data_dict = extract_dict_list_from_query(*ret_dict['data'])

            ret_dict['data'] = data_dict

        except Exception as e:

            ret_dict = dict(
                data="An error occurred while responding the request.",
                error=e,
                status_code=400,
            )

        return json.dumps(ret_dict) + back_button

    wrapper.__name__ = func.__name__
    return wrapper


def render_decorator(func):
    def wrapper(*args, **kwargs):

        try:
            ret_dict = func(*args, **kwargs)

            if isinstance(ret_dict, Response):
                return ret_dict

        except Exception as e:

            print(e)

            ret_dict = dict(
                data="An error occurred while responding the request.",
                error=e,
                status_code=400,
                render_target='error'

            )

        return render_template(f"{ret_dict['render_target']}.html", **ret_dict)

    wrapper.__name__ = func.__name__
    return wrapper


@app.route("/")
@render_decorator
def index():
    if 'username' in session:

        user: User = conn.get(User, User.user_name == session['username']).first()
        customer: Customer = conn.get(Customer, Customer.user_id == user.id).first()

        return dict(render_target='index',
                    username=session['username'],
                    customer=customer.id)

    else:

        return redirect(url_for('login'))


@app.route("/login", methods=['POST', 'GET'])
@render_decorator
def login():
    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        if conn.validate_login(username, password):

            session['username'] = username
            return redirect(url_for('index'))

        else:
            return redirect(url_for('login'))

    if request.method == 'GET':
        return dict(render_target='login')


@app.route("/items")
@query_decorator
def items():
    query = conn.get(Products).all()

    return dict(status_code=200,
                data=query)


@app.route("/cart/<customer_id>")
@query_decorator
def cart(customer_id=None):
    query = conn.get(CartItem, CartItem.customer_id == customer_id).all()

    return dict(status_code=200,
                data=query)


if __name__ == '__main__':
    app.run()
