import time
import threading
import pygal

from flask import Flask
from temp_reader import read_device_file
from pygal.style import NeonStyle

from Remote_Outlet.control import turn_off, turn_on

app = Flask(__name__)

bath_temperature = [{'time': 'N/A', 'temp': 0.0}] * 25

def update_data():
    threading.Timer(600.0, update_data).start()
    bath_temperature.pop(0)
    bath_temperature.append({'time': time.strftime('%H:%M'),
                             'temp': read_device_file()})

@app.route('/')
def index():
    return 'Hello World'

@app.route('/temp')
def file():
    return str(read_device_file())

@app.route('/temp_graph')
def graph():
    title = 'Bath Temperature'
    bar_chart = pygal.StackedLine(width=1200, height=600, explicit_size=True, title=title, x_label_rotation=20, style=NeonStyle, fill=True)
    bar_chart.x_labels = [data['time'] for data in bath_temperature]
    bar_chart.add('Temperature', [float(data['temp']) for data in bath_temperature])
    html = """
        <html>
            <head>
                <title>%s</title>
            </head>
            <body>
                Current Temperature is %s<br>
                %s
            </body>
        </html>
        """ % (title, str(read_device_file()), bar_chart.render())
    return html


@app.route('/turn_off/<outlet_id>')
def turn_off_web(outlet_id):
    turn_off(outlet_id)

@app.route('/turn_on/<outlet_id>')
def turn_on_web(outlet_id):
    turn_on(outlet_id)

if __name__ == '__main__':
    update_data()
    app.run(debug=True, host='0.0.0.0')
