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

ELEMENT_SIZE = 10

# Connect Arcus
client = Arcus(ArcusLocator(ArcusMCNodeAllocator(ArcusTranscoder())))
#client.connect("172.17.0.3:2181,172.17.0.4:2181,172.17.0.5:2181", "studio-cloud")
client.connect("172.17.0.3:2181", "studio-cloud")

# Connect mySQL
db = mysql.connector.connect(user='root', host='127.0.0.1', port='3306', password='password')
cur = db.cursor()

ret = client.delete("Timeline:btree_eflag")
print "delete"
print ret.get_result()
    
# Create Arcus Tree
timeout = 10
ret = client.bop_create("Timeline:btree_eflag", ArcusTranscoder.FLAG_INTEGER, timeout)
print "btree_eflag Create"
print ret.get_result()

def init():
    # close & delete DB if exist
    cur.execute("DROP DATABASE IF EXISTS TimeLine;")
   
    # DB initialization
    cur.execute("CREATE DATABASE TimeLine;")
    cur.execute("USE TimeLine;")

    # ID | CONTENT | FLAG(GROUP)
    cur.execute("CREATE TABLE User (ID INT, Contents VARCHAR(100), Flag INT);")

    # Make element
    for i in range(ELEMENT_SIZE):
        randomEleCreate(i)

# Integer to Hex
def itoh(i):
    h = hex(i)
    if len(h) % 2 == 1:
        h = '0x0%s' % h[2:].upper()
    else:
        h = '0x%s' % h[2:].upper()
    return h


# Make Random Element
def randomEleCreate(n):
    flag = random.randint(0,255)
    
    cur.execute("INSERT INTO User VALUES ('%d', 'some contents', '%d');" % (n, flag))
    db.commit()

    # Insert into Arcus
    # key | bkey | value | eflag
    ret = client.bop_insert("Timeline:btree_eflag", n, flag, itoh(flag))
    print ret.get_result()


###### init ######
app = Flask(__name__)
init()
##################

# Home Page
@app.route("/")
def home():
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

# Search with flag thru Arcus
@app.route("/search_with_arcus", methods=['POST'])
def search_arcus():
    flaglist = request.form['flag_list']
    flags = ' '.join(flaglist.split())

    flag = 0
    for i in flags.split(' '):
        flag = flag + (2**int(i))

    eflag = 'EFLAG & 0x00ff == ' + itoh(flag)
    print eflag

    ret = client.bop_get("Timeline:btree_eflag", (0,10), EflagFilter('EFLAG & 0x00ff == 0x0001'))
    #ret = client.bop_get("Timeline:btree_eflag",(0,ELEMENT_SIZE), EflagFilter(eflag))
    print ret.get_result()

    return render_template('search_with_arcus.html')


client.disconnect()

if __name__ == '__main__':
    app.run(debug=True)
