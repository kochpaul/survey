from flask import Flask, render_template, redirect, url_for, request
from celery import Celery
import mysql.connector

import time

app = Flask(__name__)
simple_app = Celery('simple_worker', broker='redis://redis:6379/0', backend='redis://redis:6379/0')

# following function returns status of specific task -> specified in "worker/tasks.py"
@app.route('/task_status/<id>')
def get_status(id):
    status = simple_app.AsyncResult(id, app=simple_app)
    return f"Status of task {id}: \n\n{status.state}"

# following function returns result of specific task -> specified in "worker/tasks.py"
@app.route('/task_result/<id>')
def task_result(id):
    result = simple_app.AsyncResult(id).result
    return "Result of the Task " + str(result)

# following routes the "createroom" - page, where an admin can create a room -> room_id
@app.route("/admin/createroom", methods=["POST", "GET"])
def createroom():
    # check if something "posted" on this url (/admin/createroom)
    if request.method == "POST":
        key_request_ = request.form.keys()            
        key_request = list(key_request_)

        # get value which was posted 
        if key_request == ['room_name']:            
            value_request = request.form.values()
            room_name_list = list(value_request)
            room_name = str(room_name_list[0])
            
            # trigger task to create room, without question 
            app.logger.info(f"Create room {room_name}!")
            room = simple_app.send_task('tasks.room', kwargs={"name": room_name})
            time.sleep(3)
            app.logger.info(room.backend)
            app.logger.info("Created room!")
            
            # redirect to next page where the question can be asked 
            return redirect(url_for("adminroom", room_id=room.id))
    
    return render_template("admin/createroom.html")

# following routes the "admin/room" - page, where an admin can post a question in the room -> (new) room_id 
@app.route("/admin/room/<room_id>", methods=["POST", "GET"])
def adminroom(room_id):
    # gets the result from "room" - task -> {name; question; result}
    room = simple_app.AsyncResult(room_id).result

    # check if something "posted" on this url (/admin/room/<room_id>)
    if request.method == "POST":
        key_request_ = request.form.keys()            
        key_request = list(key_request_)

        # get value which was posted  
        if key_request == ['question']:            
            value_request = request.form.values()
            question_list = list(value_request)
            question = str(question_list[0])
            
            # trigger task "room" -> creates room
            app.logger.info(f"Create new Room {room['name']}, with question {room['question']}!")
            question_task = simple_app.send_task('tasks.room', kwargs={"name": room["name"] ,"question": question})            
            time.sleep(3)
            app.logger.info(question_task.backend)

            # push room_id and question to db
            # cnx opens connection to db 
            cnx = mysql.connector.connect(user='root', password='root',
                            host='db',
                            database='survey')

            # .cursor() creates a cursor which can execute SQL - commands
            cursor = cnx.cursor()

            # sql = the SQL - query (SQL syntax)
            sql = "INSERT INTO voting (room_id, question, yes, no) VALUES (%s, %s, %s, %s)"
            # val are the values which should get inserted into db 
            val = (question_task.id, question, 0, 0)
            
            # .execute() executes the query 
            cursor.execute(sql, val)
            # .commit() commites the data to the named table, if .commit() isn't in the code -> no change in db 
            cnx.commit()            
            # .close() closes the database connection 
            cnx.close()
            return redirect(url_for("adminresults", room_id=question_task.id))
    return render_template("admin/question.html", room_id=room_id, room_name=room["name"])

# following routes the "/admin/results/room/<room_id>" - page, where the results of the survey are displayed
# admin can close the survey -> saves the results with the question; or can start a new survey -> also saves 
# the result, but also creates a new "adminroom"
@app.route("/admin/results/room/<room_id>", methods=["POST", "GET"])
def adminresults(room_id):
    room = simple_app.AsyncResult(room_id).result

    cnx = mysql.connector.connect(user='root', password='root',
                              host='db',
                              database='survey')
    cursor = cnx.cursor()

    # query to get the result from the survey where room_id = room_id 
    sql = "SELECT yes, no FROM voting WHERE room_id = %s"
    val = (room_id, )
    cursor.execute(sql, val)
    
    myresult = cursor.fetchone()
    result = {"yes": myresult[0], "no": myresult[1]}

    if request.method == "POST":
        key_request_ = request.form.keys()            
        key_request = list(key_request_)

        # get value which was posted  
        if key_request == ['close']:            
            app.logger.info(f"Create result room {room['name']}, with question {room['question']}!")
            result_room = simple_app.send_task('tasks.room', kwargs={"name": room["name"] ,"question": room['question'], "result": result})            
            time.sleep(3)
            app.logger.info(result_room.backend)
            return redirect(url_for("task_result", id=result_room.id))

        # get value which was posted  
        elif key_request == ['next']:            
            app.logger.info(f"Create new Room {room['name']}, with question {room['question']}!")
            new_room = simple_app.send_task('tasks.room', kwargs={"name": room["name"]})            
            time.sleep(3)
            app.logger.info(new_room.backend)
            return redirect(url_for("adminroom", room_id=new_room.id))
    return render_template("admin/result.html", room_name=room["name"], room_question=room["question"], result=result, room_id=room_id)

# routes "/user/room/<room_id>" -> user can join the room and vote 
@app.route("/user/room/<room_id>", methods=["POST", "GET"])
def room(room_id):
    room = simple_app.AsyncResult(room_id).result

    if request.method == "POST":
        key_request_ = request.form.keys()            
        key_request = list(key_request_)

        # if user votes with "yes"
        if key_request == ['yes',]:            
            app.logger.info(f"User in room: {room['name']} votes the question {room['question']} with YES!")
            # triggers task "voting" -> increases the value of "yes" in db 
            question_task = simple_app.send_task('tasks.voting', kwargs={"vote": "y", "room_id": room_id})
            time.sleep(2)
            app.logger.info(question_task.backend)
            app.logger.info("Voting finished")
            return redirect(url_for("result", result_id=question_task.id, room_id=room_id))
        
        # if user votes with "no"
        else:            
            app.logger.info(f"User in room: {room['name']} votes the question {room['question']} with NO!")
            # triggers task "voting" -> increases the value of "no" in db 
            question_task = simple_app.send_task('tasks.voting', kwargs={"vote": "n", "room_id": room_id})            
            time.sleep(2)
            app.logger.info(question_task.backend)
            app.logger.info("Voting finished")
            return redirect(url_for("result", result_id=question_task.id, room_id=room_id))

    return render_template("user/room.html", room_name=room["name"], room_question=room["question"])

# routes "/user/room=<room_id>/results=<result_id>" -> user can see the results of the survey 
@app.route("/user/room=<room_id>/results=<result_id>")
def result(result_id, room_id):
    room = simple_app.AsyncResult(room_id).result
    
    cnx = mysql.connector.connect(user='root', password='root',
                              host='db',
                              database='survey')
    cursor = cnx.cursor()

    sql = "SELECT yes, no FROM voting WHERE room_id = %s"
    val = (room_id, )
    cursor.execute(sql, val)

    myresult = cursor.fetchone()
    app.logger.info(myresult)
    result = {"yes": myresult[0], "no": myresult[1]}
    
    return f"Results for room {room['name']} with the question {room['question']}: \n\n {result}"

    