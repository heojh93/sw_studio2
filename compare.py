from __future__ import absolute_import

# Import from different folder
import sys
sys.path.insert(0, './arcus-python2-client')

# Import Arcus
from arcus import *
from arcus_mc_node import ArcusMCNodeAllocator
from arcus_mc_node import EflagFilter

# Import flask
from flask import Flask
from flask import render_template
from flask import request

# Import mySQL
import MySQLdb
import mysql.connector

# Import nbase-ARC
import redis

# Other
import string
import random

ELEMENT_SIZE = 100
STRING_LENGTH = 100
timeout = 10

# Connect Arcus
client = Arcus(ArcusLocator(ArcusMCNodeAllocator(ArcusTranscoder())))
#client.connect("172.17.0.3:2181,172.17.0.4:2181,172.17.0.5:2181", "studio-cloud")
client.connect("172.17.0.3:2181", "studio-cloud")

# Connect mySQL
db = mysql.connector.connect(user='root', host='127.0.0.1', port='3306', password='password')
cur = db.cursor()

# Conenct nbase-ARC
nbase = redis.StrictRedis(port=6000)

# Make Random Element
def randomElement(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


app = Flask(__name__)


# Home Page
@app.route("/")
def home():

    # close & delete DB if exist
    cur.execute("DROP DATABASE IF EXISTS Comp;")
   
    # DB initialization
    cur.execute("CREATE DATABASE Comp;")
    cur.execute("USE Comp;")
 
    # KEY | VALUE
    cur.execute("CREATE TABLE testSQL (_Key INT, Val VARCHAR(100));")
    
    # INSERT DATA
    for i in range(ELEMENT_SIZE) :
        cur.execute("INSERT INTO testSQL VALUES ('%d', '%s');" % (i, randomElement(STRING_LENGTH)))
        db.commit()
 
    return render_template('compare_home.html')


# mySQL TEST
@app.route("/mysql", methods=['POST'])
def sql_test():
    
    # GET DATA
    items = []
    for i in range(200) :
        n = random.randint(0,ELEMENT_SIZE)
        cur.execute("SELECT * FROM testSQL WHERE _Key=%d;" % n)
        for item in cur.fetchall() :
            items.append([item[0], item[1]])


    return render_template('sql_test.html', items = items)



# Arcus TEST
@app.route("/arcus", methods=['POST'])
def arcus_test():

    Hit = 0
    Miss = 0

    items = []
    for i in range(200) :
        n = random.randint(0,ELEMENT_SIZE)

        ret = client.get('testArcus:%d' % n)

        if ret.get_result() == None :
            print "MISS : %d" % n
            Miss += 1
            cur.execute("SELECT * FROM testSQL WHERE _Key=%d;" % n)
            
            for item in cur.fetchall() :
                e = item[1]
            print e
            ret = client.set('testArcus:%d' % n, str(e), timeout)
            items.append([i, e])
            
        else :
            print "HIT : %d" % n
            Hit += 1
            items.append([i, ret.get_result()])

    print "Hit = %d, Miss = %d" % (Hit, Miss)
    print "Hit Ratio = %f" % (Hit*100/(Hit+Miss))

    return render_template('arcus_test.html', items=items)


# nbase-ART TEST
@app.route("/nbase", methods=['POST'])
def nbase_test():

    Hit = 0
    Miss = 0

    items = []
    for i in range(200) :
        n = random.randint(0,ELEMENT_SIZE)

        ret = nbase.get('testNBASE:%d' % n)

        if ret == None :
            print "MISS : %d" % n
            Miss += 1
            cur.execute("SELECT * FROM testSQL WHERE _Key=%d;" % n)
            
            for item in cur.fetchall() :
                e = item[1]

            ret = nbase.set('testNBASE:%d' % n, e)
            items.append([i, e])

        else :
            print "HIT : %d" % n
            Hit += 1
            items.append([i, ret])

    print "Hit = %d, Miss = %d" % (Hit, Miss)
    print "Hit Ratio = %f" % (Hit*100/(Hit+Miss))

    return render_template('nbase_test.html', items=items)


#client.disconnect()

if __name__ == '__main__':
    app.run(debug=False)
