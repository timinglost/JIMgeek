import sqlite3
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base

conn = sqlite3.connect("../messenger.db")

cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
results = cursor.fetchall()
conn.close()
users = []
for i in results:
    users.append(i[1])

for i in users:
    Base = declarative_base()
    engine = create_engine(f'sqlite:///{i}_db.db', echo=True)

    class Contact(Base):
        __tablename__ = 'contact'
        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String)

        def __init__(self, name):
            self.name = name

        def __repr__(self):
            return "<User('%s')>" % (self.name)

    class Massege(Base):
        __tablename__ = 'massege'
        id = Column(Integer, primary_key=True, autoincrement=True)
        text = Column(String)

        def __init__(self, name, text):
            self.name = name
            self.text = text

        def __repr__(self):
            return "<Massege('%s', '%s')>" % (self.name, self.text)

    Base.metadata.create_all(engine)
