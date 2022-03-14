from flask import Flask, redirect, url_for, session, request, render_template
import json
from server.server.Utils import Connection, and_cond, dict_to_html_table, extract_dict_list_from_query_list
from server.server.models import Products, CartItem, User, Customer
app = Flask(__name__)

app.secret_key = "any random string"

conn = Connection(local=False)

back_button = "</br></br><a href='/'>Back</a>"


@app.route("/")
def index():
    if 'username' in session:

        user: User = conn.get(User, User.user_name == session['username']).first()
        customer: Customer = conn.get(Customer, Customer.user_id == user.id).first()

        return f"you are logged as {session['username']}</br></br><a href='/items'>Go Shopping</a>" \
               f"</br></br><a href='/cart/{customer.id}'>Go to Cart</a>"

    else:

        return redirect(url_for('login'))


@app.route("/login", methods=['POST', 'GET'])
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
        return render_template("login.html")


@app.route("/items")
def items():
    query = conn.get(Products).all()

    if not query:
        return json.dumps(dict(data="no items where found", status_code=500)) + back_button

    # res = dict(status_code=200,
    #            data=extract_dict_list_from_query_list(query))

    return dict_to_html_table(extract_dict_list_from_query_list(query)) + back_button


@app.route("/cart/<customer_id>")
def cart(customer_id=None):
    query = conn.get(CartItem, CartItem.customer_id == customer_id).all()

    if not query:
        return json.dumps(dict(data="your cart is empty!", status_code=400)) + back_button

    # ret = dict(status_code=200,
    #            data=extract_dict_list_from_query_list(query))

    return dict_to_html_table(extract_dict_list_from_query_list(query)) + back_button


if __name__ == '__main__':
    app.run()
