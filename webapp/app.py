from __future__ import print_function
import sys
import flask
from flask import * #Flask, render_template, request, send_from_directory
from flask_cors import CORS, cross_origin
import io

########IPMORTS
sys.path.append('..')
from draw_tabglyphs_on_music import *

app = Flask(__name__)

webroot = 'frontend'

@app.route('/download/<path:path>')
def download_image(path):
    flaskprint('path: ' + path)

    img_music =  cv2.imread('input/music1.png',0)
    img_tab   =  cv2.imread('input/tab1.png',0)
    img_result = draw_tabglyphs_on_music(img_music, img_tab)
    status, img_png = cv2.imencode(".png", img_result)

    return send_file(
        io.BytesIO(img_png),
        mimetype='image/png',
        as_attachment=True,
        attachment_filename='%s.png' % 'yay')

@app.route('/api/upload', methods = ['POST'])
def api_upload():

    flaskprint(request.files)
    if 'image' not in request.files:
        flaskprint('no image')
        return "not in there"
    flaskprint('\n\nrequest.files:  ' + request.files['file'].filename )
    #f = request.files.values()[0]
    f = request.files['file']
    pathtofile = '/tmp/yay'
    f.save(pathtofile)
    flaskprint('[route] Received a File, saved blob to'+pathtofile+'\n')
    return 'aye'












@app.route('/api/process/music', methods = ['POST'])
def api_process():

    if False == request.is_json:
        flaskprint('no json')
        return 'not a json'
    requestjson = request.get_json()
    if 'image' not in requestjson:
        flaskprint('no image')
        return 'no image'

    return request.get_json()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def hello_worldz(path):
    flaskprint('path: ' + path)
    if path == '':
      return send_from_directory(webroot, 'index.html')

    return send_from_directory(webroot, path)

def flaskprint(stupid):
    print(stupid, file=sys.stderr)

if __name__ == '__main__':

	app.run(debug = True,host='0.0.0.0', threaded=True)




