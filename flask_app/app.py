from flask import Flask, render_template, redirect, url_for, request
from celery import Celery
import mysql.connector

import time

app = Flask(__name__)
simple_app = Celery('simple_worker', broker='redis://redis:6379/0', backend='redis://redis:6379/0')

@app.route('/simple_start_task')
def call_method():
    app.logger.info("Invoking Method ")
    #    queue name in task folder.function name
    r = simple_app.send_task('tasks.longtime_add', kwargs={'x': 1, 'y': 2})
    app.logger.info(r.backend)
    return r.id

@app.route('/simple_task_result/<task_id>')
def task_result(task_id):
    result = simple_app.AsyncResult(task_id).result
    return "Result of the Task " + str(result)

@app.route("/admin/createroom", methods=["POST", "GET"])
def createroom():
    if request.method == "POST":
        key_request_ = request.form.keys()            
        key_request = list(key_request_)

        if key_request == ['room_name']:            
            value_request = request.form.values()
            room_name_list = list(value_request)
            room_name = str(room_name_list[0])
            
            app.logger.info("Invoking Method ")
            room = simple_app.send_task('tasks.room', kwargs={"name": room_name})
            app.logger.info(room.backend)
            time.sleep(4)
            return redirect(url_for("adminroom", room_id=room.id))
            
    return render_template("admin/createroom.html")

@app.route('/admin/room_status/<room_id>')
def get_status(room_id):
    status = simple_app.AsyncResult(room_id, app=simple_app)
    print("Invoking Method ")
    return "Status of the Task " + str(status.state)

@app.route("/admin/room/<room_id>", methods=["POST", "GET"])
def adminroom(room_id):
    room = simple_app.AsyncResult(room_id).result
    
    if request.method == "POST":
        key_request_ = request.form.keys()            
        key_request = list(key_request_)

        if key_request == ['question']:            
            value_request = request.form.values()
            question_list = list(value_request)
            question = str(question_list[0])
        
            app.logger.info("Invoking Method ")
            question_task = simple_app.send_task('tasks.room', kwargs={"name": room["name"] ,"question": question})
            app.logger.info(question_task.backend)
            time.sleep(4)

            return redirect(url_for("adminresults", room_id=question_task.id))
    return render_template("admin/question.html", room_id=room_id, room_name=room["name"])

@app.route("/admin/results/room/<room_id>", methods=["POST", "GET"])
def adminresults(room_id):
    room = simple_app.AsyncResult(room_id).result
    try:
        f = open("result.txt", "r")
        result = f.read()
        if result is None:
            result = {"yes": 0, "no": 0}
    except:
        result = {"yes": 0, "no": 0}
    return render_template("admin/result.html", room_name=room["name"], room_question=room["question"], result=result, room_id=room_id)


@app.route("/user/room/<room_id>", methods=["POST", "GET"])
def room(room_id):
    room = simple_app.AsyncResult(room_id).result

    if request.method == "POST":
        key_request_ = request.form.keys()            
        key_request = list(key_request_)

        if key_request == ['yes',]:            
            app.logger.info("Invoking Method ")
            question_task = simple_app.send_task('tasks.voting', kwargs={"vote": "y"})
            app.logger.info(question_task.backend)
            time.sleep(4)
            return redirect(url_for("result", result_id=question_task.id))

        else:            
            app.logger.info("Invoking Method ")
            question_task = simple_app.send_task('tasks.voting', kwargs={"vote": "n"})
            app.logger.info(question_task.backend)
            time.sleep(4)
            return redirect(url_for("result", result_id=question_task.id))

    return render_template("user/room.html", room_name=room["name"], room_question=room["question"])

@app.route("/user/results/<result_id>")
def result(result_id):
    result = simple_app.AsyncResult(result_id).result
    return str(result)

