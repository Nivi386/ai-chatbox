# test_connection.py
# A throwaway script just to prove Python can talk to MySQL.
# We'll replace this hardcoded approach with proper config in the next milestone.

import mysql.connector

# Open a connection to the MySQL server
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Azsx12az*",  # replace with your real password
    database="ai_chatbox"
)

# A "cursor" is the object you use to run SQL commands and fetch results
cursor = connection.cursor()
cursor.execute("SELECT * FROM chat_messages")

# fetchall() retrieves every row from the last query as a list of tuples
results = cursor.fetchall()
for row in results:
    print(row)

# Always close what you open, to free up the connection
cursor.close()
connection.close()