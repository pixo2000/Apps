from flask import Flask, render_template, request, jsonify, send_from_directory, url_for, session, redirect
from werkzeug.utils import secure_filename
import os
import json
import time
from pathlib import Path
from threading import Thread

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'videos'
app.config['MAX_CONTENT_LENGTH'] = 5000 * 1024 * 1024  # 5GB max file size
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mkv', 'mov', 'webm', 'flv', 'wmv'}
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'  # Change this!

# Password for admin page (change this!)
ADMIN_PASSWORD = 'admin123'

PLAYLIST_FILE = 'playlist.json'

# Create videos folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def cleanup_pending_deletes():
    """Background task to delete files that were locked"""
    while True:
        time.sleep(10)  # Check every 10 seconds
        
        if not os.path.exists('pending_delete.txt'):
            continue
        
        try:
            with open('pending_delete.txt', 'r') as f:
                pending_files = [line.strip() for line in f.readlines() if line.strip()]
            
            if not pending_files:
                os.remove('pending_delete.txt')
                continue
            
            successfully_deleted = []
            
            for filename in pending_files:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if not os.path.exists(filepath):
                    # Already deleted
                    successfully_deleted.append(filename)
                    continue
                
                try:
                    os.remove(filepath)
                    print(f"Successfully deleted pending file: {filepath}")
                    successfully_deleted.append(filename)
                except PermissionError:
                    # Still locked, try again later
                    pass
                except Exception as e:
                    print(f"Error deleting pending file {filepath}: {e}")
                    successfully_deleted.append(filename)  # Remove from pending anyway
            
            # Update pending list
            remaining_files = [f for f in pending_files if f not in successfully_deleted]
            
            if remaining_files:
                with open('pending_delete.txt', 'w') as f:
                    f.write('\n'.join(remaining_files) + '\n')
            else:
                if os.path.exists('pending_delete.txt'):
                    os.remove('pending_delete.txt')
        
        except Exception as e:
            print(f"Error in cleanup task: {e}")

# Start cleanup thread
cleanup_thread = Thread(target=cleanup_pending_deletes, daemon=True)
cleanup_thread.start()

def allowed_file(filename):
    has_extension = '.' in filename
    if not has_extension:
        print(f"File rejected - no extension: {filename}")
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    is_allowed = extension in app.config['ALLOWED_EXTENSIONS']
    
    if not is_allowed:
        print(f"File rejected - invalid extension '{extension}': {filename}")
        print(f"Allowed extensions: {app.config['ALLOWED_EXTENSIONS']}")
    else:
        print(f"File accepted - extension '{extension}': {filename}")
    
    return is_allowed

def load_playlist():
    """Load playlist from JSON file"""
    if os.path.exists(PLAYLIST_FILE):
        with open(PLAYLIST_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_playlist(playlist):
    """Save playlist to JSON file"""
    with open(PLAYLIST_FILE, 'w', encoding='utf-8') as f:
        json.dump(playlist, f, indent=2)

@app.route('/')
def index():
    """Management interface - requires password"""
    if not session.get('authenticated'):
        return redirect('/login')
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['authenticated'] = True
            return redirect('/')
        else:
            return render_template('login.html', error='Invalid password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.pop('authenticated', None)
    return redirect('/login')

@app.route('/player')
def player():
    """Video player page for Raspberry Pi"""
    return render_template('player.html')

@app.route('/api/playlist', methods=['GET'])
def get_playlist():
    """Get current playlist"""
    playlist = load_playlist()
    # Add full URLs for video playback and check if files exist
    valid_playlist = []
    for item in playlist:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], item['filename'])
        if os.path.exists(filepath):
            item['url'] = url_for('serve_video', filename=item['filename'], _external=True)
            valid_playlist.append(item)
    
    # Update playlist if some videos were removed
    if len(valid_playlist) != len(playlist):
        save_playlist(valid_playlist)
    
    return jsonify(valid_playlist)

