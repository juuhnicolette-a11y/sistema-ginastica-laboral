from flask import Flask

app = Flask(__name__)


@app.route("/")
def inicio():
    return "Ginástica em Dia"


if __name__ == "__main__":
    app.run(debug=True)