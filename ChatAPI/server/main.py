from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from datetime import datetime
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store messages with timestamp and username
messages = []

# Legacy REST API endpoints for compatibility
@app.route('/api/send', methods=['POST'])
def send_message():
    data = request.json
    if not data or 'message' not in data or 'username' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400
    
    new_message = {
        'username': data['username'],
        'message': data['message'],
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }
    messages.append(new_message)
    socketio.emit('new_message', new_message)
    return jsonify({'status': 'success'}), 200

@app.route('/api/messages', methods=['GET'])
def get_messages():
    since = request.args.get('since', 0, type=int)
    return jsonify({
        'messages': messages[since:],
        'total': len(messages)
    })

@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'online'})

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connection_response', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(data):
    if not data or 'message' not in data or 'username' not in data:
        emit('error', {'message': 'Invalid message format'})
        return
    
    new_message = {
        'username': data['username'],
        'message': data['message'],
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }
    messages.append(new_message)
    # Broadcast the message to all connected clients
    emit('new_message', new_message, broadcast=True)

@socketio.on('get_messages')
def handle_get_messages(data):
    since = data.get('since', 0)
    emit('message_history', {
        'messages': messages[since:],
        'total': len(messages)
    })

# Clean old messages periodically
def clean_old_messages():
    global messages
    while True:
        time.sleep(3600)  # Clean every hour
        if len(messages) > 1000:
            messages = messages[-1000:]  # Keep only the latest 1000 messages

if __name__ == '__main__':
    # Start the cleanup thread
    cleanup_thread = threading.Thread(target=clean_old_messages)
    cleanup_thread.daemon = True
    cleanup_thread.start()
    
    # Run the Flask app with SocketIO
    socketio.run(app, host='0.0.0.0', port=5500, debug=True)
    # If port 80 doesn't work (might need admin privileges), try:
    # socketio.run(app, host='0.0.0.0', port=5000, debug=True)
