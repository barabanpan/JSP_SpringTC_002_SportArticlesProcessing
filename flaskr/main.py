from flask import Flask


app = Flask(__name__)


@app.route('/')
def index():
    return "This thing is working!"


if __name__ == "__main__":
    app.run()
