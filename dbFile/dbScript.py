import sqlite3

conn = sqlite3.connect('cloud_assign.db')
cur = conn.cursor()
# cur.execute("""DROP TABLE IF EXISTS user_data""")
# cur.execute("""CREATE TABLE user_data
#             (username text, password text, first_name text, last_name text, email_id text)""")
# cur.execute("""DROP TABLE IF EXISTS user_file""")
# cur.execute("""CREATE TABLE user_file (username text, file_name text, file_content text)""")
query = """INSERT INTO USER_DATA (USERNAME, PASSWORD, FIRST_NAME, LAST_NAME, EMAIL_ID) values (?, ?, ?, ?, ?)"""
values = ["username", "password", "first_name", "last_name", "email_id"]
cur.execute(query, values)
result = cur.execute("""SELECT * from user_data""")
for row in result:
    print(row)

conn.commit()
conn.close()