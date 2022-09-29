from flask import Flask, redirect, url_for, render_template

from proscan import PriorStage

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

    # testing: move to provided coordinates
    # coordinate provided in JSON format
    # if the stage is already at those coordinates, it will not move
    p.move_to({'x': -100000, 'y': -100000})
    p.move_to({'x': 100000, 'y': 100000})

    # close serial port communication
    p.close()
    return render_template('running_test_page.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')