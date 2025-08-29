# --- Flask-based Web Video Player ---
import os
import threading
import socket
from flask import Flask, send_from_directory, jsonify, request, render_template_string

# === USER CONFIGURABLE PATH ===
MEDIA_BASE_PATH = r"C:\Users\pixo2000\Downloads\SyncClient"  # <-- CHANGE THIS
PLAYLIST_FILE = os.path.join(MEDIA_BASE_PATH, "playlist.txt")
VIDEO_FOLDER = os.path.join(MEDIA_BASE_PATH, "videos")
HOST = '127.0.0.1'
LOCAL_CONTROL_PORT = 64138
WEB_PORT = 64140  # Port for the web UI

app = Flask(__name__)

# --- State ---
state = {
		'playlist': [],
		'playlist_index': 0,
		'volume': 100,
}

def load_playlist():
		playlist = []
		if os.path.exists(PLAYLIST_FILE):
				with open(PLAYLIST_FILE, 'r', encoding='utf-8') as f:
						for line in f:
								video_name = line.strip()
								if video_name:
										video_path = os.path.join(VIDEO_FOLDER, video_name)
										if os.path.exists(video_path):
												playlist.append(video_name)
		return playlist

def reload_playlist():
		state['playlist'] = load_playlist()
		state['playlist_index'] = 0

reload_playlist()

# --- Flask Endpoints ---
@app.route('/')
def index():
		return render_template_string(WEB_PLAYER_HTML)

@app.route('/playlist')
def get_playlist():
		return jsonify({
				'playlist': state['playlist'],
				'current': state['playlist_index'],
				'volume': state['volume']
		})

@app.route('/video/<int:index>')
def get_video(index):
		if 0 <= index < len(state['playlist']):
				filename = state['playlist'][index]
				return send_from_directory(VIDEO_FOLDER, filename)
		return '', 404

@app.route('/control', methods=['POST'])
def control():
		data = request.json
		action = data.get('action')
		if action == 'play':
				# No-op, handled client-side
				pass
		elif action == 'pause':
				pass
		elif action == 'next':
				if state['playlist']:
						state['playlist_index'] = (state['playlist_index'] + 1) % len(state['playlist'])
		elif action == 'prev':
				if state['playlist']:
						state['playlist_index'] = (state['playlist_index'] - 1) % len(state['playlist'])
		elif action == 'set_volume':
				vol = int(data.get('volume', 100))
				state['volume'] = max(0, min(100, vol))
		elif action == 'set_index':
				idx = int(data.get('index', 0))
				if 0 <= idx < len(state['playlist']):
						state['playlist_index'] = idx
		return jsonify({'status': 'ok', 'state': state})

# --- Socket server for remote commands (RELOAD, SETVOLUME) ---
def control_server_thread():
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
				s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				s.bind((HOST, LOCAL_CONTROL_PORT))
				s.listen(1)
				while True:
						conn, _ = s.accept()
						with conn:
								data = conn.recv(1024).decode().strip()
								if data == 'RELOAD':
										reload_playlist()
										conn.sendall(b'OK')
								elif data.startswith('SETVOLUME:'):
										try:
												vol = int(data.split(':')[1])
												state['volume'] = max(0, min(100, vol))
												conn.sendall(b'OK')
										except Exception:
												conn.sendall(b'ERR')
								else:
										conn.sendall(b'ERR')

