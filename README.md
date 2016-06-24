##Yt2mp3

###About  
yt2mp3 is a wrapper for youtube-dl and ffmpeg that allows users to download and convert youtube videos to
mp3's with ease. The program consists of a python script witch prompts the user for needed input and executes 
the commands needed to achieve proper video download and mp3 conversion.

###Features
- Downloads Youtube file in HD
- Conversion of the Youtube download to .mp3
- Tag adding such as Artist and Title
- Embedding of album art from Youtube video or custom .jpg

###Usage
```
    $ yt2mp3 [YOUTUBE URL] [OPTIONS]
   
    Options:
    [-u]                 run update for yt2mp3 and youtube-dl
    [-v]                 run yt2mp3 in verbose mode (display all output)
    [-t] [00:00:00.000]  set time to get album art from
    [-r]                 remove all temp files
    [-k]                 keep all temp files
    [-h]                 print help screen
    [-d] [PATH]          set a custom download path

    In App Commands:
    [\exit]              exit program at any input
    [\back]              use to redo tags
```

###Installing
Instling yt2mp3 is very easy, simply run `./install.sh` within the cloned git folder.  
After installing, yt2mp3 can be accessed anywhere from the terminal, installation files
are no longer needed unless you want to run yt2mp3 as a stand alone program.

#####Mac OS X Installation Dependencies
- Homebrew _(needed to install other dependencies)_
- eyeD3  _(installed with pip)_
- python3
- python2.7
- youtube-dl
- ffmpeg  
- pip

#####Linux Installation Dependencies
- eyeD3  _(installed from pip)_ 
- python3.4  _(if not installed)_
- python2.7 
- youtube-dl
- ffmpeg
- pip3

###About alb_add.py
`alb_add.py` is a python script that works with the eyeD3 module to add either the video or custom album art
to the mp3 file.  
`alb_add` can be ran as a stand alone program to add album art to preexisting .mp3 files.  

##Bugs
- Program incapable of downloading songs from Youtube playlists

