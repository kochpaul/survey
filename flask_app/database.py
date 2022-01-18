import mysql.connector

cnx = mysql.connector.connect(user='root', password='root',
                            host='db',
                            database='survey')

cursor = cnx.cursor()

sql = "CREATE TABLE voting (id INT AUTO_INCREMENT PRIMARY KEY, room_id VARCHAR(1000), question VARCHAR(1000), yes int, no int)"

try:
    cursor.execute(sql)
except:
    print("DATABASE: Already created!")
    exit()
