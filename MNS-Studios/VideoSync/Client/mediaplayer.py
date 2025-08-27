import os
import cv2
from ffpyplayer.player import MediaPlayer

# Set the folder to use at the top
MEDIA_FOLDER = os.path.abspath(r"C:/Users/Paul.Schoeneck.INFORMATIK/Downloads/SyncClient")  # CHANGE THIS
PLAYLIST_FILE = os.path.join(MEDIA_FOLDER, "playlist.txt")
VIDEOS_FOLDER = os.path.join(MEDIA_FOLDER, "Videos")

# Read playlist
with open(PLAYLIST_FILE, "r", encoding="utf-8") as f:
    playlist = [line.strip() for line in f if line.strip()]

def play_video_with_audio(video_path, window_created):
    cap = cv2.VideoCapture(video_path)
    player = MediaPlayer(video_path)
    if not cap.isOpened():
        print(f"[ERROR] Could not open video: {video_path}")
        return
    if not window_created[0]:
        cv2.namedWindow("Media Player", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Media Player", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        window_created[0] = True
    delay = int(1000 / 28.5)  # 30 fps
    while True:
        grabbed, frame = cap.read()
        audio_frame, val = player.get_frame()
        if not grabbed:
            break
        if val != 'eof' and audio_frame is not None:
            img, t = audio_frame
        cv2.imshow("Media Player", frame)
        key = cv2.waitKey(delay)
        if key == 27:  # ESC
            cap.release()
            player.close_player()
            cv2.destroyAllWindows()
            os._exit(0)
    cap.release()
    player.close_player()
    # Do not destroy window here

def find_video_file(playlist_entry, folder_files):
    entry_norm = playlist_entry.strip().lower()
    for f in folder_files:
        if f.strip().lower() == entry_norm:
            return f
    return None

if __name__ == "__main__":
    print("[MEDIA FOLDER] Files in media folder:")
    for f in os.listdir(MEDIA_FOLDER):
        print(f"  {f}")
    print("[TXT FILES] Contents of all .txt files in media folder:")
    for fname in os.listdir(MEDIA_FOLDER):
        if fname.lower().endswith('.txt'):
            print(f"-- {fname} --")
            with open(os.path.join(MEDIA_FOLDER, fname), "r", encoding="utf-8") as txtf:
                for line in txtf:
                    print(f"  {line.rstrip()}")
    print("[PLAYLIST] Videos to play (in order):")
    for idx, video in enumerate(playlist, 1):
        print(f"  {idx}. '{video}'")
    print("[FOLDER] Files in Videos folder:")
    folder_files = os.listdir(VIDEOS_FOLDER)
    for f in folder_files:
        print(f"  {f}")
    window_created = [False]
    while True:
        for video in playlist:
            matched_file = find_video_file(video, folder_files)
            if not matched_file:
                print(f"[ERROR] No matching file for playlist entry: '{video}'")
                continue
            video_path = os.path.join(VIDEOS_FOLDER, matched_file)
            print(f"[DEBUG] Playing: {video_path}")
            print(f"[PLAYING] Now playing: {matched_file}")
            play_video_with_audio(video_path, window_created)
        # Repeat playlist
