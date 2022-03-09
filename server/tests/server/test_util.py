import pytest
import pytest_check as check
from server.server.Utils import User, Products, Customer, Connection, CartItem, and_cond, or_cond
from server.tests.server.tests_assist import test_users, add_users, add_products, add_customer, add_cart_items, \
    test_products


#############  Util Tests  #############

@pytest.fixture()
def conn():
    """Fixture to execute asserts before and after a test is run"""
    connection = Connection()

    yield connection

    connection.shutdown()


def test_users_inserting(conn):
    add_users(conn)

    check.equal(conn.get(User).count(), len(test_users))


mixture_users = [
    dict(name=test_users[0]['name'], email="new_email@glossai.co", password=test_users[0]['password']),  # test same username
    dict(name="new_username", email=test_users[0]['email'], password=test_users[0]['password']),       # test same email
    dict(name=test_users[0]['name'], email=test_users[0]['email'], password=test_users[0]['password']),  # test same both
]


@pytest.mark.parametrize("user_dict", mixture_users)
def test_existing_user_insert(conn,
                              user_dict):
    add_users(conn)

    conn.add_new_user(user_dict['name'], user_dict["email"], user_dict['password'])

    check.equal(conn.get(User).count(), len(user_dict))


def test_add_products(conn):
    products = add_products(conn)

    check.equal(conn.get(Products).count(), len(test_products))

    check.equal(conn.get(Products, Products.id == products[0].id).first().quantity, test_products[0]['quantity'])


def test_customers(conn):
    users = add_users(conn)

    for user in users:
        add_customer(conn, user)

    check.equal(conn.get(Customer).count(), len(users))


def test_cart_items(conn):
    users = add_users(conn)

    customers = [add_customer(conn, user) for user in users]

    products = add_products(conn)

    for customer in customers:
        add_cart_items(conn, customer, products)

    check.equal(conn.get(CartItem).count(), len(customers) * len(products))

    check.equal(conn.get(CartItem, CartItem.customer_id == customers[0].id).count(), len(products))


def test_checkout(conn):
    # add users
    users = add_users(conn)

    # add customers
    first_customer = add_customer(conn, users[0])

    second_customer = add_customer(conn, users[1])

    # add products
    products = add_products(conn)

    test_sum = test_products[0]['quantity']

    # customers shopping
    add_cart_items(conn, first_customer, products)

    add_cart_items(conn, second_customer, products)

    test_sum -= conn.get(CartItem, and_cond(CartItem.customer_id == first_customer.id,
                                            CartItem.product_id == products[0].id)).first().quantity

    # checkout
    conn.execute_order(first_customer)

    check.equal(conn.get(Products, Products.id == products[0].id).first().quantity, test_sum)

    check.equal(conn.get(CartItem, CartItem.customer_id == first_customer.id).count(), 0)  # no items left in the cart for him

    missing = conn.execute_order(second_customer)

    for item_id in missing:
        query = conn.get(CartItem, and_cond(CartItem.customer_id == second_customer.id,
                                            CartItem.product_id == item_id))

        check.greater(query.count(), 0)  # we must not get zero because some items should be in the cart

        check.equal(query.first().quantity, missing[item_id])
