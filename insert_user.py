from db import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute(
    "INSERT INTO users(username,password) VALUES(%s,%s)",
    ("admin", "1234")
)

conn.commit()

print("User inserted successfully!")

cursor.close()
conn.close()