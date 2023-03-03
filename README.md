# Integrate_Microscope_eeDAP

## Folder Structure

Folder structure is as follows:

.

├── CoreLogs/

├── hardware_control/

│   ├── grasshopper_cam_usb/

│   ├── miscellaneous_rough_drafts/

│   ├── prior_stage/

│   │    ├── proscan.py

│   ├── base_stage.py

│   ├── check_ports.py

│   ├── move_stage_tester.py

│   └── requirements.txt

├── micromanager_files/

└── README.md

The micromanager_files/ and CoreLogs/ are remnants of configuration files, Pycro-Manager scripts, and log files from attempts to use µManager for the microscope hardware control before transitioning to a Python script from scratch, based on source code from the Python-Microscope and the OpenFlexure server microscope hardware control.

 
Under the folder hardware_control/:

•	grasshopper_cam_usb/ : this is where future Python scripts for controlling the Point Grey Grasshopper cameras used by eeDAP will live

•	miscellaneous_rough_drafts/ : these are drafts of my earlier commits and test files that I used while creating the hardware control for the Prior ProScan III controller

•	requirements.txt: a text file containing the libraries that will be installed using pip, the package installer for Python

•	base_stage.py: contains the abstract parent class BaseStage, for all stages. Currently, its only child class is PriorStage, but will be used as a parent class for all stages used by eeDAP (Ludl stages)

•	check_ports.py: auxiliary Python script to check for devices currently connected to the host computer via serial port

•	prior_stage/proscan.py: defines the class PriorStage, whose parent class is BaseStage. Its most important attribute is its serial connection, defined by the class _PriorConnection. Using PySerial’s serial.Serial, it initializes the Python serial port communication to the Prior ProScan III controller, “talking” in messages composed of bytes. For more detail on what types of commands this controller accepts, refer to the user manual for this controller (Section 4: Software Commands). 

   Note that the move_to method for the PriorStage is designed to accept xy coordinates in JSON format. This was intentional – the xy coordinates for ROIs of a slide saved in caMicroscope’s Mongo database are in JSON format. These are then converted to a byte string that is comprehensible to the ProScan III controller.

•	move_stage_tester.py: an example Python script that initializes a PriorStage object, and moves to the provided coordinates. This script will be run manually through the command line to test that this code works.


The library used for serial port communication is PySerial, and the latest Python version it runs on is Python 3.8. These instructions will run through the download of this repository and running the test script in Python 3.8.10 in a virtual environment – the corresponding pip version is 21.1.1.