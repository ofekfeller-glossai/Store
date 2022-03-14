from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from server.server.db import Base


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
