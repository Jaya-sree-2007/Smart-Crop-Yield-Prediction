import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Jaya@2007",
    database="crop_db"
)

print("Connected Successfully!")

conn.close()