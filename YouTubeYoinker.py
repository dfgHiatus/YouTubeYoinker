from threading import Thread
from multiprocessing import Queue
from pytube import Playlist
import subprocess
import os
import time

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