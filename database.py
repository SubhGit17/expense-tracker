import os
import mysql.connector
from urllib.parse import urlparse

url = urlparse(os.getenv("MYSQL_URL"))

conn = mysql.connector.connect(
    host=url.hostname,
    user=url.username,
    password=url.password,
    database=url.path[1:],
    port=url.port
)

cursor = conn.cursor(dictionary=True)