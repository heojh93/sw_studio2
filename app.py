from flask import Flask
from flask import render_template

from db_setting import *
import MySQLdb

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
