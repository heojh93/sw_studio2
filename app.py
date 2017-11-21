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

from db_setting import *

client = Arcus(ArcusLocator(ArcusMCNodeAllocator(ArcusTranscoder())))
client.connect("172.17.0.3:2181", "rou91-cloud")

# test
ret = client.set('test:string1', 'test...', 10)
print ret.get_result()
assert ret.get_result() == True

# close & delete DB
cleanDB()


# DB initialization
createDB()
initDB()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False)
