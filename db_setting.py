import MySQLdb
import mysql.connector
import random

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



