from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


Base = declarative_base()

db_path = "main.db"

engine = create_engine(f'sqlite:///{db_path}?check_same_thread=False')  # check same thread is false

LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


