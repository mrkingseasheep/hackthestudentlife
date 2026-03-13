from flask import Flask, render_template

app = Flask(__name__)
print("hello world")


@app.route("/")
def home():
    return "Hello World"


@app.route("/info/")
def info():
    return "Info"


@app.route("/hello/")
@app.route("/hello/<name>")
def hello(name=None):
    return render_template("hello.html", name=name)
    # return render_template("hello.html")
