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

@app.route('/not_download/<path:path>')
def not_download_image(path):
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


@app.route('/api/download_link', methods = ['GET'])
def wtf2_download():
      return send_from_directory(webroot, 'output.png')


@app.route('/api/download', methods = ['POST'])
def api_download():
    if False == request.is_json:
        flaskprint('no json')
        flaskprint(request)
        return 'not a json'
    requestjson = request.get_json()
    if 'image' not in requestjson:
        flaskprint('no image')
        return 'no image'

    # base64 -> img
    imgbase64 = requestjson['image']
    nparr = np.fromstring(imgbase64.decode('base64'), np.uint8)
    img_music = cv2.imdecode(nparr, 0)

    # img -> base64
    s, img_png = cv2.imencode(".png", img_music)

    return send_file(
        io.BytesIO(img_png),
        mimetype='image/png',
        as_attachment=True,
        attachment_filename='%s.png' % 'yay')





def crop_image(img, cropbox):

    x      = int(cropbox['x']     )
    y      = int(cropbox['y']     )
    width  = int(cropbox['width'] )
    height = int(cropbox['height'])

    flaskprint("CROPPING:  WIDTH HEIGHT OF BOX: %d %d "%(width,height))

    # cropbox is x and y, img is row and column
    newimg = img[y:y+height, x:x+width]


    flaskprint("CROPPED:  LEN OF NEWIMG : %d %d "%(len(newimg),len(newimg[0])))

    return newimg



def draw_combined_over_original(img_small, img_large, cropbox):

    x      = int(cropbox['x']     )
    y      = int(cropbox['y']     )

    #dimension of small image, because it's only the top half (the music) that gets pasted
    width  = len(img_small[0])
    height = len(img_small)


    flaskprint("CROP BOXSIZE: ")
    flaskprint("%d %d %d %d"%(x,y,width,height))

    flaskprint("IMG SMALL SIZE: ")
    flaskprint("%d %d "%(len(img_small),len(img_small[0])))

    img_large[y:y+height, x:x+width] = img_small
    return img_large




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

    # Crop
    img_music_cropped = crop_image(img_music, cropbox)

    # Split Image in Half, top and bottom
    img_split_top, img_split_bottom = split_image_top_bottom(img_music_cropped)

    # Process
    try:
        img_result       = draw_tabglyphs_on_music(img_split_top, img_split_bottom)
        img_orig_updated = draw_combined_over_original(img_result, img_music, cropbox)

        cv2.imwrite("frontend/output.png",img_orig_updated)

        message = "Great Result!"
        status = "OK"

    except:
        img_music_processed = imgmusic_preprocess(img_split_top)
        img_tab_processed   = imgtab_preprocess(img_split_bottom)
        img_result = np.concatenate((img_music_processed, img_tab_processed), axis=0)
        img_orig_updated = img_result
        message = "fail... maybe this helps?"
        status = "FAIL"


    # img -> base64
    s, img_result_png = cv2.imencode(".png", img_result)
    image_result_encoded = base64.b64encode(img_result_png)
    s, img_orig_updated_png = cv2.imencode(".png", img_orig_updated)
    image_orig_updated_encoded = base64.b64encode(img_orig_updated_png)

    d = dict()
    d['status'] = status
    d['message'] = message
    d['image'] = image_result_encoded
    d['image_updated'] = image_orig_updated_encoded

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




