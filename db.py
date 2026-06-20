import mysql.connector

def get_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Jaya@2007",
        database="crop_db"
    )
    return conn