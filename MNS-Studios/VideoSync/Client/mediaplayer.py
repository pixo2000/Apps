# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 Multimedia player example"""

import sys
import os
import threading
import socket
from PySide6.QtCore import QStandardPaths, Qt, Slot, QEvent, QUrl, Signal
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import (QApplication, QDialog, QFileDialog,
                               QMainWindow, QSlider, QStyle, QToolBar)
from PySide6.QtMultimedia import (QAudioOutput, QMediaFormat,
                                  QMediaPlayer, QAudio)
from PySide6.QtMultimediaWidgets import QVideoWidget


AVI = "video/x-msvideo"  # AVI


MP4 = 'video/mp4'


def get_supported_mime_types():
    result = []
    for f in QMediaFormat().supportedFileFormats(QMediaFormat.Decode):
        mime_type = QMediaFormat(f).mimeType()
        result.append(mime_type.name())
    return result


# === USER CONFIGURABLE PATH ===
# Set the path to the directory containing playlist.txt and the video folder
MEDIA_BASE_PATH = r"C:\Users\Paul.Schoeneck.INFORMATIK\Downloads\SyncClient"  # <-- CHANGE THIS
PLAYLIST_FILE = os.path.join(MEDIA_BASE_PATH, "playlist.txt")
VIDEO_FOLDER = os.path.join(MEDIA_BASE_PATH, "videos")  # Folder with .mp4 files

HOST = '127.0.0.1' # use ur client ip
LOCAL_CONTROL_PORT = 64138  # Port for local control commands


