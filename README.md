##Yt2mp3

###About  
yt2mp3 is a wrapper for youtube-dl and ffmpeg that allows users to download and convert youtube videos to
mp3's with ease. The program consists of a shell script witch prompts the user for needed input and executes 
the commands needed to achieve proper video download and mp3 conversion.

###Features
- Downloads Youtube file in HD
- Conversion of the Youtube download to .mp3
- Tag adding such as Artist and Title
- Embedding of album art from Youtube video or custom .jpg

###Usage
```
Download and convert from Youtube:
    yt2mp3 https://youtube.com/example

Optional:
    -r   Remove temp file located in /tmp/yt2mp3
    -h   Help page for yt2mp3
    -u   Update current yt2mp3 program
    -t [00:00]   Change time in minutes that thumbnail is extracted from video

In Program
Adding Tags
    /back  use to redo the previously entered tags
```

###Installing
Installing yt2mp3 is very easy, simply run `./install.sh` within the cloned folder.  
After installing, yt2mp3 can be accessed anywhere from the terminal, installation files
are no longer needed unless you want to run yt2mp3 as a stand alone program.

#####Mac OS X Installation Dependencies
- Homebrew _(needed to install other dependencies)_
- eyeD3  _(installed from pip)_
- python2.7
- youtube-dl
- ffmpeg  
- pip

#####Linux Installation Dependencies
- eyeD3  _(installed from pip)_ 
- python3.4  _(if not installed)_
- youtube-dl
- ffmpeg
- pip3

###About alb_add.py
`alb_add.py` is a python script that works with the eyeD3 module to add either the video or custom album art
to the mp3 file.  
`alb_add` can be ran as a stand alone program to add album art to preexisting .mp3 files.  

##Bugs
- Program incapable of downloading songs from Youtube playlists

