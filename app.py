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
import random


# Connect Arcus
client = Arcus(ArcusLocator(ArcusMCNodeAllocator(ArcusTranscoder())))
client.connect("172.17.0.3:2181,172.17.0.4:2181,172.17.0.5:2181", "studio-cloud")

# Connect mySQL
db = mysql.connector.connect(user='root', host='127.0.0.1', port='3306', password='password')
cur = db.cursor()

def randomEleCreate(n):
    flag = random.randint(0,255)
    
    cur.execute("INSERT INTO User VALUES ('%d', 'some contents', '%d');" % (n, flag))
    db.commit()


app = Flask(__name__)

# Init Page
@app.route("/")
def init():
    # close & delete DB if exist
    cur.execute("DROP DATABASE IF EXISTS TimeLine;")

    # DB initialization
    cur.execute("CREATE DATABASE TimeLine;")
    cur.execute("USE TimeLine;")

    # ID | CONTENT | FLAG(GROUP)
    cur.execute("CREATE TABLE User (ID INT, Contents VARCHAR(100), Flag INT);")

    for i in range(100):
        randomEleCreate(i)

    # get current data
    cur.execute("SELECT * FROM User;")
    items = [dict(id=row[0], content=row[1], flag='{0:08b}'.format(row[2])) for row in cur.fetchall()]
    
    return render_template('index.html', items = items)


# Search with flag thru mySQL
@app.route("/search_with_sql", methods=['POST'])
def search_sql():
    flaglist = request.form['flag_list']
    flags = ' '.join(flaglist.split())
    
    
    # flag operation
    flag = 0
    for i in flags.split(' '):
        flag = flag + (2**int(i))

    # get current data
    cur.execute("SELECT * FROM User WHERE (Flag&%d);" % flag)
    items = [dict(id=row[0], content=row[1], flag='{0:08b}'.format(row[2])) for row in cur.fetchall()]

    return render_template('search_with_sql.html', items = items)

@app.route("/search_with_arcus", methods=['GET'])
def search_arcus():
    print 'a'

if __name__ == '__main__':
    app.run(debug=True)
