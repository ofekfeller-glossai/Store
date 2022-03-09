from server.server.Utils import Products, User, CartItem, Customer
from typing import List


test_users = [
    dict(name="ofek", email="ofek@glossai.co", password="12345"),
    dict(name="sivan", email="sivan@glossai.co", password="1234"),
    dict(name="adi", email="adi@glossai.co", password="123456"),
]


def add_users(conn):
    return (conn.add_new_user(test_users[0]['name'], test_users[0]['email'], test_users[0]['password']),
            conn.add_new_user(test_users[1]['name'], test_users[1]['email'], test_users[1]['password']),
            conn.add_new_user(test_users[2]['name'], test_users[2]['email'], test_users[2]['password']))


test_products = [
    dict(name="Board", price=200, description="Snowboarding Board", quantity=5),
    dict(name="Boots", price=170, description="Snowboarding Boots", quantity=4),
    dict(name="Board", price=150, description="Snowboarding Bindings", quantity=5),
]


def add_products(conn):
    # add products
    products = [
        Products(test_products[i]['name'], test_products[i]['price'], test_products[i]['description'],
                 test_products[i]['quantity'])
        for i in range(len(test_products))
    ]

    conn.add_multiple_objects(products)

    return products


def add_customer(conn,
                 user: User):
    new_customer = Customer(user, "some address")
    conn.add_object(new_customer)

    return new_customer


def add_cart_items(conn,
                   customer: Customer,
                   products_list: List[Products]):
    cart = [
        CartItem(customer.id, products_list[0].id, 3),
        CartItem(customer.id, products_list[1].id, 3),
        CartItem(customer.id, products_list[2].id, 3),
    ]

    conn.add_multiple_objects(cart)



