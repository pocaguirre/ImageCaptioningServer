from flask import Flask
from model import Tasks

engine = Tasks()
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
