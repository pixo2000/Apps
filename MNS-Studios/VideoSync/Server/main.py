import socket
import os
import threading
import json
import time
import logging
from flask import Flask, request, render_template_string, redirect, url_for, send_from_directory, session, make_response
from werkzeug.utils import secure_filename
import requests
from flask import jsonify
import json as pyjson
import pyotp
from functools import wraps

# Set the folder to sync at the top
SYNC_FOLDER = os.path.abspath(r"C:\Users\pixo2000\Downloads\SyncServer")  # CHANGE THIS
HOST = 'localhost'  # Change to '
PORT = 5001
BUFFER_SIZE = 4096
WEB_PORT = 64137

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_NAMES_FILE = os.path.join(BASE_DIR, 'client_names.json')
VIDEOS_FOLDER = os.path.join(SYNC_FOLDER, 'videos')
PLAYLIST_FILE = os.path.join(SYNC_FOLDER, 'playlist.txt')

logging.basicConfig(level=logging.DEBUG, format='[SERVER] %(asctime)s %(message)s')

# Helper to get all files (relative paths) in the sync folder
def get_all_files():
    file_list = []
    for root, dirs, files in os.walk(SYNC_FOLDER):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, SYNC_FOLDER)
            size = os.path.getsize(abs_path)
            file_list.append({'name': rel_path.replace('\\', '/'), 'size': size})
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

clients = {}
clients_lock = threading.Lock()
CLIENT_TIMEOUT = 60  # seconds

# --- Persistent client names ---

# Now stores { ip: name, ... }
def load_client_names():
  if os.path.exists(CLIENT_NAMES_FILE):
    with open(CLIENT_NAMES_FILE, 'r', encoding='utf-8') as f:
      data = pyjson.load(f)
      # Migrate new format if needed
      if data and isinstance(next(iter(data.values())), dict):
        # New format: {ip: {name:..., volume:...}}
        return {ip: v.get('name', ip) for ip, v in data.items()}
      return data
  return {}

def save_client_names(names):
  with open(CLIENT_NAMES_FILE, 'w', encoding='utf-8') as f:
    pyjson.dump(names, f)

client_names = load_client_names()


@app.route('/set_client_name', methods=['POST'])
def set_client_name():
  data = request.get_json(force=True)
  ip = data['ip']
  name = data['name']
  client_names[ip] = name
  save_client_names(client_names)
  with clients_lock:
    if ip in clients:
      clients[ip]['name'] = name
  return jsonify({'status': 'ok'})

# --- Video management ---
@app.route('/videos')
def list_videos():
    os.makedirs(VIDEOS_FOLDER, exist_ok=True)
    files = [f for f in os.listdir(VIDEOS_FOLDER) if os.path.isfile(os.path.join(VIDEOS_FOLDER, f))]
    return jsonify(files)

