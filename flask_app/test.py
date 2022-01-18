import mysql.connector

cnx = mysql.connector.connect(user='root', password='root',
                              host='127.0.0.1',
                              database='survey')

cursor = cnx.cursor()

# sql = "INSERT INTO voting (room_id, question, yes, no) VALUES (%s, %s, %s, %s)"
# val = ("ajkfh", "daily", 2, 5)

# sql = "CREATE TABLE voting (id INT AUTO_INCREMENT PRIMARY KEY, room_id VARCHAR(1000), question VARCHAR(1000), yes int, no int)"
room_id = "ajkfh"
sql = "UPDATE voting SET yes = yes - 1 WHERE room_id = %s"
val = (room_id, )
# cursor.execute(sql)
cursor.execute(sql,val)
cnx.commit()
# myresult = cursor.fetchone()

# print(myresult)    
# result = result = {"yes": myresult[0], "no": myresult[1]}
# print(result)