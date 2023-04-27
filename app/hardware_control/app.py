import os
from flask import Flask, render_template, Response, request, session
from flask_session import Session
from werkzeug.utils import secure_filename
from prior_stage.proscan import PriorStage
from grasshopper_cam_usb.camera import Grasshopper3Camera
from task_helpers import Task, randomize_tasks, visit_task, get_all_slide_numbers


""" 
Initialize Flask session for saving data between routes. 
Session contains: 
- tasks: a list of randomized Task objects, read from the dapsi file
- current_task_num: the index of the current task being read, initialized to 0 and incremented as tasks are visited via the stage
- slides: a list of possible slide numbers within the dapsi file (for example: ['81B', '82B', '83B'])
"""
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


""" homepage """
@app.route('/')
def index():
    return render_template('index.html')


""" page for visiting ROI coordinates via stage movement """
@app.route('/stage_test', methods=['GET', 'POST'])
def stage_test():
    OFFSET_CONSTANT = 200 # pixel size of each additional slide, as offset

    # on each POST request, visit a new task
    if request.method == 'POST':
      
      # access saved variables in session
      index = session['current_task_num']
      try:
        task = session['tasks'][index]
      except:
          # all tasks completed
          return render_template('running_test_page.html')
      slides = session['slides']

      # initialize stage class
      p = PriorStage("COM4")

      # visit desired task
      offset = slides.index(task._get_slide_number()) * OFFSET_CONSTANT # takes the index of the slide the task is on and multiplies by  offset constant
      visit_task(p, task, offset)
      
      # output values
      print(str(task._get_slide_number()) + " offset = " + str(slides.index(task._get_slide_number()) * 200))
      print("moved to task #%d at (%d, %d)" % (index, task.x, task.y))

      # update session task number for next task
      session['current_task_num'] += 1

      # close serial port communication
      p.close()

      # render test page with task info
      return render_template('stage_test.html', number=session['current_task_num']-1, x=task.x, y=task.y)
        
    else:
      print("running move stage tester")
      
      # check that tasks have been saved
      if not session['tasks']:
          return render_template('error.html', error='Could not find tasks. Return to landing page to upload file.')

      # initialize communication with Prior ProScan III
      # input the appropriate COM port
      p = PriorStage("COM4")

      # randomize ROI coordinates
      tasks = randomize_tasks(session['tasks'])
      slides = get_all_slide_numbers(tasks) # get all possible slide numbers in dapsi file

      # initialize session variables
      session['tasks'] = tasks
      session['current_task_num'] = 0
      session['slides'] = slides
      task = session['tasks'][session['current_task_num']]

      # visit the first task
      offset = slides.index(task._get_slide_number()) * OFFSET_CONSTANT
      visit_task(p, task, slides.index(task._get_slide_number()) * 200)

      # output values
      print(str(task._get_slide_number()) + " offset = " + str(slides.index(task._get_slide_number()) * 200))
      print("moved to task #%d at (%d, %d)" % (session['current_task_num'], task.x, task.y))
      
      # update session task number for next task
      session['current_task_num'] += 1

      # close serial port communication
      p.close()

      # render test page with task info
      return render_template('stage_test.html', number=session['current_task_num']-1, x=task.x, y=task.y)


""" landing page for uploading dapsi files """
@app.route('/admin_screen', methods=['GET', 'POST'])
def admin_screen():
    # read data from uploaded dapsi file
    if request.method == 'POST':
        f = request.files['file']

        if f.filename:
            # if file was uploaded successfully, temporarily save file for reading
            f.save(secure_filename(f.filename))
            print('The file was uploaded successfully')

        else:
            # if file was not uploaded successfully, return an error message for the user to try again
            print('No file was uploaded.')
            return render_template('admin_screen.html', error_message="No file uploaded.")
        
        """ 
        reads through file as a state machine with states: 
            "header"
            "settings"
            "body" 
        """
        read_state = "header"
        tasks = []
        with open(f.filename, "r") as tmp:

            # read temporarily saved file line by line
            for line in tmp:

                # currently skips over all settings
                # future TODO: save settings into session for use
                if "SETTINGS" in line:
                    read_state = "settings"

                elif "BODY" in line:
                    read_state = "body"

                elif read_state == "settings":
                    print(line) # can save into settings dictionary here to put into session

                elif read_state == "body":
                    if 'start' in line or 'finish' in line:
                        continue

                    # save tasks into task list
                    tasks.append(Task(line))

        os.remove(f.filename) # remove temporary file
        session['tasks'] = tasks # save tasks into session
        return render_template('admin_screen.html', uploaded=True, file=f.filename)
    else:
        # renders upload screen for dapsi file
        return render_template('admin_screen.html', uploaded=False)

""" route for testing the camera """
@app.route('/camera', methods=['GET', 'POST'])
def camera():
    """ 
    Successfully opens a tkinter display of the live video feed from a Grasshopper3 camera.

    At the moment, the camera display route is not fully functional. Because the code 
    uses a tkinter window, initializing the Grasshopper3Camera class immediately calls
    the camera_preview method. When the tkinter window is closed, the program quits on an
    error, and the final Response return is never reached. See project write-up for 
    tips on how to address this issue.  
    """
    if request.method == 'POST':
        # cam.take_image() (TODO: does not successfully take photo via tkinter)
        return Response(cam.camera_preview(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        print("showing live image")

        # initialize Grasshopper3Camera (immediately opens display of live feed)
        cam = Grasshopper3Camera()

        # note that at the moment this route does not work properly,
        # because once the tkinter window closes, the program quits
        # so the following line is never reached
        return Response(cam.camera_preview(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')
    