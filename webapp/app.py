from __future__ import print_function
import sys
import flask
from flask import * #Flask, render_template, request, send_from_directory
from flask_cors import CORS, cross_origin
import io
import base64

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









def crop_image(img, cropbox):

    x      = int(cropbox['x']     )
    y      = int(cropbox['y']     )
    width  = int(cropbox['width'] )
    height = int(cropbox['height'])

    # cropbox is x and y, img is row and column
    newimg = img[y:y+height, x:x+width]
    return newimg


def split_image_top_bottom(img):
    num_rows = len(img)
    img_top = img[0:(num_rows/2) , :]
    img_bot = img[(num_rows/2) : num_rows , :]
    return img_top,img_bot


@app.route('/api/process/combined', methods = ['POST'])
def api_process_combined():

    if False == request.is_json:
        flaskprint('no json')
        flaskprint(request)
        return 'not a json'
    requestjson = request.get_json()
    if 'image' not in requestjson:
        flaskprint('no image')
        return 'no image'
    if 'metadata' not in requestjson:
        flaskprint('no metadata')
        return 'no metadata'

    cropbox = requestjson['metadata']
    cropbox_x = cropbox['x']
    cropbox_y = cropbox['y']
    cropbox_width = cropbox['width']
    cropbox_height = cropbox['height']

    flaskprint("%f %f %f %f"%(cropbox_x, cropbox_y, cropbox_width, cropbox_height))

    # base64 -> img
    imgbase64 = requestjson['image']
    nparr = np.fromstring(imgbase64.decode('base64'), np.uint8)
    img_music = cv2.imdecode(nparr, 0)

    # crop image
    img_music_cropped = crop_image(img_music, cropbox)

    # Split Image in Half, top and bottom
    img_split_top, img_split_bottom = split_image_top_bottom(img_music_cropped)

    # process
    centers = imgmusic_to_notecoordinates(img_split_top)
    glyphs  = imgtab_to_glyphs(img_split_bottom)

    img_result = draw_tabglyphs_on_music(img_split_top, img_split_bottom)

    # img -> base64
    status, img_png = cv2.imencode(".png", img_result)
    encoded = base64.b64encode(img_png)

    d = dict()
    d['yay'] = 'yay'
    d['image'] = encoded

    return jsonify(d)



@app.route('/api/process/music', methods = ['POST'])
def api_process():

    if False == request.is_json:
        flaskprint('no json')
        flaskprint(request)
        return 'not a json'
    requestjson = request.get_json()
    if 'image' not in requestjson:
        flaskprint('no image')
        return 'no image'
    if 'metadata' not in requestjson:
        flaskprint('no metadata')
        return 'no metadata'

    cropbox = requestjson['metadata']
    cropbox_x = cropbox['x']
    cropbox_y = cropbox['y']
    cropbox_width = cropbox['width']
    cropbox_height = cropbox['height']

    flaskprint("%f %f %f %f"%(cropbox_x, cropbox_y, cropbox_width, cropbox_height))

    # base64 -> img
    imgbase64 = requestjson['image']
    nparr = np.fromstring(imgbase64.decode('base64'), np.uint8)
    img_music = cv2.imdecode(nparr, 0)

    # crop image
    img_music_cropped = crop_image(img_music, cropbox)

    # process
    img_result = imgmusic_preprocess(img_music_cropped)


    # img -> base64
    status, img_png = cv2.imencode(".png", img_result)
    encoded = base64.b64encode(img_png)

    d = dict()
    d['yay'] = 'yay'
    d['image'] = encoded

    return jsonify(d)

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




