import sqlite3

conn = sqlite3.connect("messenger.db")

cursor = conn.cursor()
for i in range(20):
    name = f'user_{i}'
    cursor.execute(f'insert into users(name, password) values ("{name}", "qwe");')
conn.commit()
cursor.execute("SELECT * FROM users")
results = cursor.fetchall()
print(results)
conn.close()