@app.route('/delete_video', methods=['POST'])
def delete_video():
    data = request.get_json(force=True)
    filename = data['filename']
    abs_path = os.path.join(VIDEOS_FOLDER, filename)
    if os.path.isfile(abs_path):
        os.remove(abs_path)
    # Remove all occurrences from playlist
    if os.path.exists(PLAYLIST_FILE):
        with open(PLAYLIST_FILE, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() != filename]
        with open(PLAYLIST_FILE, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(line + '\n')
    return jsonify({'status': 'ok'})

# --- Playlist management ---
@app.route('/playlist', methods=['GET', 'POST'])
def playlist():
    if request.method == 'GET':
        if os.path.exists(PLAYLIST_FILE):
            with open(PLAYLIST_FILE, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
            return jsonify(lines)
        else:
            return jsonify([])
    else:
        data = request.get_json(force=True)
        videos = data['videos']
        with open(PLAYLIST_FILE, 'w', encoding='utf-8') as f:
            for v in videos:
                f.write(v + '\n')
        return jsonify({'status': 'ok'})



@app.route('/register', methods=['POST'])
def register():
  data = request.get_json(force=True)
  ip = request.remote_addr
  # Use stored name if present, else client-supplied, else IP
  name = client_names.get(ip, data.get('name', ip))
  # Always start with 100 if new, else keep in-memory value
  with clients_lock:
    if ip not in clients:
      clients[ip] = {'name': name, 'ip': ip, 'last_seen': time.time(), 'volume': 100}
    else:
      clients[ip]['last_seen'] = time.time()
  return jsonify({'status': 'ok'})

@app.route('/unregister', methods=['POST'])
def unregister():
    ip = request.remote_addr
    with clients_lock:
        if ip in clients:
            del clients[ip]
    return jsonify({'status': 'ok'})

@app.route('/clients')
def get_clients():
    now = time.time()
    with clients_lock:
        # Remove stale clients
        to_remove = [ip for ip, c in clients.items() if now - c['last_seen'] > CLIENT_TIMEOUT]
        for ip in to_remove:
            del clients[ip]
        return jsonify(list(clients.values()))


@app.route('/set_volume', methods=['POST'])
def set_volume():
  data = request.get_json(force=True)
  ip = data['ip']
  volume = int(data['volume'])
  # Send volume command to client
  try:
    # Assume client exposes a local endpoint for volume (on same host as client)
    url = f'http://{ip}:64139/set_volume'
    requests.post(url, json={'volume': volume}, timeout=2)
    with clients_lock:
      if ip in clients:
        clients[ip]['volume'] = volume
    return jsonify({'status': 'ok'})
  except Exception as e:
    return jsonify({'status': 'error', 'error': str(e)}), 500

# --- Client media control routes ---
@app.route('/client_control/<client_ip>', methods=['POST'])
def client_control(client_ip):
    data = request.get_json(force=True)
    action = data.get('action')
    try:
        url = f'http://{client_ip}:64139/control'
        response = requests.post(url, json=data, timeout=2)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/client_playlist/<client_ip>')
def client_playlist(client_ip):
    try:
        url = f'http://{client_ip}:64139/playlist'
        response = requests.get(url, timeout=2)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/client_skip/<client_ip>', methods=['POST'])
def client_skip(client_ip):
    data = request.get_json(force=True)
    seconds = data.get('seconds', 10)
    try:
        url = f'http://{client_ip}:64139/skip'
        response = requests.post(url, json={'seconds': seconds}, timeout=2)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/client_playing_status/<client_ip>')
def client_playing_status(client_ip):
    try:
        url = f'http://{client_ip}:64139/playing_status'
        response = requests.get(url, timeout=2)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

HTML = '''
<!DOCTYPE html>
<html>
<head>
<title>VideoSync Control</title>
<style>
:root {
  --bg: #181c24;
  --panel: #232837;
  --accent: #0078d7;
  --accent2: #1e90ff;
  --text: #e6e6e6;
  --text-muted: #b0b0b0;
  --danger: #d70022;
  --item-bg: #23283a;
  --item-hover: #26304a;
  --border: #2a2f3d;
  --shadow: 0 2px 16px #0008;
}
body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; }
.container { max-width: 900px; margin: 40px auto; background: var(--panel); padding: 30px; border-radius: 16px; box-shadow: var(--shadow); }
h2 { color: var(--accent2); letter-spacing: 1px; }
.client-list { margin-bottom: 30px; }
.client-entry { margin-bottom: 14px; background: var(--item-bg); border-radius: 8px; padding: 12px 16px; display: flex; align-items: center; gap: 16px; box-shadow: 0 1px 4px #0003; transition: background 0.2s; }
.client-entry input[type=text] { background: var(--panel); color: var(--text); border: 1px solid var(--border); border-radius: 5px; padding: 4px 8px; transition: border 0.2s; }
.client-entry input[type=text]:focus { border: 1.5px solid var(--accent2); outline: none; }
.client-controls { margin-top: 10px; display: flex; gap: 8px; flex-wrap: wrap; }
.client-controls button { background: var(--accent); color: #fff; border: none; border-radius: 5px; padding: 6px 12px; font-size: 0.9em; cursor: pointer; transition: background 0.18s; }
.client-controls button:hover { background: var(--accent2); }
.client-playlist { margin-top: 10px; max-height: 150px; overflow-y: auto; background: var(--panel); border-radius: 5px; padding: 8px; }
.client-playlist-item { padding: 4px 8px; margin: 2px 0; background: var(--item-bg); border-radius: 3px; cursor: pointer; font-size: 0.9em; }
.client-playlist-item.active { background: var(--accent2); color: #fff; }
.client-playlist-item:hover { background: var(--item-hover); }
.playing-indicator { display: inline-block; width: 12px; height: 12px; background: #00ff00; border-radius: 50%; margin-right: 8px; animation: pulse 1.5s ease-in-out infinite alternate; }
.paused-indicator { display: inline-block; width: 12px; height: 12px; background: #ff6b6b; border-radius: 50%; margin-right: 8px; }
@keyframes pulse { from { opacity: 0.6; } to { opacity: 1; } }
input[type=range] { width: 120px; accent-color: var(--accent2); }
input[type=range]::-webkit-slider-thumb { background: var(--accent2); }
input[type=range]::-moz-range-thumb { background: var(--accent2); }
input[type=range]::-ms-thumb { background: var(--accent2); }
.flex-row { display: flex; gap: 40px; }
.flex-col { display: flex; flex-direction: column; gap: 10px; }
#videos, #playlist { min-width: 300px; min-height: 300px; border: 1.5px solid var(--border); border-radius: 12px; padding: 14px; background: var(--item-bg); box-shadow: 0 1px 8px #0002; transition: background 0.2s, border 0.2s; }
#videos { flex: 1; }
#playlist { flex: 1; }
.video-item, .playlist-item { background: var(--panel); margin: 7px 0; padding: 10px 12px; border-radius: 7px; cursor: grab; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 4px #0002; transition: background 0.18s, transform 0.15s; }
.video-item:hover, .playlist-item:hover { background: var(--item-hover); transform: scale(1.025); }
.video-item button, .playlist-item button { margin-left: 10px; background: var(--danger); color: #fff; border: none; border-radius: 5px; padding: 5px 14px; font-size: 1em; cursor: pointer; box-shadow: 0 1px 4px #0003; transition: background 0.18s, transform 0.12s; }
.video-item button:hover, .playlist-item button:hover { background: #a00018; transform: scale(1.08); }
#drop-overlay { position: fixed; top:0; left:0; right:0; bottom:0; background:rgba(30,144,255,0.12); z-index:1000; display:none; align-items:center; justify-content:center; font-size:2em; color:var(--accent2); font-weight:600; letter-spacing:2px; animation: fadein 0.2s; }
#upload-status { margin-top:10px; color:var(--accent2); font-weight:500; letter-spacing:1px; }
::-webkit-scrollbar { width: 10px; background: var(--panel); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 6px; }
@keyframes fadein { from { opacity: 0; } to { opacity: 1; } }
</style>
</head>
<body>
<div id="drop-overlay">Drop files to upload</div>
<div class="container" id="main-container">
<h2>VideoSync Control</h2><a href="/logout" style="float:right; color:#1e90ff; text-decoration:underline; font-size:1em; margin-top:-32px;">Logout</a>
<div class="client-list" id="clients"></div>
<div class="flex-row">
  <div>
    <h3 style="color:var(--accent2);">Videos</h3>
    <div id="videos" ondragover="event.preventDefault()"></div>
    <div id="upload-status"></div>
  </div>
  <div>
    <h3 style="color:var(--accent2);">Playlist</h3>
    <div id="playlist" ondragover="event.preventDefault()"></div>
  </div>
</div>
</div>
<script>
// --- Drag and Drop Upload ---
const dropOverlay = document.getElementById('drop-overlay');
const mainContainer = document.getElementById('main-container');
const uploadStatus = document.getElementById('upload-status');
['dragenter','dragover'].forEach(evt=>{
  document.body.addEventListener(evt, e=>{
    if(e.dataTransfer && e.dataTransfer.types.includes('Files')) {
      dropOverlay.style.display = 'flex';
      e.preventDefault();
    }
  });
});
['dragleave','drop'].forEach(evt=>{
  document.body.addEventListener(evt, e=>{
    dropOverlay.style.display = 'none';
  });
});
document.body.addEventListener('drop', function(e) {
  e.preventDefault();
  dropOverlay.style.display = 'none';
  let files = e.dataTransfer.files;
  if(files.length > 0) {
    let formData = new FormData();
    for(let i=0; i<files.length; ++i) formData.append('file', files[i]);
    uploadStatus.textContent = 'Uploading...';
    fetch('/upload_video', {method:'POST', body:formData}).then(()=>{
      uploadStatus.textContent = 'Upload complete!';
      setTimeout(()=>uploadStatus.textContent='', 2000);
      fetchVideos();
    });
  }
});
// --- Clients ---
function fetchClients() {
  // Store current playlist visibility states before refreshing
  const playlistStates = {};
  document.querySelectorAll('[id^="playlist-"]').forEach(div => {
    const ip = div.id.replace('playlist-', '');
    playlistStates[ip] = div.style.display !== 'none';
  });

  fetch('/clients').then(r => r.json()).then(clients => {
    let html = '';
    clients.forEach(c => {
      html += `
        <div class='client-entry'>
          <div style="flex: 1;">
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 10px;">
              <span class="playing-status" id="playing-${c.ip}">⏸️</span>
              <b>Name:</b> <input type='text' value='${c.name||''}' id='name-${c.ip}' oninput='saveName("${c.ip}", this.value)'>
              <b>IP:</b> ${c.ip}
              <b>Volume:</b> <input type='range' min='0' max='100' value='${c.volume}' onchange='setVolume("${c.ip}", this.value)'>
              <span id='volval-${c.ip}'>${c.volume}</span>
            </div>
            <div class="client-controls">
              <button onclick='clientControl("${c.ip}", "play")'>▶️ Play</button>
              <button onclick='clientControl("${c.ip}", "pause")'>⏸️ Pause</button>
              <button onclick='clientControl("${c.ip}", "next")'>⏭️ Next</button>
              <button onclick='clientControl("${c.ip}", "prev")'>⏮️ Prev</button>
              <button onclick='clientSkip("${c.ip}", 10)'>+10s</button>
              <button onclick='clientSkip("${c.ip}", 30)'>+30s</button>
              <button onclick='clientSkip("${c.ip}", 60)'>+1m</button>
              <button onclick='clientSkip("${c.ip}", -10)'>-10s</button>
              <button onclick='togglePlaylist("${c.ip}")'>📋 Playlist</button>
            </div>
            <div class="client-playlist" id="playlist-${c.ip}" style="display: none;"></div>
          </div>
        </div>`;
    });
    document.getElementById('clients').innerHTML = html;
    
    // Restore playlist visibility states and refresh visible playlists
    Object.keys(playlistStates).forEach(ip => {
      const playlistDiv = document.getElementById(`playlist-${ip}`);
      if (playlistDiv && playlistStates[ip]) {
        playlistDiv.style.display = 'block';
        fetchClientPlaylist(ip); // Refresh the content of visible playlists
      }
    });
    
    // Update playing status for all clients
    clients.forEach(c => {
      updateClientPlayingStatus(c.ip);
    });
  });
}

function updateClientPlayingStatus(ip) {
  fetch(`/client_playing_status/${ip}`)
    .then(r => r.json()).then(data => {
      const statusEl = document.getElementById(`playing-${ip}`);
      if (statusEl) {
        if (data.is_playing) {
          statusEl.innerHTML = '<span class="playing-indicator"></span>▶️ Playing';
          statusEl.style.color = '#00ff00';
        } else {
          statusEl.innerHTML = '<span class="paused-indicator"></span>⏸️ Paused';
          statusEl.style.color = '#ff6b6b';
        }
      }
    }).catch(() => {
      // If can't get status, show unknown
      const statusEl = document.getElementById(`playing-${ip}`);
      if (statusEl) {
        statusEl.innerHTML = '❓ Unknown';
        statusEl.style.color = '#888';
      }
    });
}
function setVolume(ip, vol) {
  fetch('/set_volume', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ip:ip, volume:vol})})
    .then(r => r.json()).then(res => {
      if(res.status==='ok') {
        const el = document.getElementById('volval-'+ip);
        if (el) el.innerText = vol;
      } else alert('Failed to set volume: '+res.error);
    });
}
function saveName(ip, name) {
  fetch('/set_client_name', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ip:ip, name:name})})
    .then(r => r.json()).then(res => {
      if(res.status!=='ok') alert('Failed to save name');
    });
}

// --- Client Controls ---
function clientControl(ip, action) {
  fetch(`/client_control/${ip}`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({action:action})})
    .then(r => r.json()).then(res => {
      if(res.status!=='ok') alert(`Failed to ${action}: ${res.error || 'Unknown error'}`);
    });
}

function clientSkip(ip, seconds) {
  fetch(`/client_skip/${ip}`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({seconds:seconds})})
    .then(r => r.json()).then(res => {
      if(res.status!=='ok') alert(`Failed to skip: ${res.error || 'Unknown error'}`);
    });
}

function togglePlaylist(ip) {
  const playlistDiv = document.getElementById(`playlist-${ip}`);
  if(playlistDiv.style.display === 'none') {
    fetchClientPlaylist(ip);
    playlistDiv.style.display = 'block';
  } else {
    playlistDiv.style.display = 'none';
  }
}

function fetchClientPlaylist(ip) {
  fetch(`/client_playlist/${ip}`)
    .then(r => r.json()).then(data => {
      if(data.status === 'error') {
        alert(`Failed to fetch playlist: ${data.error}`);
        return;
      }
      const playlistDiv = document.getElementById(`playlist-${ip}`);
      let html = '';
      data.playlist.forEach((video, idx) => {
        const isActive = idx === data.current;
        html += `<div class="client-playlist-item ${isActive ? 'active' : ''}" onclick="setClientVideo('${ip}', ${idx})">${video}</div>`;
      });
      if(html === '') html = '<div style="color: var(--text-muted); font-style: italic;">No videos in playlist</div>';
      playlistDiv.innerHTML = html;
    });
}

function setClientVideo(ip, index) {
  fetch(`/client_control/${ip}`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({action:'set_index', index:index})})
    .then(r => r.json()).then(res => {
      if(res.status==='ok') {
        // Refresh playlist after a short delay to show the new active video
        setTimeout(() => {
          const playlistDiv = document.getElementById(`playlist-${ip}`);
          if (playlistDiv && playlistDiv.style.display !== 'none') {
            fetchClientPlaylist(ip);
          }
        }, 500);
      } else {
        alert(`Failed to set video: ${res.error || 'Unknown error'}`);
      }
    });
}
setInterval(fetchClients, 3000);
fetchClients();
// --- Videos ---
function fetchVideos() {
  fetch('/videos').then(r => r.json()).then(videos => {
    let html = '';
    videos.forEach(v => {
      html += `<div class='video-item' draggable='true' ondragstart='dragVideo(event, "${v}")'>${v} <button onclick='deleteVideo("${v}")'>Delete</button></div>`;
    });
    document.getElementById('videos').innerHTML = html;
  });
}
function deleteVideo(filename) {
  if(!confirm('Delete video '+filename+'?')) return;
  fetch('/delete_video', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({filename:filename})})
    .then(r => r.json()).then(res => { fetchVideos(); fetchPlaylist(); });
}
function dragVideo(ev, filename) {
  ev.dataTransfer.setData('video', filename);
}
// --- Playlist ---
let playlistOrder = [];
function fetchPlaylist() {
  fetch('/playlist').then(r => r.json()).then(list => {
    playlistOrder = list;
    renderPlaylist();
  });
}
function renderPlaylist() {
  let html = '';
  playlistOrder.forEach((v, idx) => {
    html += `<div class='playlist-item' draggable='true' ondragstart='dragPlaylist(event, ${idx})'>${v} <button onclick='removeFromPlaylist(${idx})'>Remove</button></div>`;
  });
  document.getElementById('playlist').innerHTML = html;
}
function dragPlaylist(ev, idx) {
  ev.dataTransfer.setData('playlist', idx);
}
document.getElementById('playlist').ondrop = function(ev) {
  ev.preventDefault();
  let idx = ev.dataTransfer.getData('playlist');
  let video = ev.dataTransfer.getData('video');
  if(video) {
    playlistOrder.push(video);
    savePlaylist();
  } else if(idx !== '') {
    let from = parseInt(idx);
    let to = getDropIndex(ev, this);
    if(to !== from) {
      let item = playlistOrder.splice(from, 1)[0];
      playlistOrder.splice(to, 0, item);
      savePlaylist();
    }
  }
  renderPlaylist();
};
function getDropIndex(ev, container) {
  let y = ev.clientY;
  let items = Array.from(container.children);
  for(let i=0; i<items.length; ++i) {
    let rect = items[i].getBoundingClientRect();
    if(y < rect.top + rect.height/2) return i;
  }
  return items.length;
}
function removeFromPlaylist(idx) {
  playlistOrder.splice(idx, 1);
  savePlaylist();
  renderPlaylist();
}
function savePlaylist() {
  fetch('/playlist', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({videos:playlistOrder})});
}
document.getElementById('videos').ondrop = function(ev) {
  ev.preventDefault();
  // No-op: only allow drag to playlist
};
fetchVideos();
fetchPlaylist();
</script>
</body>
</html>
'''

app.secret_key = os.environ.get('VIDEOSYNC_SECRET_KEY', 'ThisIsAVerySecretKey')
app.permanent_session_lifetime = 3600  # 1 hour
TOTP_SECRET = os.environ.get('VIDEOSYNC_TOTP_SECRET', '4O5ZAPVGSCLFG7FL7EK7N5BRCI6KCOTY')  # Use your own secret!
TOTP_INTERVAL = 3600  # 1 hour instead of 5 minutes

def require_totp(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('totp_valid_until', 0) < time.time():
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        code = request.form.get('code', '')
        totp = pyotp.TOTP(TOTP_SECRET)
        if totp.verify(code):
            session.permanent = True  # Make session persistent
            session['totp_valid_until'] = int(time.time()) + TOTP_INTERVAL
            return redirect('/')
        else:
            return render_template_string(LOGIN_HTML, error='Invalid code')
    return render_template_string(LOGIN_HTML, error=None)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

LOGIN_HTML = '''
<!DOCTYPE html>
<html><head><title>Login</title>
<style>
body { background: #181c24; color: #e6e6e6; font-family: 'Segoe UI', Arial, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; }
.login-box { background: #232837; padding: 40px 30px; border-radius: 14px; box-shadow: 0 2px 16px #0008; min-width: 320px; }
h2 { color: #1e90ff; margin-bottom: 18px; }
input[type=text], input[type=password] { width: 100%; padding: 12px; border-radius: 6px; border: 1.5px solid #2a2f3d; background: #181c24; color: #e6e6e6; font-size: 1.1em; margin-bottom: 18px; box-sizing: border-box; }
input[name=code] { width: 100%; min-width: 0; }
button { width: 100%; background: #1e90ff; color: #fff; border: none; border-radius: 6px; padding: 12px; font-size: 1.1em; font-weight: 500; cursor: pointer; transition: background 0.18s, transform 0.12s; }
button:hover { background: #0078d7; transform: scale(1.03); }
.error { color: #d70022; margin-bottom: 10px; }
.logout-link { display:block; text-align:center; margin-top:18px; color:#1e90ff; text-decoration:underline; cursor:pointer; font-size:1em; }
.logout-link:hover { color:#0078d7; }
</style>
</head><body>
<div class="login-box">
<h2>Enter TOTP Code</h2>
{% if error %}<div class="error">{{ error }}</div>{% endif %}
<form method="post">
  <input type="text" name="code" placeholder="6-digit code" autocomplete="one-time-code" autofocus required>
  <button type="submit">Login</button>
</form>
<a class="logout-link" href="/logout">Logout</a>
</div>
</body></html>
'''

# --- Protect all main routes with TOTP ---
@app.route("/")
@require_totp
def index():
    files = get_all_files()
    return render_template_string(HTML, folder=SYNC_FOLDER, files=files)

@app.route("/delete/<path:filename>")
def delete(filename):
    abs_path = os.path.join(SYNC_FOLDER, filename)
    if os.path.isfile(abs_path):
        os.remove(abs_path)
    return redirect(url_for('index'))

@app.route('/files/<path:filename>')
def download(filename):
    return send_from_directory(SYNC_FOLDER, filename)

@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'error': 'No file part'}), 400
    files = request.files.getlist('file')
    os.makedirs(VIDEOS_FOLDER, exist_ok=True)
    saved = []
    for file in files:
        if file.filename == '':
            continue
        filename = secure_filename(file.filename)
        save_path = os.path.join(VIDEOS_FOLDER, filename)
        file.save(save_path)
        saved.append(filename)
    return jsonify({'status': 'ok', 'saved': saved})

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

# Protect all other relevant routes:
app.view_functions['index'] = require_totp(app.view_functions['index'])
app.view_functions['list_videos'] = require_totp(app.view_functions['list_videos'])
app.view_functions['playlist'] = require_totp(app.view_functions['playlist'])
app.view_functions['delete_video'] = require_totp(app.view_functions['delete_video'])
app.view_functions['set_client_name'] = require_totp(app.view_functions['set_client_name'])
app.view_functions['set_volume'] = require_totp(app.view_functions['set_volume'])
app.view_functions['get_clients'] = require_totp(app.view_functions['get_clients'])
app.view_functions['client_control'] = require_totp(app.view_functions['client_control'])
app.view_functions['client_playlist'] = require_totp(app.view_functions['client_playlist'])
app.view_functions['client_skip'] = require_totp(app.view_functions['client_skip'])
app.view_functions['client_playing_status'] = require_totp(app.view_functions['client_playing_status'])
