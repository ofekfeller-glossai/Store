from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, create_engine
from server.server.models import User, Customer, CartItem, Products
from server.server.db import Base, engine, db_path, LocalSession
import uuid
import os
from typing import List
import json


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

    def all_to_json(self):
        return json.dumps([obj.__dict__ for obj in self.all()], default=lambda obj: obj.__dict__)


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
                 local=True):
        self.db_path = "{}.db".format(uuid.uuid1()) if local else db_path
        self.engine = create_engine(f'sqlite:///{self.db_path}') if local else engine
        self.session = Session(bind=self.engine) if local else LocalSession()
        Base.metadata.create_all(bind=self.engine)

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


