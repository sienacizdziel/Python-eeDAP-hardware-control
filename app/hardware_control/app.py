from flask import Flask, redirect, url_for, render_template, Response, request, session
from flask_session import session
import cv2

from proscan import PriorStage
from camera import Grasshopper3Camera

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stage_test')
def stage_test():

    print("running move stage tester")

    # initialize communication with Prior ProScan III
    # input the appropriate COM port
    p = PriorStage("COM4")

    # # testing: move to provided coordinates
    # # coordinate provided in JSON format
    # # if the stage is already at those coordinates, it will not move
    # p.move_to({'x': -100000, 'y': -100000})
    # p.move_to({'x': 100000, 'y': 100000})

    # visit each ROI coordinate
    for x, y in session['roi_coords']:
        p.move_to({'x': x, 'y': y})

    # close serial port communication
    p.close()
    return render_template('running_test_page.html')

@app.route('/admin_screen', methods=['GET', 'POST'])
def admin_screen():
    if request.method == 'POST':
        # reads data from uploaded dapsi file
        f = request.files['file']
        f.save(f.filename)
        print(f)

        # data within GUI.m (myData) in MATLAB
        session['roi_coords'] = None
        print(session['roi_coords'])

        return redirect('/camera')
    else:
        return render_template('admin_screen.html')

@app.route('/camera', methods=['GET', 'POST'])
# route for testing the camera
def camera():
    if request.method == 'POST':
        cam.take_image()
        return Response(cam.camera_preview(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        print("showing live image")
        cam = Grasshopper3Camera()
        print("outside cam")
        cam.camera_preview()
        return render_template('camera.html')
        # return Response(cam.camera_preview(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')