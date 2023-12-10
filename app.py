# ./app.py

from flask import Flask

app = Flask(__name__)

@app.route('/') # root directory
def index():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True) # debug mode on