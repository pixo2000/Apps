# WebSocket Chat Application

A real-time chat application built with Python using WebSockets for efficient communication between clients and server.

## Features

- Real-time bidirectional communication using WebSockets
- Multiple client implementations:
  - GUI client using Tkinter
  - Basic terminal client
  - Enhanced terminal client with improved UI
- User identification with customizable usernames
- Message history retrieval
- System that automatically cleans old messages
- Legacy REST API support for backwards compatibility

## Components

The project consists of the following components:

- **Server**: WebSocket server built with Flask-SocketIO
- **WebSocket Client**: Shared client library for WebSocket connections
- **GUI Client**: Graphical chat interface using Tkinter
- **Terminal Clients**: Command-line interfaces for systems without GUI support

## Requirements

- Python 3.7+
- Required packages:
  - Flask
  - Flask-SocketIO
  - python-socketio
  - (GUI client only) Tkinter (usually comes with Python)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/chatapi.git
   cd chatapi
   ```

2. Install the required dependencies:
   ```bash
   pip install flask flask-socketio python-socketio
   ```

## Usage

### Starting the Server

1. Navigate to the server directory:
   ```bash
   cd server
   ```

2. Run the server:
   ```bash
   python main.py
   ```

   The server will start on port 5500 by default.

### Using the GUI Client

1. Navigate to the client directory:
   ```bash
   cd client
   ```

2. Start the GUI client:
   ```bash
   python gui.py
   ```

3. In the GUI:
   - Enter the server URL and port
   - Click "Connect"
   - Set your username
   - Start chatting!

### Using the Terminal Clients

#### Basic Terminal Client

```bash
cd client
python terminal_client.py -s http://server_address -p 5500 -u YourUsername
```

#### Enhanced Terminal Client

```bash
cd client
python enhanced_terminal_client.py -s http://server_address -p 5500 -u YourUsername
```

### Command Line Arguments

Both terminal clients support the following command-line arguments:

- `-s` or `--server`: Server URL (default: http://localhost)
- `-p` or `--port`: Server port (default: 5500)
- `-u` or `--username`: Your username (default: Anonymous)

### Terminal Client Commands

While using the terminal clients, you can use these commands:

- `/username <new_name>`: Change your username
- `/clear`: Clear the message screen (enhanced client only)
- `/quit`: Exit the application

## Technical Details

### WebSocket Implementation

This application uses WebSockets instead of traditional REST API polling for better performance:

- **Lower Latency**: Messages are delivered instantly
- **Less Overhead**: No HTTP headers for each message
- **Reduced Server Load**: No constant polling from clients
- **True Bidirectional Communication**: Server can push messages to clients

### Architecture

```
/ChatAPI
├── server/
│   └── main.py             # WebSocket server with Flask-SocketIO
├── client/
│   ├── socketclient.py     # Shared WebSocket client library
│   ├── gui.py              # Tkinter GUI client
│   ├── terminal_client.py  # Basic terminal client
│   └── enhanced_terminal_client.py  # Advanced terminal client
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
