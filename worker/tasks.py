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


result = {"yes": 0, "no": 0}
@app.task()
def voting(vote):
    logger.info('Got Request [voting] - Starting work ')
    time.sleep(3)

    if vote == "y":
        result["yes"] = result["yes"] + 1 
    
    else:
        result["no"] = result["no"] + 1 

    print(result)
    logger.info('Work Finished ')
    f = open("result.txt", "w")
    f.write(result)
    f.close()
    return result


@app.task()
def room(name=None, question=None):
    logger.info('Got Request [create room] - Starting work ')
    time.sleep(3) 

    room = {
        "name" : name,
        "question" : question, 
        "result" : result
    }
    logger.info('Work Finished ')
    return room
