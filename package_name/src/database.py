import sqlite3
import hashlib
from utils import load_config

conn = sqlite3.connect("messenger.db")
salt = load_config('salt.yaml')['SALT']

cursor = conn.cursor()
hashed_password = hashlib.sha512(
                        'qwe'.encode('utf-8') + salt.encode('utf-8')).hexdigest()
for i in range(20):
    name = f'user_{i}'
    cursor.execute(f'insert into users(name, password) values ("{name}", "{hashed_password}");')
conn.commit()
cursor.execute("SELECT * FROM users")
results = cursor.fetchall()
print(results)
conn.close()