class MainWindow(QMainWindow):
    reload_playlist_signal = Signal()
    set_volume_signal = Signal(int)

    def __init__(self):
        super().__init__()

        self._playlist = []
        self._playlist_index = -1
        self._audio_output = QAudioOutput()
        self._player = QMediaPlayer()
        self._player.setAudioOutput(self._audio_output)

        self._player.errorOccurred.connect(self._player_error)

        tool_bar = QToolBar()
        self.addToolBar(tool_bar)

        file_menu = self.menuBar().addMenu("&File")
        icon = QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen)
        open_action = QAction(icon, "&Open...", self,
                              shortcut=QKeySequence.Open, triggered=self.open)
        file_menu.addAction(open_action)
        tool_bar.addAction(open_action)
        icon = QIcon.fromTheme(QIcon.ThemeIcon.ApplicationExit)
        exit_action = QAction(icon, "E&xit", self,
                              shortcut="Ctrl+Q", triggered=self.close)
        file_menu.addAction(exit_action)

        play_menu = self.menuBar().addMenu("&Play")
        style = self.style()
        icon = QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackStart,
                               style.standardIcon(QStyle.SP_MediaPlay))
        self._play_action = tool_bar.addAction(icon, "Play")
        self._play_action.triggered.connect(self._player.play)
        play_menu.addAction(self._play_action)

        icon = QIcon.fromTheme(QIcon.ThemeIcon.MediaSkipBackward,
                               style.standardIcon(QStyle.SP_MediaSkipBackward))
        self._previous_action = tool_bar.addAction(icon, "Previous")
        self._previous_action.triggered.connect(self.previous_clicked)
        play_menu.addAction(self._previous_action)

        icon = QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackPause,
                               style.standardIcon(QStyle.SP_MediaPause))
        self._pause_action = tool_bar.addAction(icon, "Pause")
        self._pause_action.triggered.connect(self._player.pause)
        play_menu.addAction(self._pause_action)

        icon = QIcon.fromTheme(QIcon.ThemeIcon.MediaSkipForward,
                               style.standardIcon(QStyle.SP_MediaSkipForward))
        self._next_action = tool_bar.addAction(icon, "Next")
        self._next_action.triggered.connect(self.next_clicked)
        play_menu.addAction(self._next_action)

        icon = QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackStop,
                               style.standardIcon(QStyle.SP_MediaStop))
        self._stop_action = tool_bar.addAction(icon, "Stop")
        self._stop_action.triggered.connect(self._ensure_stopped)
        play_menu.addAction(self._stop_action)

        # Fullscreen action
        icon = QIcon.fromTheme(QIcon.ThemeIcon.ViewFullscreen, style.standardIcon(QStyle.SP_TitleBarMaxButton))
        self._fullscreen_action = tool_bar.addAction(icon, "Fullscreen")
        self._fullscreen_action.setCheckable(True)
        self._fullscreen_action.setShortcut(Qt.Key_F11)
        self._fullscreen_action.triggered.connect(self.toggle_fullscreen)
        play_menu.addAction(self._fullscreen_action)

        self._volume_slider = QSlider()
        self._volume_slider.setOrientation(Qt.Orientation.Horizontal)
        self._volume_slider.setMinimum(0)
        self._volume_slider.setMaximum(100)
        available_width = self.screen().availableGeometry().width()
        self._volume_slider.setFixedWidth(available_width / 10)
        self._volume_slider.setValue(self._audio_output.volume() * 100)
        self._volume_slider.setTickInterval(10)
        self._volume_slider.setTickPosition(QSlider.TicksBelow)
        self._volume_slider.setToolTip("Volume")
        self._volume_slider.valueChanged.connect(self.setVolume)
        tool_bar.addWidget(self._volume_slider)

        icon = QIcon.fromTheme(QIcon.ThemeIcon.HelpAbout)
        about_menu = self.menuBar().addMenu("&About")
        about_qt_act = QAction(icon, "About &Qt", self, triggered=QApplication.instance().aboutQt)
        about_menu.addAction(about_qt_act)

        self._video_widget = QVideoWidget()
        self.setCentralWidget(self._video_widget)
        self._player.playbackStateChanged.connect(self.update_buttons)
        self._player.setVideoOutput(self._video_widget)

        self._video_widget.installEventFilter(self)
        self._is_fullscreen = False

        self.update_buttons(self._player.playbackState())
        self._mime_types = []

        self.load_playlist_from_file()
        if self._playlist:
            self._playlist_index = 0
            self.play_current_video()

        self._player.mediaStatusChanged.connect(self.handle_media_status)
        # Automatically start in fullscreen
        self.toggle_fullscreen()

        self.reload_playlist_signal.connect(self.reload_and_restart)
        self.set_volume_signal.connect(self.set_volume_from_command)
        threading.Thread(target=self.control_server_thread, daemon=True).start()

    def toggle_fullscreen(self):
        if not self._is_fullscreen:
            self._video_widget.setFullScreen(True)
            self._is_fullscreen = True
            self._fullscreen_action.setChecked(True)
            self._video_widget.setFocus()  # Ensure key events go to video widget
        else:
            self._video_widget.setFullScreen(False)
            self._is_fullscreen = False
            self._fullscreen_action.setChecked(False)
            self.setFocus()  # Return focus to main window

    def eventFilter(self, obj, event):
        if self._is_fullscreen:
            # Accept Escape from anywhere
            if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
                self.toggle_fullscreen()
                return True
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        if self._is_fullscreen and event.key() == Qt.Key_Escape:
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        self._ensure_stopped()
        event.accept()

    def load_playlist_from_file(self):
        self._playlist = []
        print(f"[Playlist Loader] Listing all files in: {VIDEO_FOLDER}")
        if os.path.exists(VIDEO_FOLDER):
            for f in os.listdir(VIDEO_FOLDER):
                print(f"  Found: {f}")
        else:
            print(f"  [ERROR] Video folder does not exist: {VIDEO_FOLDER}")
        print(f"[Playlist Loader] Reading playlist from: {PLAYLIST_FILE}")
        if os.path.exists(PLAYLIST_FILE):
            with open(PLAYLIST_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    video_name = line.strip()
                    if video_name:
                        video_path = os.path.join(VIDEO_FOLDER, video_name)
                        if os.path.exists(video_path):
                            video_url = QUrl.fromLocalFile(video_path)
                            self._playlist.append(video_url)
                            print(f"  Added to playlist: {video_path}")
                        else:
                            print(f"  [WARNING] Listed in playlist.txt but not found: {video_path}")
        else:
            print(f"  [ERROR] Playlist file does not exist: {PLAYLIST_FILE}")
        print(f"[Playlist Loader] Final playlist order:")
        for idx, url in enumerate(self._playlist):
            print(f"  {idx+1}. {os.path.basename(url.toLocalFile())}")

    def play_current_video(self):
        if self._playlist:
            video_url = self._playlist[self._playlist_index]
            print(f"[Player] Now playing: {video_url.toLocalFile()}")
            self._player.setSource(video_url)
            self._player.play()

    def handle_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            if self._playlist:
                self._playlist_index += 1
                if self._playlist_index >= len(self._playlist):
                    self._playlist_index = 0  # Loop to start
                self.play_current_video()

    @Slot()
    def open(self):
        # Overridden: disables manual open, as playlist is loaded from file
        self.show_status_message("Playlist is loaded from file. To change videos, edit playlist.txt.")

    @Slot()
    def _ensure_stopped(self):
        if self._player.playbackState() != QMediaPlayer.StoppedState:
            self._player.stop()

    @Slot()
    def previous_clicked(self):
        if self._playlist:
            self._playlist_index = (self._playlist_index - 1) % len(self._playlist)
            self.play_current_video()

    @Slot()
    def next_clicked(self):
        if self._playlist:
            self._playlist_index = (self._playlist_index + 1) % len(self._playlist)
            self.play_current_video()

    @Slot("QMediaPlayer::PlaybackState")
    def update_buttons(self, state):
        media_count = len(self._playlist)
        self._play_action.setEnabled(media_count > 0 and state != QMediaPlayer.PlayingState)
        self._pause_action.setEnabled(state == QMediaPlayer.PlayingState)
        self._stop_action.setEnabled(state != QMediaPlayer.StoppedState)
        self._previous_action.setEnabled(self._player.position() > 0)
        self._next_action.setEnabled(media_count > 1)

    def show_status_message(self, message):
        self.statusBar().showMessage(message, 5000)

    @Slot("QMediaPlayer::Error", str)
    def _player_error(self, error, error_string):
        print(error_string, file=sys.stderr)
        self.show_status_message(error_string)

    @Slot()
    def setVolume(self):
        self.volumeValue = QAudio.convertVolume(self._volume_slider.value() / 100.0,
                                                QAudio.VolumeScale.LogarithmicVolumeScale,
                                                QAudio.VolumeScale.LinearVolumeScale)
        self._audio_output.setVolume(self.volumeValue)

    def control_server_thread(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, LOCAL_CONTROL_PORT))
            s.listen(1)
            while True:
                conn, _ = s.accept()
                with conn:
                    data = conn.recv(1024).decode().strip()
                    if data == 'RELOAD':
                        self.reload_playlist_signal.emit()
                        conn.sendall(b'OK')
                    elif data.startswith('SETVOLUME:'):
                        try:
                            vol = int(data.split(':')[1])
                            self.set_volume_signal.emit(vol)
                            conn.sendall(b'OK')
                        except Exception:
                            conn.sendall(b'ERR')
                    else:
                        conn.sendall(b'ERR')

    def reload_and_restart(self):
        self.load_playlist_from_file()
        if self._playlist:
            self._playlist_index = 0
            self.play_current_video()
        self.show_status_message('Playlist reloaded and restarted.')

    def set_volume_from_command(self, vol):
        vol = max(0, min(100, vol))
        self._volume_slider.setValue(vol)
        self.setVolume()
        self.show_status_message(f'Volume set to {vol}% (remote)')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    available_geometry = main_win.screen().availableGeometry()
    main_win.resize(available_geometry.width() / 3,
                    available_geometry.height() / 2)
    main_win.show()
    sys.exit(app.exec())