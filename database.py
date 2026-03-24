import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

conn = None
cursor = None

try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306))
    )

    cursor = conn.cursor(dictionary=True)
    print("DB Connected")

except Exception as e:
    print("DB ERROR:", e)