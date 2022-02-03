from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker, declarative_base
from sqlalchemy.sql import func


Base = declarative_base()
engine = create_engine('sqlite:///messenger.db', echo=True)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)

    def __init__(self, name, password):
        self.name = name
        self.password = password

    def __repr__(self):
        return "<User('%s', '%s')>" % (self.name, self.password)


class UserHistory(Base):
    __tablename__ = 'user_history'
    id = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey('users.id'))
    time_connect = Column(DateTime(timezone=True), server_default=func.now())
    ip_addr = Column(String)

    def __init__(self, id_user, time_connect, ip_addr):
        self.id_user = id_user
        self.time_connect = time_connect
        self.ip_addr = ip_addr

    def __repr__(self):
        return "<UserHistory('%s', '%s')>" % (self.time_connect, self.ip_addr)


class ContactList(Base):
    __tablename__ = 'contact_list'
    id = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey('users.id'))
    id_client = Column(Integer, ForeignKey('users.id'))

    def __init__(self, id_user, id_client):
        self.id_user = id_user
        self.id_client = id_client

    def __repr__(self):
        return "<ContactList('%s', '%s')>" % (self.id_user, self.id_client)


Base.metadata.create_all(engine)