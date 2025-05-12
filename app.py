# Simple telnet client
import telnetlib
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

class TelnetClient:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None

    def connect(self):
        """Connect to the specified host and port using Telnet."""
        self.connection = telnetlib.Telnet(self.host, self.port)
        self.connection.read_until(b"login: ")
        self.connection.write(self.username.encode('ascii') + b"\n")
        self.connection.read_until(b"Password: ")
        self.connection.write(self.password.encode('ascii') + b"\n")

        # Wait a moment for the MOTD to be fully sent
        time.sleep(1)  # Adjust sleep as necessary for your environment
        return self.connection.read_very_eager().decode('ascii')  # Read any immediate response

    def execute_command(self, command):
        """Execute a command on the remote server."""
        self.connection.write(command.encode('ascii') + b"\n")
        
        # Adjust the read command to wait for the prompt after the command execution
        time.sleep(1)  # Wait for a moment to let the command execute
        return self.connection.read_very_eager().decode('ascii')  # Read the response

    def close(self):
        """Close the Telnet connection."""
        if self.connection:
            self.connection.close()

@app.route('/')
def home():
    return "Hello!"

@app.route('/execute', methods=['POST'])
def execute():
    """API endpoint to execute a command on the remote server."""
    data = request.json
    host = data.get('host')
    port = data.get('port')
    username = data.get('username')
    password = data.get('password')
    command = data.get('command')

    try:
        client = TelnetClient(host, port, username, password)
        client.connect()
        output = client.execute_command(command)
        client.close()
        return jsonify({'output': output}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8910) 
