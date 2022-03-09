from typing import List
from sqlalchemy import Column, Integer, String, ForeignKey, or_, and_, create_engine
from sqlalchemy.orm import declarative_base, relationship, Session
import uuid
import os


Base = declarative_base()


###############  Utils Classes   ##################


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    user_name = Column(String)
    email = Column(String)
    password = Column(String)

    customer = relationship("Customer", backref="owner")

    def __init__(self,
                 user_name,
                 email,
                 password):
        self.user_name = user_name
        self.email = email
        self.password = password


class Admin(User):
    pass


class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    description = Column(String)
    quantity = Column(Integer)
    image_path = Column(String)

    def __init__(self,
                 product_name,
                 price,
                 description,
                 quantity,
                 image_path=""):
        self.product_name = product_name
        self.price = price
        self.description = description
        self.quantity = quantity
        self.image_path = image_path


class Customer(Base):
    __tablename__ = 'customer'

    id = Column(Integer, primary_key=True)
    address = Column(String)

    user_id = Column(Integer, ForeignKey("user.id"))

    def __init__(self,
                 user: User,
                 address):
        self.user = user
        self.address = address


class CartItem(Base):
    __tablename__ = "cartitem"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)

    def __init__(self,
                 customer_id,
                 product_id,
                 quantity):
        self.customer_id = customer_id
        self.product_id = product_id
        self.quantity = quantity


###############  Utils Functions   ################

###############  SQLALCHEMY CLASS  ################

class Query:
    def __init__(self,
                 query):
        self.query = query

    def all(self):
        return self.query.all()

    def count(self):
        return self.query.count()

    def first(self):
        return self.query.first()


def or_cond(*args):
    """
    :param session:
    :param object_type:
    :param filters:
    :return:
    sql alchemy based function
    """
    return or_(*args)


def and_cond(*args):
    """
    :param session:
    :param object_type:
    :param filters:
    :return:
    sql alchemy based function
    """
    return and_(*args)


class Connection:
    """

    """
    def __init__(self,
                 db_path=None):
        self.db_path = "{}.db".format(db_path or uuid.uuid1())
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        Base.metadata.create_all(bind=self.engine)
        self.session = Session(self.engine)

    def shutdown(self):
        self.session.close()
        self.engine.dispose()
        os.remove(self.db_path)

    def delete_object(self,
                      object_):
        self.session.delete(object_)
        self.commit()

    def add_multiple_objects(self,
                             objects_to_add):
        """
        :param objects_to_add: object that we wish to add to the db.
        :return: 0 if succeded, 1 if failed
        sql alchemy based function
        """
        self.session.add_all(objects_to_add)
        self.commit()

        return 0  # add logic to imply the success return terms

    def add_object(self,
                   object_to_add):
        """
        :param session: sqlalchemy session.
        :param object_to_add: object that we wish to add to the db.
        :return: 0 if succeded, 1 if failed
        """

        return self.add_multiple_objects([object_to_add])

    def commit(self):
        return self.session.commit()

    def get(self, object_type, filters=True):
        query = self.session.query(object_type).filter(filters)
        return Query(query)

    def add_new_user(self,
                     user_name,
                     email,
                     password):
        """
        The idea is to make this function generic
        gets a class (every class has features that must be unique), determine wheather the uniqness is violated
        and add new object accordingly.
        """

        if self.user_exist(user_name, email):
            print("Username or email is already taken")
            return None

        new_user = User(user_name, email, password)

        self.add_object(new_user)

        return new_user

    def user_exist(self,
                   user_name,
                   email):
        user_query = self.get(User, or_cond(User.user_name == user_name, User.email == email))
        return user_query.count() > 0

    def execute_order(self,
                      customer: Customer):
        """
        :param session: the sqlalchemy session
        :param customer: the customer executing the order
        :return: missing items dict (empty dict if no items were missing)
        executing the order, update the stock, and reset customer cart.
        return a dict with the id of missing products as keys and the quantity of them as values.
        """
        cart_item_query = self.get(CartItem, CartItem.customer_id == customer.id)
        cart_items: List[CartItem] = cart_item_query.all()

        missing_dict = {}

        for item in cart_items:
            product_query = self.get(Products, Products.id == item.product_id)
            product: Products = product_query.first()
            product.quantity -= item.quantity

            # if there were not enough unit on stock
            if product.quantity < 0:
                missing_dict[product.id] = abs(product.quantity)
                item.quantity = abs(product.quantity)
                product.quantity = 0

            else:
                self.delete_object(item)

            self.commit()

        return missing_dict


