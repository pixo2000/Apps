import socket
import os
import threading
import json
import time
import logging
from flask import Flask, request, render_template_string, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

# Set the folder to sync at the top
SYNC_FOLDER = os.path.abspath(r"C:/Users/Paul.Schoeneck.INFORMATIK/Downloads/SyncServer")  # CHANGE THIS
HOST = '0.0.0.0'
PORT = 5001
BUFFER_SIZE = 4096
WEB_PORT = 64137

logging.basicConfig(level=logging.DEBUG, format='[SERVER] %(asctime)s %(message)s')

# Helper to get all files (relative paths) in the sync folder
def get_all_files():
    file_list = []
    for root, dirs, files in os.walk(SYNC_FOLDER):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, SYNC_FOLDER)
            file_list.append(rel_path.replace('\\', '/'))
    logging.debug(f"Current server file list: {file_list}")
    return file_list

def handle_client(conn, addr):
    logging.info(f"Connected by {addr}")
    try:
        while True:
            data = conn.recv(BUFFER_SIZE).decode().strip()
            if not data:
                logging.debug(f"No data received from {addr}, closing connection.")
                break
            logging.debug(f"Received command from {addr}: {data}")
            if data == 'LIST':
                files = get_all_files()
                response = json.dumps(files).encode()
                conn.sendall(response)
                logging.debug(f"Sent file list to {addr} ({len(response)} bytes)")
            elif data.startswith('GET:'):
                rel_path = data[4:]
                abs_path = os.path.join(SYNC_FOLDER, rel_path)
                if os.path.isfile(abs_path):
                    file_size = os.path.getsize(abs_path)
                    conn.sendall(b'EXISTS')
                    conn.sendall(f"{file_size:016d}".encode())  # 16-byte file size header
                    logging.debug(f"Sending file to {addr}: {rel_path} ({file_size} bytes)")
                    total_bytes = 0
                    with open(abs_path, 'rb') as f:
                        while True:
                            bytes_read = f.read(BUFFER_SIZE)
                            if not bytes_read:
                                break
                            conn.sendall(bytes_read)
                            total_bytes += len(bytes_read)
                    logging.info(f"Sent file to {addr}: {rel_path} ({total_bytes} bytes)")
                else:
                    conn.sendall(b'NOFILE')
                    logging.warning(f"File not found for {addr}: {rel_path}")
            else:
                conn.sendall(b'INVALID')
                logging.warning(f"Invalid command from {addr}: {data}")
    except Exception as e:
        logging.error(f"Error with {addr}: {e}")
    finally:
        conn.close()
        logging.info(f"Connection closed for {addr}")

# Flask web interface
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = SYNC_FOLDER

HTML = '''
<!DOCTYPE html>
<html>
<head>
<title>Sync Folder Control</title>
<style>
body { font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 0; }
.container { max-width: 600px; margin: 40px auto; background: #fff; padding: 30px; border-radius: 10px; box-shadow: 0 2px 8px #0001; }
h2 { color: #333; }
#drop-area {
  border: 2px dashed #0078d7;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  color: #0078d7;
  background: #f9f9f9;
  margin-bottom: 20px;
  transition: background 0.2s;
}
#drop-area.dragover { background: #e3f1ff; }
#file-list { margin: 10px 0; }
button { background: #0078d7; color: #fff; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 1em; }
button:disabled { background: #aaa; }
ul { list-style: none; padding: 0; }
li { margin: 8px 0; }
a { color: #d70022; text-decoration: none; margin-left: 10px; }
a:hover { text-decoration: underline; }
</style>
</head>
<body>
<div class="container">
<h2>Sync Folder Control</h2>
<p>Folder: {{ folder }}</p>
<div id="drop-area">
  <p>Drag & Drop files here to upload</p>
  <div id="file-list"></div>
  <button id="upload-btn" disabled>Upload</button>
</div>
<h3>Files</h3>
<ul>
{% for file in files %}
  <li>{{ file }} <a href="/delete/{{ file }}">Delete</a></li>
{% endfor %}
</ul>
</div>
<script>
let dropArea = document.getElementById('drop-area');
let uploadBtn = document.getElementById('upload-btn');
let fileListDiv = document.getElementById('file-list');
let filesToUpload = [];

dropArea.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropArea.classList.add('dragover');
});
dropArea.addEventListener('dragleave', (e) => {
  e.preventDefault();
  dropArea.classList.remove('dragover');
});
dropArea.addEventListener('drop', (e) => {
  e.preventDefault();
  dropArea.classList.remove('dragover');
  filesToUpload = Array.from(e.dataTransfer.files);
  showFileList();
});

function showFileList() {
  fileListDiv.innerHTML = '';
  if (filesToUpload.length > 0) {
    filesToUpload.forEach(f => {
      let p = document.createElement('p');
      p.textContent = f.name + ' (' + Math.round(f.size/1024) + ' KB)';
      fileListDiv.appendChild(p);
    });
    uploadBtn.disabled = false;
  } else {
    uploadBtn.disabled = true;
  }
}

uploadBtn.addEventListener('click', () => {
  if (filesToUpload.length === 0) return;
  let confirmUpload = confirm('Upload ' + filesToUpload.length + ' file(s)?');
  if (!confirmUpload) return;
  let formData = new FormData();
  filesToUpload.forEach(f => formData.append('file', f));
  fetch('/upload', { method: 'POST', body: formData })
    .then(res => { if (res.redirected) window.location = res.url; else window.location.reload(); });
});
</script>
</body>
</html>
'''

@app.route("/")
def index():
    files = get_all_files()
    return render_template_string(HTML, folder=SYNC_FOLDER, files=files)

@app.route("/upload", methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('index'))

@app.route("/delete/<path:filename>")
def delete(filename):
    abs_path = os.path.join(SYNC_FOLDER, filename)
    if os.path.isfile(abs_path):
        os.remove(abs_path)
    return redirect(url_for('index'))

@app.route('/files/<path:filename>')
def download(filename):
    return send_from_directory(SYNC_FOLDER, filename)

def run_web():
    app.run(host=HOST, port=WEB_PORT, debug=False, use_reloader=False)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(5)
        logging.info(f"Listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
