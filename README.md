# Python eeDAP Hardware Control
## Folder Structure
Folder structure is as follows:

.

├── CoreLogs/

├── hardware_control/

│     ├── grasshopper_cam_usb/

│     │     ├── camera.py

│     ├── prior_stage/

│     │     ├── proscan.py

│     ├── templates/

│     │     ├── admin_screen.html

│     │     ├── camera.html

│     │     ├── index.html

│     │     ├── running_test_page.html

│     │     ├── stage_test.html

│     │     ├── error.html

│     ├── base_stage.py

│     ├── check_ports.py

│     ├── app.py

│     ├── task_helpers.py

│     ├── move_stage_tester.py

│     ├── .gitignore

│     └── requirements.txt

├── micromanager_files/

└── README.md


The micromanager_files/ and CoreLogs/ are remnants of configuration files, Pycro-Manager scripts, and log files from attempts to use µManager for the microscope hardware control before transitioning to a Python script from scratch, based on source code from the Python-Microscope and the OpenFlexure server microscope hardware control.

 
Under the folder `hardware_control/`:

- `grasshopper_cam_usb/camera.py`: defines the abstract parent class Camera, for all cameras. Currently, its only child class is Grasshopper3Camera, which uses the PySpin library to implement a function to view the camera video of a Grasshopper3 FLIR Camera with a USB 3.0 connector (the camera that is connected to the Blenman lab computer). The display pops up on a separate tkinter window

- `requirements.txt`: a text file containing the libraries that will be installed using pip, the package installer for Python. To install, run `pip install -r requirements.txt` from within a Python virtual environment

- `.gitignore`: specifies intentionally untracked files that Git should ignore

- `base_stage.py`: contains the abstract parent class BaseStage, for all stages. Currently, its only child class is PriorStage, but will be used as a parent class for all stages used by eeDAP (Ludl stages)

- `check_ports.py`: auxiliary Python script to check for devices currently connected to the host computer via serial port

- `prior_stage/proscan.py`: defines the class PriorStage, whose parent class is BaseStage. Its most important attribute is its serial connection, defined by the class _PriorConnection. Using PySerial’s serial.Serial, it initializes the Python serial port communication to the Prior ProScan III controller, “talking” in messages composed of bytes. For more detail on what types of commands this controller accepts, refer to the user manual for this controller (Section 4: Software Commands). 

   Note that the move_to method for the PriorStage is designed to accept xy coordinates in JSON format. This was intentional – the xy coordinates for ROIs of a slide saved in caMicroscope’s Mongo database are in JSON format. These are then converted to a byte string that is comprehensible to the ProScan III controller.

- `move_stage_tester.py`: an example Python script that initializes a PriorStage object, and moves to the provided coordinates. This script will be run manually through the command line to test that this code works.

- `app.py`: contains the Flask app initialization, session, and routes. Routes include '/', '/stage_test', '/admin_screen', '/camera'. 
   - '/' route:
      - `GET`: the initial landing page 
         - template: `index.html`
   - '/camera' route: 
      - `GET`: views a live camera image by showing a tkinter window of frames from the Grasshopper3Camera class
         - template: `camera.html`
      - `POST`: TODO (for taking a camera image)
   - '/admin_screen' route:
      - `GET`: simply renders the template to enable the user to upload a file
         - template: `admin_screen.html`
      - `POST`: read data from the uploaded dapsi file
         - template: `admin_screen.html`, sending filename through Jinja
   - '/stage_test' route:
      - `GET`: visit a new task on the stage, according to the tasks saved in the session
         - template: `stage_test.html`, sending task info through Jinja
      - `POST`: randomizes tasks and begins the process of visiting task coordinates on the stage
         - template: `stage_test.html`, sending task info through Jinja

- `task_helpers.py`: contains the Task class for reading tasks from the uploaded .dapsi file. Includes additional helper functions for ROI randomization and stage movement 

## Frameworks
This program is a Flask application calling Python scripts written to access the microscope hardware. The Flask application renders templates created in HTML (currently with minimal CSS) along with Jinja for custom templating. 

## Versions
- Python 3.8

## Usage
The code editor I would suggest to use is Visual Studio Code. If you would like to install VSCode, visit [this site](https://code.visualstudio.com/). 

The code for hardware control is located in this GitHub repository. This repository was forked off of [vstevensf’s Python-eeDAP-hardware-control repository](https://github.com/vstevensf/Python-eeDAP-hardware-control). 

To clone the repository, select the green “Code” button. Then run `git clone link`, in the command line after changing into the desired directory. 

In the event you run into SSH errors in command line, visit [this site](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account) to add an SSH access key to your GitHub account. This is a new GitHub update launched in 2022. 

To run the code, first install all requirements. On the command line, change into the Python-eeDAP-hardware-control/app/hardware_control directory. Next, create a virtual environment. 

On MacOS, to create a virtual environment titled venv, run: `python3.8 -m venv venv`

Though this can be done with the default Python version by removing the 3.8, the suggested Python version for this program would be 3.8. Running python3.8 automatically creates a virtual environment that uses 3.8 as its Python version.

To install required packages, first activate the virtual environment. On MacOS, the command is source `venv/bin/activate`. On Windows, the command is `venv\Scripts\activate`. Once the virtual environment is activated, install the required packages by running `pip install -r requirements.txt`. 

## Spinnaker SDK and PySpin Installation
In order to use the PySpin package, the Spinnaker SDK must first be installed.  To do this:
1.	Visit the Spinnaker SDK section of the FLIR website at: https://www.flir.com/products/spinnaker-sdk/.
2.	Select the blue DOWNLOAD NOW button.
3.	First log in via the profile image on the top right of the screen. Then, return to this page and fill out the Download Spinnaker SDK form on the right side of the screen.
4.	Once the form is submitted, you will be redirected to a screen titled “Spinnaker SDK Download.” Download the package for your OS: Windows, Linux, MacOS. For more information, visit my senior project write-up at Yale CPSC 490's website. 
5.	Once downloaded, open the zip files using the command: `unzip [file_name]`
6.	Enter the appropriate directory: `cd [file_name]`
7.	Make sure you are in your virtual environment. Once there, run: `python -m pip install [file_name.whl]`. This will install PySpin in your virtual environment. If you run into the error below for Python version 3.8, run `pip3.8 install [file_name.whl]`. This will force an install in the Python version required. 

