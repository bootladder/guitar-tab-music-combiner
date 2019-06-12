from __future__ import print_function
import sys
import flask
from flask import Flask, render_template, request, send_from_directory
from flask_cors import CORS, cross_origin


########IPMORTS
sys.path.append('..')
from draw_tabglyphs_on_music import *

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def hello_worldz(path):
    flaskprint('path: ' + path)
    return "hello!"

def flaskprint(stupid):
    print(stupid, file=sys.stderr)

if __name__ == '__main__':

	app.run(debug = True,host='0.0.0.0', threaded=True)




