from flask import Flask
from temp_reader import read_device_file

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World'

@app.route('/temp')
def file():
    return str(read_device_file()[1])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
