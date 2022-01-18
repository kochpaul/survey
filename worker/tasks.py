import time
from celery import Celery
from celery.utils.log import get_task_logger

import mysql.connector

logger = get_task_logger(__name__)

app = Celery('tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0')


@app.task()
def longtime_add(x, y):
    logger.info('Got Request - Starting work ')
    time.sleep(4)
    logger.info('Work Finished ')
    return x + y

@app.task()
def createroom(name):
    logger.info('Got Request [create room] - Starting work ')
    time.sleep(3) 
    logger.info('Work Finished ')
    return name

@app.task()
def question(question):
    logger.info('Got Request [create room] - Starting work ')
    time.sleep(3) 
    logger.info('Work Finished ')
    return question



@app.task()
def voting(vote, room_id):
    logger.info('Got Request [voting] - Starting work ')
    cnx = mysql.connector.connect(user='root', password='root',
                                    host='db',
                                    database='survey')

    cursor = cnx.cursor()
    if vote == "y":
        sql = "UPDATE voting SET yes = yes + 1 WHERE room_id = %s"
        val = (room_id, )
        cursor.execute(sql,val)
        cnx.commit()
        cursor.close()

    else:
        sql = "UPDATE voting SET no = no + 1 WHERE room_id = %s"
        val = (room_id, )
        cursor.execute(sql,val)
        cnx.commit()
        cursor.close()

    logger.info('Work Finished ')
    return result


@app.task()
def room(name=None, question=None, result={"yes": 0, "no": 0}):
    logger.info('Got Request [create room] - Starting work ')
    time.sleep(1) 

    room = {
        "name" : name,
        "question" : question, 
        "result" : result
    }
    logger.info('Work Finished ')
    return room
