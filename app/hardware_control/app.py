from flask import Flask, redirect, url_for, render_template, Response, request, session
from flask_session import Session
from time import sleep
import os
from werkzeug.utils import secure_filename

from prior_stage.proscan import PriorStage
from camera import Grasshopper3Camera
from task_helpers import Task, randomize_tasks, visit_task, get_all_slide_numbers

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stage_test')
def stage_test():

    print("running move stage tester")

    # initialize communication with Prior ProScan III
    # input the appropriate COM port
    p = PriorStage("COM4")
    # p = PriorStage("/dev/ttyACM0")

    # # testing: move to provided coordinates
    # # coordinate provided in JSON format
    # # if the stage is already at those coordinates, it will not move
    # p.move_to({'x': -100000, 'y': -100000})
    # p.move_to({'x': 100000, 'y': 100000})

    # visit each ROI coordinate
    tasks = randomize_tasks(session['tasks'])
    # explain offset process
    slides = get_all_slide_numbers(tasks)
    print(slides)
    print(tasks)
    for i, task in enumerate(tasks[:10]):
        visit_task(p, task, slides.index(task._get_slide_number()) * 200)
        print(slides.index(task._get_slide_number()))
        print(str(task._get_slide_number()) + " offset = " + str(slides.index(task._get_slide_number()) * 200))
        print("moved to task #%d at (%d, %d)" % (i, task.x, task.y))
        sleep(5)
    # for task in session['tasks']:
    #     p.move_to({'x': task.x, 'y': task.y})

    # close serial port communication
    p.close()
    return render_template('running_test_page.html')

@app.route('/admin_screen', methods=['GET', 'POST'])
def admin_screen():
    if request.method == 'POST':
        # reads data from uploaded dapsi file
        f = request.files['file']
        if f.filename:
            f.save(secure_filename(f.filename))
            print('The file was uploaded successfully')
        else:
            print('No file was uploaded.')
            return render_template('admin_screen.html', error_message="No file uploaded.")
        read_state = "header"
        tasks = []
        with open(f.filename, "r") as tmp:
            print("here")
            for line in tmp:
                print(line)
                if "SETTINGS" in line:
                    read_state = "settings"
                elif "BODY" in line:
                    read_state = "body"
                elif read_state == "settings":
                    # read in settings, saved in settings dict
                    # keys: n_wsi
                    print(line)
                elif read_state == "body":
                    if 'start' in line or 'finish' in line:
                        continue
                    # task input format: string from dapsi file
                    # contains task name, task ID, task order, slot, ROI_X, ROI_Y, ROI_W, ROI_H, Q_text
                    print(line)
                    tasks.append(Task(line))

        os.remove(f.filename)
        session['tasks'] = tasks
        return render_template('admin_screen.html', uploaded=True, file=f.filename)
    else:
        return render_template('admin_screen.html', uploaded=False)

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
        # return render_template('camera.html')
        return Response(cam.camera_preview(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')