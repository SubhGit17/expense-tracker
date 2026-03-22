import os
import mysql.connector
from urllib.parse import urlparse

conn = None
cursor = None

try:
    url = urlparse(os.getenv("MYSQL_URL"))

    conn = mysql.connector.connect(
        host=url.hostname,
        user=url.username,
        password=url.password,
        database=url.path[1:],
        port=url.port
    )

    cursor = conn.cursor(dictionary=True)
    print("DB Connected")

except Exception as e:
    print("DB ERROR:", e)