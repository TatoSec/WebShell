from flask import Flask, request, render_template, jsonify
import subprocess
import threading
import time

app = Flask(__name__)

# Flag to track if a connection has been established
connection_established = False

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

# Start the Netcat listener in a separate thread
listener_thread = threading.Thread(target=start_netcat_listener)
listener_thread.start()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute():
    global connection_established
    if request.method == 'POST':
        command = request.form['command']
        try:
            if command == "nc -lvnp 4444":
                if not connection_established:
                    subprocess.Popen(["nc", "-lvnp", "4444"])
                    time.sleep(1)  # Give time for the listener to start
                    connection_established = True
                else:
                    return jsonify({'output': 'Listener is already running.'})
            else:
                result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                if connection_established:
                    response = "[+] Connection Established\n" + result.decode()
                else:
                    response = result.decode()
                return jsonify({'output': response})
        except subprocess.CalledProcessError as e:
            return jsonify({'output': str(e.output)})

if __name__ == '__main__':
    app.run(debug=True)
