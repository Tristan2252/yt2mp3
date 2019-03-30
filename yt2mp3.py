#!/usr/bin/env python3

from __future__ import unicode_literals
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC # add album art
from mutagen.mp3 import MP3  # add album art
import youtube_dl
import urllib.request
import subprocess as sp
import sys, getopt
import time
import os


"""
#########################################################################################
#                        Lambda's for Print escape sequences                            #
#                                                                                       #
#  RED: Concatenates escape sequence for red text with the string passed to it          #
#  YELLOW: Concatenates escape sequence for yellow text with the string passed to it    #
#  WHITE: Concatenates escape sequence for white text with the string passed to it      #
#                                                                                       #
#  CLEAR_REPLACE: Escape sequence for moving x lines up then clearing the line,         #
#                 allowing for priting from that line                                   #
#  REPLACE: Escape sequence that moves to the begining of the current line or line      #
#           passed in                                                                   #
#  CLEAR_LINE: Runs escape sequence to clear current line                               #
#                                                                                       #
#  http://www.tldp.org/HOWTO/Bash-Prompt-HOWTO/x361.html                                #
#  http://ascii-table.com/ansi-escape-sequences.php                                     #
#                                                                                       #
#########################################################################################
"""

#########################  COLORS  #################################
RED = lambda string: "\033[31;1m{}\033[0m".format(string)
GREEN = lambda string: "\033[92m{}\033[0m".format(string)
YELLOW = lambda string: "\033[33;1m{}\033[0m".format(string)
WHITE = lambda string: "\033[37;1m{}\033[0m".format(string)

##################  STDOUT Manipulation  ###########################
CLEAR_REPLACE = lambda line_num: "\033[{}H\033[K".format(line_num)
REPLACE = lambda line_num: "\033[{}A".format(line_num)
CLEAR_LINE = lambda: "\033[K"
CLEAR_SCREEN = lambda: "\033[2J"

#################################################################################
#                                                                               #
#                             Helper Functions                                  #
#                                                                               #
#################################################################################

def usage():
    print("\n\n"\
          "In App Commands:\n"\
          "[\exit]              exit program at any input\n"\
          "[\help]              print out usage in app\n"\
          "[\\back]              use to redo a tag \n"\
          "[\clear]             use to clear a tag \n"\
          "\n")

def update():
    sp.check_call(['sudo', 'git', '--git-dir=/usr/local/src/yt2mp3/.git', '--work-tree=/usr/local/src/yt2mp3/', 'pull', '--force'])
    sp.check_call([sys.executable, '-m', 'pip', 'install', 'youtube-dl', '--upgrade', '--user'])

def leave(status):
    print(CLEAR_SCREEN())
    sys.exit(status)

def subproc_wait(screen_obj, subproc_fuction, status_string):
    try:
        pid = os.fork()
    except OSError:
        exit("Could not create a child process")
    
    if pid == 0:
        subproc_fuction()
        sys.exit(0)
    
    count = 0
    while True:
        status = os.waitpid(pid, os.WNOHANG) 
        
        if status[1] != 0:
            print(RED("\nYT2MP3 ERROR: ") + "Occurred in subproc function: " + YELLOW(subproc_fuction.__name__) + "()")
            input("\nHit Enter to exit")
            sys.exit(-1)
        elif status[0] != 0:
            break

        screen_obj.set_progress(status_string, count)
        count += 1
        time.sleep(0.1)

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(CLEAR_SCREEN())
        print(msg)
        sys.exit(-1)

class Screen(): 

    def __init__(self):
        """
        Splash screen to print to user when called, not much more to explane here
        return: 
        """
        self.__splash=CLEAR_REPLACE("0;0") + "\n" + \
                      CLEAR_LINE() + "\t\t#############################\n" + \
                      CLEAR_LINE() + "\t\t#   -- " + RED("Yt2mp3 BETA 3.0") + " --   #\n" + \
                      CLEAR_LINE() + "\t\t#############################\n"
        self.__progress=""
        self.__menu=""

        print(CLEAR_SCREEN())

    def set_progress(self, status_msg="", status=-1):
        if status == -1:
            self.__progress = status_msg
        elif (status % 4) == 0:
            self.__progress = status_msg + " -"
        elif (status % 4) == 1:
            self.__progress = status_msg + " \\"
        elif (status % 4) == 2:
            self.__progress = status_msg + " |"
        elif (status % 4) == 3:
            self.__progress = status_msg + " /"
        
        self.draw()
    
    def set_menu(self, menu):
        self.__menu = menu

    def prompt(self, prompt, function=None, menu_get_method=None):

        if type(prompt) == list:

            index = 0
            while index < len(prompt):
                reply = input(prompt[index])
                sys.stdout.write("\033[1A\033[K") # clear prompt after getting input

                if '\exit' in reply:
                    leave(0)
                elif '\\back' in reply and index != 0:
                        index -= 1
                elif '\help' in reply:
                    print("\033[1A \033[K \r")
                    usage()
                elif '\clear' in reply:
                    function[index]("")
                    index += 1
                elif '\sub' in reply:
                    # TODO: add ability to subtract words from answer
                    index = index
                elif reply:
                    function[index](reply)
                    index += 1
                else:
                    index += 1

                self.set_menu(menu_get_method())
                self.draw()

        else:
            while True:
                reply = input(prompt)
                sys.stdout.write("\033[1A\033[K") # clear prompt after getting input

                if '\exit' in reply:
                    leave(0)
                elif '\help' in reply:
                    print("\033[1A \033[K \r")
                    usage()
                else:
                    break

            if function:
                function(reply)
            else:
                return reply

    def draw(self):
        sys.stdout.write(self.__splash + "\n\033[K" + self.__progress + "\n\n" + self.__menu + "\n")

