from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()
engine = create_engine('sqlite:///messenger.db', echo=True)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    password = Column(String)

    def __init__(self, name, password):
        self.name = name
        self.password = password

    def __repr__(self):
        return "<User('%s', '%s')>" % (self.name, self.password)


class UserHistory(Base):
    __tablename__ = 'user_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
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
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey('users.id'))
    id_client = Column(Integer, ForeignKey('users.id'))

    def __init__(self, id_user, id_client):
        self.id_user = id_user
        self.id_client = id_client

    def __repr__(self):
        return "<ContactList('%s', '%s')>" % (self.id_user, self.id_client)


class Room(Base):
    __tablename__ = 'room'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Room('%s')>" % self.name


class RoomChat(Base):
    __tablename__ = 'roomchat'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_room = Column(Integer, ForeignKey('room.id'))
    id_user = Column(Integer, ForeignKey('users.id'))

    def __init__(self, id_room, id_user):
        self.id_room = id_room
        self.id_user = id_user

    def __repr__(self):
        return "<Room('%s', '%s')>" % (self.id_room, self.id_user)


class Massage(Base):
    __tablename__ = 'massage'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey('users.id'))
    id_room = Column(Integer, ForeignKey('room.id'))
    text = Column(String)

    def __init__(self, id_user, id_room, text):
        self.id_user = id_user
        self.id_room = id_room
        self.text = text

    def __repr__(self):
        return "<Massage('%s', '%s')>" % (self.id_user, self.id_room)


Base.metadata.create_all(engine)
