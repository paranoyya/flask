from typing import Any, Union

from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.datastructures import ImmutableMultiDict
from wtforms.validators import DataRequired
from wtforms import TextAreaField

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URL'] = 'postgresql://10.252.40.4:Password@localhost/rvision'
db = SQLAlchemy(app)



@app.route("/", methods = ['GET'])
def index():
    return render_template('index.html')


@app.route("/searching/", methods = ['GET', 'POST'])
def main():
    return render_template('searching.html')

@app.route('/result', methods = ['POST, GET'])
def result():
    message = ''
    if request.method == 'POST':
        result = request.form
        result = TextAreaField('wordforsearch', validators=[DataRequired()])
    else:
        message = 'Введите слово'
    return render_template('result.html', result=result)

#@app.route("/add_word/")
#def add_word():
    #from werkzeug.utils import redirect
    #return redirect(url_for('main'))


if __name__ == "__main__":
    app.run(debug=True)

