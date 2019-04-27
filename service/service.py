from flask import Flask, request, Response, jsonify, send_file
from flask_cors import CORS
import time

import controller as CTL
import pixels as PX
import mixer as MX
import state as ST

app = Flask(__name__)
CORS(app)


@app.route('/make_cocktail', methods=['GET'])
def make_cocktail():
    if request.method == 'GET':
        name = request.args['name']

        if not ST.is_glass:
            return "Please put a glass"
        
        if ST.making_cocktail:
            return not_acceptable(error_message="cocktail maker is busy")
        
        message = MX.mix_cocktail(name)
        if message.startswith("Error"):
            return not_acceptable(error_message=message)
        else:
            return message
    else:
        return method_not_allowed()


@app.route('/cancel', methods=['GET'])
def cancel():
    if request.method == 'GET':
        ST.cancel = True
        time.sleep(2)
        ST.making_cocktail = False
        ST.cancel = False
        return "canceld"
    else:
        return method_not_allowed()
    

@app.route('/image', methods=['GET'])
def get_image():
    if request.method == 'GET':
        name = request.args['name']
        path = MX.get_image_path(name)
        if path is not None:
            return send_file(path, mimetype="image/jpeg")
        else:    
            return not_acceptable(error_message="name could not be found")


@app.route('/cocktail_info', methods=['GET'])
def get_cocktail_info():
    if request.method == 'GET':
        name = request.args['name']
        info = MX.cocktail_info(name)
        if info is not None:
            return jsonify(info)
        else:
            return not_acceptable(error_message="cocktail not found") 
    else:
        return method_not_allowed()


@app.route('/init', methods=['PUT'])
def init():
    if request.method == 'PUT':
        if request.headers['Content-Type'] == 'application/json':
            init_status = request.get_json()
            MX.init(init_status)
            return "smart bartender is filled"
        else:
            return unsupported_media_type()
    else:
        return method_not_allowed()


@app.route('/load', methods=['GET'])
def load():
    if request.method == 'GET':
        MX.load_drink(request.args['tray'],
             request.args['drink'],
             request.args['size'],
             request.args['capacity'])
        return "Drink is loaded"
    else:
        return method_not_allowed()


@app.route('/status', methods=['GET'])
def get_status():
    if request.method == 'GET':
        return jsonify(MX.get_status())
    else:
        return method_not_allowed()

@app.route('/machine_state', methods=['GET'])
def get_machine_state():
    if request.method == 'GET':
        current_state = ''
        if not ST.making_cocktail:
            current_state = 'ready'
        elif ST.is_glass:
            current_state = 'making'
        else:
            current_state = 'blocked'

        state = {
                'duration':ST.duration,
                'remaining_time':ST.remaining_time,
                'time_taken':ST.time_taken,
                'state':current_state
                }

        return jsonify(state)
    else:
        method_not_allowed()

@app.route('/makeable_cocktails', methods=['GET'])
def get_makable_cocktails():
    if request.method == 'GET':
        return jsonify(MX.makeables())
    else:
        return method_not_allowed()


@app.route('/clean', methods=['GET'])
def clean():
    if request.method == 'GET':
        CTL.all_motors_on()
    else:
        return method_not_allowed()
    return "start cleaning"


@app.route('/stop_cleaning', methods=['GET'])
def stop_cleaning():
    if request.method == 'GET':
        CTL.all_motors_off()
    else:
        return method_not_allowed()
    return "cleaning stoped"


@app.errorhandler(406)
def not_acceptable(error=None, error_message=''):
    message = {
            'status':406,
            'message':error_message
            }
    resp = jsonify(message)
    resp.status_code = 406
    return resp


@app.errorhandler(415)
def unsupported_media_type(error=None):
    message = {
            'status':415,
            'message':'Unsupported media type'
            }
    resp = jsonify(message)
    resp.status_code = 415
    return resp


@app.errorhandler(405)
def method_not_allowed(error=None):
    message = {
            'status':405,
            'message':'Method not allowed for: ' + request.url
            }
    resp = jsonify(message)
    resp.status_code = 405
    return resp


try:
    CTL.init()
    CTL.all_off()
    PX.half_green()
    
    if __name__ == '__main__':
        app.run(host="0.0.0.0", port=8080)

except (KeyboardInterrupt, BaseException) as e:
#except Exception as e:
    print(e)

CTL.cleanup()

