import MySQLdb
import mysql.connector
import random
from flask import json

def getMysqlConnection():
        return mysql.connector.connect(user='root', host='127.0.0.1', port='3306', password='password')


def createDB():
    db = getMysqlConnection()

    cur = db.cursor()
    cur.execute("CREATE DATABASE Friend;")
    cur.execute("USE Friend;")


# add friend randomly
def createPerson(n):
    
    db = getMysqlConnection()
    cur = db.cursor()
    cur.execute("USE Friend;")

    table = 'User' + str(n)
    
    cur.execute("CREATE TABLE %s (User VARCHAR(10));" % table)

    arr = range(n)
    random.shuffle(arr)
    if n > 1:
        m = random.randint(1,n-1)
    else:
        m = n

    for i in arr[0:m]:
        cur.execute("INSERT INTO %s VALUES ('%s');" % (table, str(i)))

        friend_table = 'User' + str(i)
        cur.execute("INSERT INTO %s VALUES ('%s');" % (friend_table, str(n)))
        db.commit()


def initDB():
    for i in range(20):
        createPerson(i)

def cleanDB():
    db = getMysqlConnection()
    cur = db.cursor()
    cur.execute("DROP DATABASE Friend;")
    db.close()


def getAllPeople():
    db = getMysqlConnection()
    cur = db.cursor()
    cur.execute("USE Friend")

    cur.execute("SELECT table_name FROM information_schema.tables where table_schema='Friend';")
    table = cur.fetchall()
    
    for i in table:
        query = ""
        query += "SELECT * FROM "
        query += str(i[0])
        query += ";"
       
        cur.execute(query)
        element = cur.fetchall()
        
        ele_list = []
        for ele in element:
            eleDict = {
                    'source' : str(i[0]),
                    'target' : "User"+str(ele[0])
            }
            print(eleDict)
            ele_list.append(eleDict)
    
    return json.dumps(ele_list)