@app.route('/api/playlist', methods=['POST'])
def update_playlist():
    """Update playlist order"""
    playlist = request.json
    save_playlist(playlist)
    return jsonify({'success': True})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload a video file"""
    if 'file' not in request.files:
        print("ERROR: No file in request")
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        print("ERROR: Empty filename")
        return jsonify({'error': 'No file selected'}), 400
    
    print(f"Upload request for file: {file.filename}")
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Make filename unique if it already exists
        base_name = filename.rsplit('.', 1)[0]
        extension = filename.rsplit('.', 1)[1]
        counter = 1
        original_filename = filename
        while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
            filename = f"{base_name}_{counter}.{extension}"
            counter += 1
        
        if filename != original_filename:
            print(f"File renamed to avoid conflict: {original_filename} -> {filename}")
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        print(f"File saved to: {filepath}")
        
        # Add to playlist
        playlist = load_playlist()
        print(f"Current playlist has {len(playlist)} videos")
        playlist.append({
            'filename': filename,
            'title': base_name
        })
        save_playlist(playlist)
        print(f"Added to playlist. New playlist size: {len(playlist)}")
        
        return jsonify({'success': True, 'filename': filename})
    
    print(f"ERROR: File type not allowed for {file.filename}")
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Delete a video file"""
    filename = secure_filename(filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    # Find the index of the deleted video
    playlist = load_playlist()
    deleted_index = None
    for i, item in enumerate(playlist):
        if item['filename'] == filename:
            deleted_index = i
            break
    
    # Remove from playlist first
    playlist = [item for item in playlist if item['filename'] != filename]
    save_playlist(playlist)
    
    # Signal player to skip immediately (before trying to delete file)
    if deleted_index is not None:
        with open('skip_flag.txt', 'w') as f:
            f.write('1')
    
    # Try to delete the file, but don't fail if it's locked
    try:
        os.remove(filepath)
        print(f"Successfully deleted file: {filepath}")
        return jsonify({'success': True, 'deleted_index': deleted_index, 'file_deleted': True})
    except PermissionError as e:
        # File is being used (probably by the video player)
        # Mark it for deletion and let it be deleted later
        print(f"File is locked, marking for deletion: {filepath}")
        with open('pending_delete.txt', 'a') as f:
            f.write(f"{filename}\n")
        return jsonify({
            'success': True, 
            'deleted_index': deleted_index, 
            'file_deleted': False,
            'message': 'Video removed from playlist. File will be deleted when playback finishes.'
        })
    except Exception as e:
        print(f"Error deleting file {filepath}: {e}")
        # Still return success since we removed it from playlist
        return jsonify({
            'success': True,
            'deleted_index': deleted_index,
            'file_deleted': False,
            'message': 'Video removed from playlist but file could not be deleted.'
        })

@app.route('/api/rename/<filename>', methods=['POST'])
def rename_video(filename):
    """Rename a video's title in the playlist"""
    filename = secure_filename(filename)
    data = request.json
    new_title = data.get('title', '')
    
    playlist = load_playlist()
    for item in playlist:
        if item['filename'] == filename:
            item['title'] = new_title
            save_playlist(playlist)
            return jsonify({'success': True})
    
    return jsonify({'error': 'Video not found'}), 404

@app.route('/videos/<filename>')
def serve_video(filename):
    """Serve video files"""
    filename = secure_filename(filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        print(f"ERROR: Video file not found: {filepath}")
        return jsonify({'error': 'Video file not found'}), 404
    
    print(f"Serving video: {filepath}")
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/restart', methods=['POST'])
def restart_playback():
    """Signal to restart playback (client will poll for this)"""
    # We'll use a simple file-based flag
    with open('restart_flag.txt', 'w') as f:
        f.write('1')
    return jsonify({'success': True})

@app.route('/api/play/<int:index>', methods=['POST'])
def play_video_at_index(index):
    """Signal to play a specific video by index"""
    with open('play_index.txt', 'w') as f:
        f.write(str(index))
    return jsonify({'success': True})

@app.route('/api/volume/<int:level>', methods=['POST'])
def set_volume(level):
    """Signal to set volume level (0-100)"""
    level = max(0, min(100, level))  # Clamp between 0 and 100
    with open('volume_level.txt', 'w') as f:
        f.write(str(level))
    return jsonify({'success': True, 'volume': level})

@app.route('/api/playpause', methods=['POST'])
def toggle_play_pause():
    """Signal to toggle play/pause state"""
    with open('playpause_flag.txt', 'w') as f:
        f.write('1')
    return jsonify({'success': True})

@app.route('/api/check_playpause', methods=['GET'])
def check_play_pause():
    """Check if play/pause should be toggled"""
    if os.path.exists('playpause_flag.txt'):
        os.remove('playpause_flag.txt')
        return jsonify({'toggle': True})
    return jsonify({'toggle': False})

@app.route('/api/check_volume', methods=['GET'])
def check_volume():
    """Check if volume should be changed"""
    if os.path.exists('volume_level.txt'):
        with open('volume_level.txt', 'r') as f:
            level = int(f.read().strip())
        os.remove('volume_level.txt')
        return jsonify({'change': True, 'level': level})
    return jsonify({'change': False})

@app.route('/api/check_play_index', methods=['GET'])
def check_play_index():
    """Check if a specific video should be played"""
    if os.path.exists('play_index.txt'):
        with open('play_index.txt', 'r') as f:
            index = int(f.read().strip())
        os.remove('play_index.txt')
        return jsonify({'play': True, 'index': index})
    return jsonify({'play': False})

@app.route('/api/check_skip', methods=['GET'])
def check_skip():
    """Check if current video should be skipped (e.g., after deletion)"""
    if os.path.exists('skip_flag.txt'):
        os.remove('skip_flag.txt')
        return jsonify({'skip': True})
    return jsonify({'skip': False})

@app.route('/api/check_restart', methods=['GET'])
def check_restart():
    """Check if playback should restart"""
    if os.path.exists('restart_flag.txt'):
        os.remove('restart_flag.txt')
        return jsonify({'restart': True})
    return jsonify({'restart': False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
