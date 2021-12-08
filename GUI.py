from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from threading import Thread
from multiprocessing import Queue
from pytube import Playlist
import subprocess
import os
import time

global UIdir
global UIPlaylists
global UISongs
global UInumThreads
global songQueue

class GUI(App):
    def build(self):
        self.window = GridLayout()
        self.window.cols = 1
        self.window.size_hint = (0.6, 0.7)
        self.window.pos_hint = {"center_x": 0.5, "center_y": 0.5 }

        # Title
        self.greeting = Label(text = "Youtube Yoinker 1.0.0")
        self.window.add_widget(self.greeting)

        # Dir Instructions
        self.greeting = Label(text = "Please specify the directory you would like to save your music:")
        self.window.add_widget(self.greeting)

        self.user = TextInput(multiline = False,
                              padding_y = (20, 20),
                              size_hint = (1, 0.3))
        self.window.add_widget(self.user)

        self.button = Button(text="Confirm Directory",
                             padding_y = (20, 20),
                             size_hint = (1, 0.3),
                             bold = False)
        self.button.bind(on_press = self.populateDirectory)
        self.window.add_widget(self.button)

        # Song Instructions
        self.greeting = Label(text = "Import Song List: ")
        self.window.add_widget(self.greeting)

        self.button = Button(text="Songs",
                             padding_y = (20, 20),
                             size_hint = (1, 0.3),
                             bold = False)
        self.button.bind(on_press = self.populateSongs)
        self.window.add_widget(self.button)

        # Playlist Instructions
        self.greeting = Label(text = "Import Playlist List: ")
        self.window.add_widget(self.greeting)

        self.button = Button(text="Playlist",
                             padding_y = (20, 20),
                             size_hint = (1, 0.3),
                             bold = False)
        self.button.bind(on_press = self.populatePlaylists)
        self.window.add_widget(self.button)

        # Download!
        self.button = Button(text="Download!",
                             padding_y = (20, 20),
                             size_hint = (1, 0.3),
                             bold = True)
        self.button.bind(on_press = self.dummyCallback)
        self.window.add_widget(self.button)

        return self.window

    def dummyCallback(self, instance):
        print("Clicked!")

    def populateSongs(self, instance):

    def downloadCallback(self, instance):
        ### Read Single Songs
        with open("songURLs.txt", "r") as songFile:
            songURLs = songFile.read().split('\n')

        songQueue = Queue()
        for song in songURLs:
            songQueue.put(song)

        ### Read Playlist Songs
        with open("playlistURLs.txt", "r") as playlistFile:
            playlistURLs = playlistFile.read().split('\n')

        for playlist in playlistURLs:
            p = Playlist(playlist)
            for url in p.video_urls:
                songQueue.put(url)
       
        # Where to store our downloaded songs
        with open("dir.txt", "r") as dirFile:
            os.chdir(dirFile.read())

        maxThreads = 4
        threadList = []

        # Mutlithread downloadSong
        for n in range(maxThreads):
            t = Thread(target=downloadSong)
            t.start()
            threadList.append(t)
            # Don't get rate limited
            time.sleep(1.0)

        for t in threadList:
            t.join()

    def downloadSong():
        while (not songQueue.empty()):
            # This will overwrite existing song(s) in dir!
            # subprocess.check_call prevents a command injection vulnerability, vs os.system
            try:
                # Formerly subprocess.check_call('cmd /c youtube-dl -i --extract-audio --audio-format opus --audio-quality 0 ' + songQueue.get()) 
                subprocess.check_call('cmd /c youtube-dl --download-archive downloaded.txt --no-post-overwrites -ciwx '
                                      '--audio-format opus --audio-quality 0 -o "%(title)s.%(ext)s" ' + songQueue.get())
            except Exception:
                continue

if __name__ == "__main__":
    GUI().run()