# --- Web UI HTML ---
WEB_PLAYER_HTML = '''
<!DOCTYPE html>
<html><head><title>VideoSync Web Player</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body { background: #181c24; color: #e6e6e6; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; }
.container { max-width: 900px; margin: 40px auto; background: #232837; padding: 30px; border-radius: 16px; box-shadow: 0 2px 16px #0008; }
h2 { color: #1e90ff; }
#player-controls { display: flex; align-items: center; gap: 16px; margin-bottom: 18px; }
#playlist { margin-top: 24px; }
.playlist-item { background: #23283a; margin: 7px 0; padding: 10px 12px; border-radius: 7px; cursor: pointer; display: flex; align-items: center; gap: 10px; transition: background 0.18s; }
.playlist-item.active { background: #1e90ff44; color: #fff; }
.playlist-item:hover { background: #26304a; }
#video { width: 100%; max-width: 100%; border-radius: 12px; background: #000; }
#volume { width: 120px; }
button { background: #1e90ff; color: #fff; border: none; border-radius: 6px; padding: 8px 16px; font-size: 1em; cursor: pointer; transition: background 0.18s, transform 0.12s; }
button:hover { background: #0078d7; transform: scale(1.05); }
#pw-modal { position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(24,28,36,0.98); z-index:10000; display:flex; align-items:center; justify-content:center; }
#pw-box { background:#232837; padding:40px 30px; border-radius:14px; box-shadow:0 2px 16px #0008; min-width:320px; display:flex; flex-direction:column; align-items:center; }
#pw-box input[type=password] { width:200px; padding:12px; border-radius:6px; border:1.5px solid #2a2f3d; background:#181c24; color:#e6e6e6; font-size:1.1em; margin-bottom:18px; box-sizing:border-box; }
#pw-box button { width:100%; }
#pw-err { color:#d70022; margin-bottom:10px; }
</style>
</head><body>
<div id="pw-modal" style="display:none;">
	<div id="pw-box">
		<h2>Enter Password</h2>
		<div id="pw-err"></div>
		<input type="password" id="pw-input" placeholder="Password" autofocus>
		<button onclick="checkPassword()">Unlock</button>
	</div>
</div>
<div class="container" id="main-content" style="display:none;">
<h2>VideoSync Web Player</h2>
<div id="player-controls">
	<button onclick="prev()">⏮️</button>
	<button onclick="playPause()" id="playpause">▶️</button>
	<button onclick="next()">⏭️</button>
	<input type="range" id="volume" min="0" max="100" value="100" onchange="setVolume(this.value)">
	<span id="volval">100</span>%
	<button onclick="fullscreen()">⛶</button>
</div>
<video id="video" autoplay style="max-height:60vh;"></video>
<div id="playlist"></div>
</div>
<script>
// --- Password protection ---
const PASSWORD = "videosync"; // Change this to your desired password
function syncVolumeFromServer() {
	fetch('/playlist').then(r=>r.json()).then(data => {
		volume = data.volume;
		volslider.value = volume;
		volval.textContent = volume;
		video.volume = volume/100;
	});
}
function showMain() {
	document.getElementById('pw-modal').style.display = 'none';
	document.getElementById('main-content').style.display = '';
	syncVolumeFromServer();
}
function showPwModal() {
	document.getElementById('pw-modal').style.display = 'flex';
	document.getElementById('main-content').style.display = 'none';
	document.getElementById('pw-input').focus();
}
function checkPassword() {
	const val = document.getElementById('pw-input').value;
	if(val === PASSWORD) {
		sessionStorage.setItem('vsync_pw', '1');
		showMain();
	} else {
		document.getElementById('pw-err').textContent = 'Wrong password!';
	}
}
window.addEventListener('DOMContentLoaded', () => {
	if(sessionStorage.getItem('vsync_pw') === '1') showMain();
	else showPwModal();
	document.getElementById('pw-input').addEventListener('keydown', function(e){
		if(e.key === 'Enter') checkPassword();
	});
});
let playlist = [];
let current = 0;
let volume = 100;
const video = document.getElementById('video');
const playpause = document.getElementById('playpause');
const volslider = document.getElementById('volume');
const volval = document.getElementById('volval');

function fetchPlaylist(updateOnly=false) {
	fetch('/playlist').then(r=>r.json()).then(data => {
		playlist = data.playlist;
		current = data.current;
		// Always update volume from server
		volume = data.volume;
		volslider.value = volume;
		volval.textContent = volume;
		video.volume = volume/100;
		renderPlaylist();
		if (!updateOnly) loadVideo();
	});
}
// Poll every second for remote volume changes
setInterval(()=>fetchPlaylist(true), 1000);

function renderPlaylist() {
	let html = '';
	playlist.forEach((v, idx) => {
		html += `<div class='playlist-item${idx===current?' active':''}' onclick='setIndex(${idx})'>${v}</div>`;
	});
	document.getElementById('playlist').innerHTML = html;
}


let firstVideoLoaded = false;
function loadVideo() {
	if (playlist.length > 0) {
		// On first video load, always sync volume with server
		if (!firstVideoLoaded) {
			fetch('/playlist').then(r=>r.json()).then(data => {
				volume = data.volume;
				volslider.value = volume;
				volval.textContent = volume;
				video.volume = volume/100;
				firstVideoLoaded = true;
				video.src = `/video/${current}`;
				video.play();
			});
		} else {
			video.src = `/video/${current}`;
			video.volume = volume/100;
			video.play();
		}
	} else {
		video.src = '';
	}
}

function playPause() {
	if (video.paused) { video.play(); playpause.textContent = '⏸️'; sendControl('play'); }
	else { video.pause(); playpause.textContent = '▶️'; sendControl('pause'); }
}

function next() {
	sendControl('next');
	setTimeout(fetchPlaylist, 200);
}
function prev() {
	sendControl('prev');
	setTimeout(fetchPlaylist, 200);
}
function setVolume(val) {
	volume = parseInt(val);
	video.volume = volume/100;
	volval.textContent = volume;
	sendControl('set_volume', {volume: volume});
}
function setIndex(idx) {
	sendControl('set_index', {index: idx});
	setTimeout(fetchPlaylist, 200);
}
function fullscreen() {
	if (video.requestFullscreen) video.requestFullscreen();
	else if (video.webkitRequestFullscreen) video.webkitRequestFullscreen();
	else if (video.msRequestFullscreen) video.msRequestFullscreen();
}
function sendControl(action, extra={}) {
	fetch('/control', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(Object.assign({action}, extra))});
}
video.onended = function() { next(); };
video.onplay = function() { playpause.textContent = '⏸️'; };
video.onpause = function() { playpause.textContent = '▶️'; };
fetchPlaylist();
// Poll every second for remote volume changes
setInterval(()=>fetchPlaylist(true), 1000);
</script>
</body></html>
'''

if __name__ == '__main__':
		threading.Thread(target=control_server_thread, daemon=True).start()
		print(f"[WebPlayer] Serving on http://{HOST}:{WEB_PORT}")
		app.run(host=HOST, port=WEB_PORT, debug=False)
