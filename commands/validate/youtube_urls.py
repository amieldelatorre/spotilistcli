import json
import os
import sys
from urllib.parse import urlparse

import click
from typing import List, Dict, Iterator
from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, \
    QLineEdit, QDialogButtonBox, QDialog
from PySide6.QtGui import QScreen, QFont, QPalette
from PySide6.QtCore import QUrl, QMargins
from PySide6.QtWebEngineWidgets import QWebEngineView

from helpers import get_obj_dict
from sptfy import PlaylistWithSongs, Song, PlaylistNoSongs


class OverwriteYoutubeUrlErrorDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invalid Youtube URL")
        palette = QPalette("#000")
        self.setPalette(palette)

        button = (QDialogButtonBox.Ok)
        self.button_box = QDialogButtonBox(button)
        self.button_box.accepted.connect(self.accept)
        layout = QVBoxLayout()
        message = QLabel("Youtube URL for overwrite cannot be empty and must be a valid Youtube Music URL!\nExample: https://music.youtube.com/watch?v='videoId'")
        message.setStyleSheet(
            """
            color: #FF474C;
            font-weight: bold;
            font-size: 18px;
            """
        )
        layout.addWidget(message)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def accept(self):
        self.deleteLater()


class MainWindow(QMainWindow):
    def __init__(self, original_playlists: List[PlaylistWithSongs], songs_to_validate_iterator: Iterator[Song], output_filename: str):
        super().__init__()
        self.setWindowTitle("Validate Youtube URLs")
        self.original_playlists = original_playlists
        self.songs_to_validate_iterator = songs_to_validate_iterator
        self.output_filename = output_filename

        self.spotify_page = QWebEngineView()
        self.spotify_page.show()
        self.youtube_page = QWebEngineView()
        self.youtube_page.show()
        self.is_valid_button = QPushButton("Is Valid")
        self.is_valid_button.clicked.connect(self.is_valid_button_clicked)
        self.skip_button = QPushButton("Skip")
        self.skip_button.clicked.connect(self.skip_button_clicked)

        self.main_layout = QVBoxLayout()
        buttons_layout = QHBoxLayout()
        browsers_layout = QHBoxLayout()
        self.main_layout.addLayout(browsers_layout)
        self.main_layout.addLayout(buttons_layout)

        buttons_layout.setContentsMargins(QMargins(100,70,100,70))
        buttons_layout.addWidget(self.skip_button)

        overwrite_entry_layout = QVBoxLayout()
        self.overwrite_entry_input = QLineEdit(placeholderText="Overwrite the Youtube URL with this value")
        self.overwrite_entry_input.setFixedSize(400, 40)
        self.overwrite_entry_button = QPushButton("Overwrite")
        self.overwrite_entry_button.clicked.connect(self.overwrite_youtube_url)
        self.overwrite_entry_button.setFixedSize(100, 40)
        overwrite_entry_layout.addWidget(self.overwrite_entry_input)
        overwrite_entry_layout.addWidget(self.overwrite_entry_button, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        buttons_layout.addLayout(overwrite_entry_layout)

        buttons_layout.addWidget(self.is_valid_button)
        browsers_layout.addWidget(self.spotify_page)
        browsers_layout.addWidget(self.youtube_page)

        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

        screen_size = QScreen.availableGeometry(QApplication.primaryScreen())
        width = int(screen_size.width() - screen_size.width() * 0.1)
        height = int(screen_size.height() - screen_size.height() * 0.1)
        self.setGeometry(0, 0, width, height)


        self.is_valid_button.setFixedSize(100, 40)
        self.is_valid_button.setStyleSheet("background-color: #5CE65C;"
                                           "font-size: 18px;")

        self.skip_button.setFixedSize(100, 40)
        self.skip_button.setStyleSheet("font-size: 18px;")

        self.current_song_spotify_url = None
        self.current_song_youtube_url = None
        self.next_song() # Call this here to get the first value from the iterator

    def is_valid_button_clicked(self):
        self.original_playlists = update_validated_song(self.original_playlists, self.current_song_spotify_url, self.output_filename)
        self.next_song()

    def skip_button_clicked(self):
        self.next_song()

    def next_song(self):
        try:
            self.is_valid_button.setEnabled(True)

            song_to_validate = next(self.songs_to_validate_iterator)
            if (song_to_validate.youtube_url is None or song_to_validate.youtube_url.strip() == "" or
                    not is_valid_youtube_music_url(song_to_validate.youtube_url.strip())):
                self.is_valid_button.setDisabled(True)
                self.youtube_page.setHtml(f"""
                <h1 style="background-color: #000; color: #FF474C; height: 100%; text-align: center;">Invalid youtube URL '{song_to_validate.youtube_url}'</h1>
                """)
            else:
                yt_url = song_to_validate.youtube_url.strip()
                self.current_song_youtube_url = yt_url
                self.youtube_page.load(QUrl(yt_url))

            self.current_song_spotify_url = song_to_validate.spotify_url
            self.spotify_page.load(QUrl(song_to_validate.spotify_url))
        except StopIteration:
            self.clear_window(self.main_layout)
            self.add_end_screen()


    def clear_window(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.clear_window(item.layout())

    def add_end_screen(self):
        end_label = QLabel()
        end_label.setText("Done! No more Youtube URLs to validate.")
        end_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(50)
        end_label.setFont(font)
        end_label.setStyleSheet("background-color: #5CE65C;")

        self.main_layout.addWidget(end_label)

    def overwrite_youtube_url(self):
        youtube_url = self.overwrite_entry_input.text()
        if youtube_url is None or youtube_url.strip() == "" or not is_valid_youtube_music_url(youtube_url.strip()):
            dialog = OverwriteYoutubeUrlErrorDialog()
            dialog.exec()
            return

        youtube_url = youtube_url.strip()
        self.original_playlists = overwrite_youtube_url(self.original_playlists, self.current_song_spotify_url, youtube_url)
        self.original_playlists = update_validated_song(self.original_playlists, self.current_song_spotify_url, self.output_filename)
        self.overwrite_entry_input.clear()
        self.next_song()



@click.command(help="Validate the Youtube URLs generated by the playlist download command and make sure it is the "
                    "same song as the one from spotify")
@click.option("--input-filename", required=True, default=None, type=click.Path(exists=True, readable=True,
              file_okay=True, dir_okay=False),
              help="The filename of with the Youtube URLs to be validated")
@click.option("--output-filename", required=False, default=None, type=click.Path(),
              help="The filename where the results will be stored. This can be the same as the original file, "
                   "but make sure to keep a copy of your original file in case of errors. If an output filename is not "
                   "specified, there is a chance that the input file will be overwritten if it already follows the "
                   "format of `validated_youtube_urls_<input-filename>`.")
def youtube_urls(input_filename: str, output_filename: str):
    if output_filename is None:
        prefix = "validated_youtube_urls_"
        if os.path.basename(input_filename).startswith(prefix):
            output_filename = input_filename
        else:
            output_filename = f"{prefix}{os.path.basename(input_filename)}"
    elif output_filename.strip() == "":
        print(f"ERROR: Output filename cannot be blank or null!")
        sys.exit(1)
    elif not output_filename.strip().endswith('.json'):
        print(f"ERROR: Output filename must end with '.json'")
        sys.exit(1)

    original_playlists = load_playlists_file(input_filename)
    songs_to_validate = get_songs_to_validate(original_playlists)
    iterator = get_songs_to_validate_iterator(songs_to_validate)

    app = QApplication()
    window = MainWindow(original_playlists, iterator, output_filename)
    window.show()
    app.exec()


def load_playlists_file(filename: str) -> List[PlaylistWithSongs]:
    with open(filename, "r") as f:
        data = json.load(f)

    playlists = []
    for item in data:
        playlist_id = item["id"]
        playlist_name = item["name"]
        playlist_total = item["total"]
        spotify_playlist_url = item["spotify_playlist_url"]
        playlist_owner_id = item["owner_spotify_id"]
        songs = []

        for item_song in item["songs"]:
            song_name = item_song["name"]
            song_artists = item_song["artists"]
            song_spotify_url = item_song["spotify_url"]
            song_youtube_url = item_song["youtube_url"]
            song_youtube_url_validated = item_song["youtube_url_validated"]

            songs.append(Song(
                name=song_name,
                artists=song_artists,
                spotify_url=song_spotify_url,
                youtube_url=song_youtube_url,
                youtube_url_validated=song_youtube_url_validated,
            ))

        playlists.append(PlaylistWithSongs(PlaylistNoSongs(
            id=playlist_id,
            name=playlist_name,
            total=playlist_total,
            spotify_playlist_url=spotify_playlist_url,
            owner_spotify_id=playlist_owner_id
        ), songs))

    return playlists


def get_songs_to_validate(playlists: List[PlaylistWithSongs]) -> Dict[str, Song]:
    songs_to_validate = {}

    for playlist in playlists:
        for song in playlist.songs:
            if song.spotify_url is None or song.spotify_url.strip() == "":
                continue
            if not song.youtube_url_validated and song.spotify_url not in songs_to_validate.keys():
                songs_to_validate[song.spotify_url] = song

    return songs_to_validate


def get_songs_to_validate_iterator(songs: Dict[str, Song]):
    for song in songs.values():
        yield song


def update_validated_song(original_playlists: List[PlaylistWithSongs], spotify_url: str, filename: str) -> List[PlaylistWithSongs]:
    for playlist in original_playlists:
        for song in playlist.songs:
            if song.spotify_url == spotify_url and (song.youtube_url is not None and song.youtube_url.strip() != ""):
                song.youtube_url_validated = True

    with open(filename, "w") as file:
        file.write(json.dumps(original_playlists, indent=4, default=get_obj_dict))

    return original_playlists


def overwrite_youtube_url(original_playlists: List[PlaylistWithSongs], spotify_url: str, youtube_url: str) -> List[PlaylistWithSongs]:
    for playlist in original_playlists:
        for song in playlist.songs:
            if song.spotify_url == spotify_url:
                song.youtube_url = youtube_url
    return original_playlists


def is_valid_youtube_music_url(url: str) -> bool:
    try:
        if not url.startswith("http://music.youtube.com/watch?v=") and not url.startswith("https://music.youtube.com/watch?v="):
            return False
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
