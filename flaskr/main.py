from flask import Flask
from flask import render_template
from flask import request

import sys
sys.path.append("..")
from libs import for_table_one


app = Flask(__name__)


@app.route('/')
def input():
    return render_template('input.html', title="Input")


@app.route('/output', methods=['GET'])
def output_get():
    return render_template(
        'output.html', title="Output",
         get_message="To see results input data first: ")


@app.route('/output', methods=['POST'])
def output_post():
    article = request.form.get("article", "empty")
    length, ents_dict = for_table_one.get_tokens_and_labels(article)
    return render_template(
        'output.html', title="Output", ents_dict=ents_dict, length=length)


if __name__ == "__main__":
    app.run()
