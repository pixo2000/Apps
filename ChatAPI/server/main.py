from flask import Flask, request, jsonify
from datetime import datetime
import threading
import time

app = Flask(__name__)

# Store messages with timestamp and username
messages = []

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
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=80, debug=True)
    # If port 80 doesn't work (might need admin privileges), try:
    # app.run(host='0.0.0.0', port=5000, debug=True)
    # For HTTPS (port 443), you'd need SSL certificates and use:
    # app.run(host='0.0.0.0', port=443, ssl_context=('cert.pem', 'key.pem'), debug=True)