class Audio(object):
    def __init__(self):
        self.__name = ""
        self.__artist = ""
        self.__album = ""
        self.__alb_artist = ""
        self.__genre = ""
        self.__cover= ""
        self.__yt_link = ""


    def set_name(self, name): 
        self.__name = name

    def set_artist(self, artist): 
        self.__artist = artist

    def set_album(self, album): 
        self.__album = album

    def set_alb_artist(self, album_artist): 
        self.__alb_artist = album_artist

    def set_genre(self, genre): 
        self.__genre = genre

    def set_cover(self, cover_path): 

        nu_str = cover_path

        # blacklisted trailing chars to clean from string 
        bad_chars = [" ", "'", ";", ":", ",", '"']

        if nu_str == "":
            self.__cover = nu_str
       
        # check first and last chars
        while True:

            # Clean string by checking for trailing blacklisted chars
            if nu_str[0] in bad_chars:
                nu_str = cover_path[1:]
            if nu_str[-1] in bad_chars:
                nu_str = nu_str[:-1]
            
            # Check if string is clean for both 
            if nu_str[0] not in bad_chars:
                if nu_str[-1] not in bad_chars:
                    break

        self.__cover = nu_str

    def set_yt_link(self, link): 
        if "youtube" in link:
            self.__yt_link = link

    def get_yt_link(self): 
        return self.__yt_link
    
    def get_name(self): 
        return self.__name

    def download(self):
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'outtmpl': self.__name + '.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'logger': MyLogger(),
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.__yt_link])

    def fetch_meta(self):
        ydl_opts = {
            'noplaylist': True,
            'logger': MyLogger(),
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(self.__yt_link, download=False)
        
        try:
            self.__name = meta['title'].split(" - ")[1]
            self.__artist = meta['title'].split(" - ")[0]
            return 0
        except IndexError:
            self.__name = meta['title']
            return 1


    def apply_tags(self):
        audio = EasyID3(self.__name + ".mp3")
        audio['title'] = self.__name
        audio['artist'] = self.__artist
        audio['album'] = self.__album
        audio['albumartist'] = self.__alb_artist
        audio['genre'] = self.__genre
        audio.save()

    def apply_cover(self):
        
        if "http" in self.__cover:
            opener=urllib.request.build_opener()
            opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
            urllib.request.install_opener(opener)

            urllib.request.urlretrieve(self.__cover, "cover.jpg")
            self.__cover = "cover.jpg"
        
        if self.__cover:
            p = open(self.__cover, 'rb').read()
            audio = MP3(self.__name + ".mp3")

            audio['APIC'] = APIC(3, 'image/jpeg', 3, 'Front cover', p)
            audio.save()

        if os.path.exists("cover.jpg"):
            os.remove("cover.jpg")

    def tag_menu(self):
        return CLEAR_LINE() + "\033[37;3mTags List:\033[0m \n" + \
        CLEAR_LINE() + "Name              : {}\n".format(WHITE(self.__name)) + \
        CLEAR_LINE() + "Artist Name       : {}\n".format(WHITE(self.__artist)) + \
        CLEAR_LINE() + "Album Name        : {}\n".format(WHITE(self.__album)) + \
        CLEAR_LINE() + "Album Artist Name : {}\n".format(WHITE(self.__alb_artist)) + \
        CLEAR_LINE() + "Genre             : {}\n".format(WHITE(self.__genre))

def main():
    audio = Audio()
    screen = Screen()
    screen.draw()
   
    print("For help enter: \help")
    while audio.get_yt_link() == "":
        audio.set_yt_link(screen.prompt(CLEAR_REPLACE("7;0") + "Enter Video Link: "))

    screen.set_progress("Link Set: " + audio.get_yt_link())
    screen.set_menu(audio.tag_menu())
    screen.draw()

    tag_setters = [audio.set_name, audio.set_artist, audio.set_album, \
                   audio.set_alb_artist, audio.set_genre, audio.set_cover]
    tag_prompts = ["Enter Name: ", "Enter Artist: ", "Enter Album: ", \
                   "Enter Album Artist: ", "Enter Genre: ", "Enter Album Cover: "]
    
    screen.set_progress(YELLOW("Fetching Metadata..."))
    if audio.fetch_meta():
        screen.set_progress(GREEN("Auto Fill Not Available"))

    screen.set_menu(audio.tag_menu())
    screen.draw()
    screen.prompt(tag_prompts, tag_setters, audio.tag_menu) # Note: waits for input from user

    # name must exist to create file
    if not audio.get_name():
        audio.set_name("yourmp3")
        screen.set_menu(audio.tag_menu())
    
    subproc_wait(screen, audio.download, YELLOW("Downloading "))
    subproc_wait(screen, audio.apply_tags, YELLOW("Applying Tags "))
    subproc_wait(screen, audio.apply_cover, YELLOW("Applying Album Cover "))
    
    print(CLEAR_SCREEN())
    screen.set_progress(GREEN("\033[1mComplete!"))


if __name__ == "__main__":
    
    args = sys.argv[1:]
    if '-l' in args:
        while True:
            main()
    elif '-u' in args:
        update()
        sys.exit(0)
    else:
        main()

