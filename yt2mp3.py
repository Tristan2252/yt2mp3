#!/usr/bin/env python3

from mutagen.id3 import APIC
from mutagen.mp3 import MP3
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
YELLOW = lambda string: "\033[33;1m{}\033[0m".format(string)
WHITE = lambda string: "\033[37;1m{}\033[0m".format(string)

##################  STDOUT Manipulation  ###########################
CLEAR_REPLACE = lambda line_num: "\033[{}A\033[K".format(line_num)
REPLACE = lambda line_num: "\033[{}A".format(line_num)
CLEAR_LINE = lambda: "\033[K"

#################################################################################
#                                                                               #
#                             Helper Functions                                  #
#                                                                               #
#################################################################################
"""
Splash screen to print to user when called, not much more to explane here
return: 
"""
def draw_screen():
    print("\033[2J\033[0;0H")
    print("")
    print("\t\t#############################")
    print("\t\t#### -- " + RED("Yt2mp3 BETA 2") + " -- ####")
    print("\t\t#############################")
    print("\n")

"""
Print out usage for user
return:
"""
def usage():
    print("\n"\
          "$ yt2mp3 [YOUTUBE URL] [OPTIONS]\n"\
          "\n"\
          "Options:\n"\
          "[-u]                 run update for yt2mp3 and youtube-dl\n"\
          "[-v]                 run yt2mp3 in verbose mode (display all output)\n"\
          "[-t] [00:00:00.000]  set time to get album art from\n"\
          "[-r]                 remove all temp files\n"\
          "[-k]                 keep all temp files\n"\
          "[-h]                 print help screen\n"\
          "[-d] [PATH]          set a custom download path\n"\
          "\n"
          "[--alb_add] [JPG PATH] [MP3 PATH]          run alb-add function\n"\
          "\n"\
          "In App Commands:\n"\
          "[\exit]              exit program at any input\n"\
          "[\help]              print out usage in app\n"\
          "[\\back]              use to redo tags ONLY\n"\
          "\n")



"""
Custom input function, takes in string as input and passes it into input. 
get_input() then checks the input given for commands such as \exit or \help 
to provide the user with additional functionality when being prompted with 
requited input

param string: type string used as prompt to pass into input()
return ans: type string of users input
"""
def get_input(string):
    while True:
        ans = input("{}".format(string))

        # check for special commands
        if ans == '\exit':
            sys.exit()
        elif ans == "\help":
            usage()
        else:
            return ans


def clean_str(string):
    nu_str = string

    # blacklisted trailing chars to clean from string 
    bad_chars = [" ", "'", ";", ":", ",", '"']

    if nu_str == "":
        return nu_str
   
    # check first and last chars
    while True:

        # Clean string by checking for trailing blacklisted chars
        if nu_str[0] in bad_chars:
            nu_str = string[1:]
        if nu_str[-1] in bad_chars:
            nu_str = nu_str[:-1]
        
        # Check if string is clean for both 
        if nu_str[0] not in bad_chars:
            if nu_str[-1] not in bad_chars:
                break
    
    return nu_str

"""
Iterates through string and sets special chars to chars usable by the program, most of
these include bash chars because input is passed into youtube-dl through bash using 
with provided strings from the user. Other cases include extra spaces or quotes at the
end or begining of the string. This happens when items are put into input via drag and 
drop. Newlines are also striped usig rstrip.

param string: type string, the string to parse
return nu_str: type string consisting of the edited string
"""
def parse_str(string):
    nu_str = string
    
    # Chars to change for bash interpretation
    chars = {" ": "\ ",
            "(": "\(",
            ")": "\)",
            "&": "\&",
            "'": "\\'"}
    
    nu_str = clean_str(nu_str)
    
    # replace chars for bash to read
    for key in chars:
        nu_str = nu_str.replace(key, chars[key])

    nu_str = nu_str.rstrip("\n") # remove newline
    return nu_str

#################################################################################
#                                                                               #
#                                FLAGS Class                                    #
#                                                                               #
#  This class is used to look through args passed into yt2mp3 and store them    #
#  as flags to be used through out the program                                  #
#                                                                               #
#################################################################################

class Flags(object):
    def __init__(self, args):

        """
        A list from sys.argv() containing all the args used when yt2mp3 was called
        from the shell. This list is set to a var local to the flags class so that 
        it can be uese throughout the class without having to pass it in
        """
        self.arg_lst = args 

        #################################################################################
        #                                                                               #
        #                           v PROGRAM DEFAULT VALUES v                          #
        #                                                                               #
        #################################################################################
        
        """
        Verbose flag to run program in verbose mode if set to True or 1 then flag is set, If set to 0 no 
        debug output is printed to screen. When flag is set, commands ran from Command.run are ran without
        catching input.
        """
        self.verbose = 0

        """
        Flag to keep or delete temp folder after program is done running. If set to
        1 the cleanup function is not ran at then end of the program. 
        """
        self.keep_files = 0
        
        """
        Update flag, if set puts the program into update mode and then exits from update. If set to 0 
        the program runs in normal mode, use this flag to update the program only.
        """
        self.update = 0

        """
        Remove temp flag is used to remove temp files form the command line using the '-r' option.
        Like update after the function is ran the program immediately exits
        """
        self.remove_tmp = 0

        """
        Usage flag, if set the help screen is printed to the user and then exits out. Used as the 
        '-h' flag from the command line
        """
        self.usage = 0

        """
        Alb_add flag, if set the alb_add fuctionality of the program is ran and exits after done 
        """
        self.alb_add = 0

        """
        To change the folder where yt2mp3 stores temp data such as the downloaded mp4 or
        output.jpg (album art) as well as any other logs for debuging
        """
        self.download_path = "/tmp/yt2mp3"

        """
        Home Music filder var. Can be used to change the destination to move song at the
        end of the program
        """
        self.music_folder = "$HOME/Music"
        
        """
        Time to get frame from video for the album art. If changed must be in format
        Hr:Min:Sec.000 so the ffmpeg can read it in as a valid argument
        """
        self.time = '00:00:10.000'

        """
        Var used to store youtube link
        """
        self.link = ""
    
    """
    Set flags is a tokenizer that goes through each arg passed into yt2mp3 and determines its 
    meaning and sets corresponding flag. For details on flags see usage or Flags.__init__.
    """
    def set_flags(self):
        if '-u' in self.arg_lst:
            self.verbose = 1
            self.update = 1
        if '-v' in self.arg_lst:
            self.verbose = 1
        if '-t' in self.arg_lst:
            self.time = self.get_coArg('-t')
        if '-r' in self.arg_lst:
            self.verbose = 1
            self.remove_tmp = 1
        if '-k' in self.arg_lst:
            self.keep_files = 1
        if '-h' in self.arg_lst:
            self.usage = 1
        if '-d' in self.arg_lst:
            music_folder = get_coArg('-d')
        if '--alb_add' in self.arg_lst:
            self.alb_add = 1
        
    def get_coArg(self, arg):
        for i, item in enumerate(self.arg_lst):
            # test if its the arg we want
            if item == arg:
                # coarg is asways 1 index after arg thus i+1
                return self.arg_lst[i+1] 

    def get_link(self):
        for string in self.arg_lst:
            if 'http' in string:
                if "youtube.com" in string:
                    self.link = string
                    return string
                else:
                    return False


class Song(object):
    def __init__(self):
        self.v_file_path = "",
        self.s_file_path = ""
        self.art_file_path = ""
        self.song = ""
        self.artist = ""
        self.album = ""
        self.alb_artist = ""
        self.genre = ""
        
        self.prompt_lst = ["Enter Song Name: ", \
                           "Enter Artist Name: ", \
                           "Enter Album Name: ", \
                           "Enter Album Artist Name: ", \
                           "Enter Genre: "]

    def set_file_path(self, download_path):

        # no more stdout from ls, Thank God!
        file_lst = os.listdir(download_path)

        if len(file_lst) == 1:
            self.v_file_path = download_path + "/" + file_lst[0]
            # empty return, nothing more to do
            return

        # find the most recent file in the list
        # test against first element in the list
        cur_file = download_path + "/" + file_lst[0]
        for i in file_lst:
            i = download_path + "/" + i
            if (".mp4" in i) and (os.path.getctime(i) > os.path.getctime(cur_file)):
                cur_file = i

        self.v_file_path = cur_file

    def set_tags(self):
        
        draw_screen()
        while True:

            for i,prompt in enumerate(self.prompt_lst):
                print("Enter the fallowing info, all fields can be skipped except the Song Name")
                print("by pressing Enter. Use '\\back' to redo previous field.\n")

                self.print_tags()
                tmp_str = get_input(CLEAR_LINE() + self.prompt_lst[i])

                if tmp_str == '\\back':
                    draw_screen()
                    break
               
                # take care of special chars for bash 
                tmp_str = tmp_str
                if tmp_str or i == 4: # if == 4 then enter statement because return is needed 
                    if i == 0:
                        # Fail safe for song title, see self.song description
                        self.song = tmp_str
                        self.s_file_path = self.song + ".mp3"

                    elif i == 1:
                        self.artist = tmp_str
                    elif i == 2:
                        self.album = tmp_str
                    elif i == 3:
                        self.alb_artist = tmp_str
                    elif i == 4:
                        self.genre = tmp_str
                        draw_screen() # get rid of top instructions
                        self.print_tags()
                        return
                    
                    if self.song == "":
                        self.song = "Dutchman\ must\ have\ a\ captain"
                        self.s_file_path = self.song + ".mp3"
                    
                draw_screen()

    def get_alb_art(self, tmp_folder):

        opt = get_input("Would you like to Add a custom Album art? y/N: ")
        if opt == "y" or opt == "yes" or opt == "Y":
            while True:
                self.art_file_path = clean_str(get_input(CLEAR_LINE() + "Enter custom art path here: "))

                if os.path.isfile(self.art_file_path):
                    if ".jpg" in self.art_file_path:
                        break
                else:
                    print(CLEAR_REPLACE(2) +YELLOW(self.art_file_path + " not fond or invalid type"))

        else:
            self.art_file_path = tmp_folder + "/output.jpg"
        

    def print_tags(self):
        print("\033[37;3mTags List:\033[0m")
        print("Song Name         : {}\t File Name: {}".format(WHITE(self.song), WHITE(parse_str(self.s_file_path))))
        print("Artist Name       : {}".format(WHITE(self.artist)))
        print("Album Name        : {}".format(WHITE(self.album)))
        print("Album Artist Name : {}".format(WHITE(self.alb_artist)))
        print("Genre             : {}".format(WHITE(self.genre)))
        print() # adding some white space


class Command(object):
    
    def __init__(self, verbose):
        self.verbose = verbose

        self.update_cmd = "sudo git clone https://github.com/Tristan2252/yt2mp3; yt2mp3/install.sh; sudo rm -r yt2mp3/"
        self.youtube_dl_update = "sudo youtube-dl -U"
        self.rm_cmd = "rm -r {}" # left blank so that path can be added to it
        self.youtube_dl_cmd = 'youtube-dl --no-playlist -r 25.5M -f 22/18/43/36/17 -o "{}/DLSONG.%(ext)s" {}'
        """
        -loglevel error: Show all errors, including ones which can be recovered from.
        """
        self.ffmpeg_conv = "ffmpeg -y -loglevel error -nostats -i {}"\
                           " -metadata title={} -metadata artist={} -metadata album_artist={}"\
                           " -metadata album={} -metadata genre={} -b:a 192K -vn {}"
        """
        vid_path, vid_time, outputh_path
        """
        self.ffmpeg_art = "ffmpeg -y -loglevel error -nostats -i {} -ss {} -vframes 1 {}"
        self.mkdir = "mkdir {}"
        self._albadd = "alb_add {} {}"
        
    def download(self, path, link):
        print(CLEAR_REPLACE(1))
        # ugh, I dont like this its too hard to read and fallow... TODO: A better way?
        self.youtube_dl_cmd = self.youtube_dl_cmd.format(path, link)
        self.run(self.youtube_dl_cmd)

    def apply_tags(self, song_obj):

        while os.path.isfile(song_obj.s_file_path):
            print(YELLOW("You already have a file Called {}").format(song_obj.s_file_path))
            opt = get_input("Would you like to replace it y/N: ")
            print(CLEAR_REPLACE(1))
            if opt == "y" or opt == "Y" or opt == "yes":
                break
            
            print(CLEAR_REPLACE(2) + YELLOW("NOTE: Changing the name only changes the file name not the Song title"))
            song_obj.s_file_path = get_input(CLEAR_LINE() + "Enter New file name: ")
           
            # update file status in tag list
            draw_screen()
            song_obj.print_tags()
        
        print(CLEAR_REPLACE(2))

        self.run(self.ffmpeg_conv.format(
                    parse_str(song_obj.v_file_path),
                    parse_str(song_obj.song),
                    parse_str(song_obj.artist),
                    parse_str(song_obj.alb_artist),
                    parse_str(song_obj.album),
                    parse_str(song_obj.genre),
                    parse_str(song_obj.s_file_path)))

    def pull_alb_art(self, file_path, time, art_path):
        self.run(self.ffmpeg_art.format(file_path, time, art_path))

    def check_folder(self, ck_folder):
        if not os.path.isdir(ck_folder):
            print("Temp Folder Created at: " + ck_folder)
            self.run(self.mkdir.format(ck_folder), True)

    def update(self):
        # remove anything in install dir
        self.run(self.rm_cmd.format("/opt/yt2mp3/*"))
        self.run(self.update_cmd)
        self.run(self.youtube_dl_update)
        # exit program after update
        sys.exit()

    def print_usage(self):
        usage()
        sys.exit()

    def alb_add(self, art=None, song=None):
            
        ##########################################################################
        #          Conditons to allow for alb_add to be ran standalone           #
        ##########################################################################
        if not song:
            while True:
                song_file = get_input("Enter song file path: ")
                if os.path.isfile(song_file) and ".mp3" in song_file:
                    draw_screen()
                    break
                draw_screen()
                print(YELLOW("File not found or invalid type"))
        else:
            song_file = song

        if not art:
            while True:
                art_file = get_input("Enter art file path: ")
                if os.path.isfile(art_file) and ".jpg" in art_file:
                    draw_screen()
                    break
                draw_screen()
                print(YELLOW("File not found or invalid type"))
        else:
            art_file = art
        

        p = open(art_file, 'rb').read()
        audio = MP3(song_file)
        audio['APIC'] = APIC(3, 'image/jpeg', 3, 'Front cover', p)
        audio.save()


    def remove_tmp(self, path):
        
        # only attempt to remove if folder exists
        if os.path.isdir(path):
            self.run(self.rm_cmd.format(path))

        print("\n Temp Files removed\n")
        sys.exit()

    def run(self, cmd, output=False):

        """
        if output or verbose is set run Popen with no piping so that the user can see 
        output for temselvs
        """
        if output or self.verbose:
            proc = sp.Popen(cmd, shell=True)
            proc.wait()
            
            """
            empty return to break out of funciton, nothing else needed to be done
            error checking not needed because user can see all output with verbose
            """
            return

        """
        If verbose flag not set then use pipe to catch output so that user doesnt 
        see it as well as for proccessing errors
        """
        proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        self.progress(proc)
        proc.wait()
        
        # Grab stderr to process
        error = str(proc.communicate()[1])
        if error != "b''":
            print(RED("Error Faild Subprocess: ") + "{}".format(cmd))
            print(YELLOW(error[2:])) # print stderr to user
            sys.exit()

    """
    The CR character '\r' goes to the begining of the current line and writes from 
    there 
    CREDIT: http://stackoverflow.com/questions/5290994/python-remove-and-replace-printed-items
    """
    def progress(self, p):
        
        draw_screen()
        cnt = 0
        while p.poll() == None:
            string = CLEAR_REPLACE(1) + "Loading" + "." * cnt
            print(string)
            time.sleep(1)

            cnt += 1
            if cnt == 5:
                # clear out dots with spaces
                print (CLEAR_REPLACE(1) + "Loading     ")
                cnt = 0
        
        # Overwrite Loading animation
        print(CLEAR_REPLACE(2))


def main():

    ################################################################################
    #                                 setup flags                                  #
    ################################################################################
    
    # init flags class and pass in command args
    flags = Flags(sys.argv[1:])
    # go through all the command flags and set them
    flags.set_flags()
    # init yt2mp3 and let command know if it needs to be verbose or not
    yt2mp3 = Command(flags.verbose)
    
    #################################################################################
    #                                                                               #
    #                            Standalone Functions                               #
    #  below code uses sys.exit() at the end of each function to halt the program   #
    #  after running. This section consists of fuctions that are ment to run        #
    #  seperately from the primary operation of the program such as update, help    #
    #  and remove. These functions are tested before the primary functions so that  #
    #  if their flags are set, the desired function and the desired function ONLY   #
    #  is executed.                                                                 #
    #                                                                               #
    #################################################################################
    
    if (flags.update):
        # run update of yt2mp3 and youtube-dl
        yt2mp3.update()

    if (flags.usage):
        # print help page
        yt2mp3.print_usage()

    if (flags.remove_tmp):
        # delete temp file
        yt2mp3.remove_tmp(flags.download_path)

    if (flags.alb_add):
        
        try:
            # attempt to pass arg 1 and 2 into alb_add()
            yt2mp3.alb_add(flags.arg_lst[1], flags.arg_lst[2])
        except IndexError:
            # if no args run alb_add() as default
            yt2mp3.alb_add()
        sys.exit()
    
    #################################################################################
    #                                                                               #
    #                           Primary Functions start here                        #
    #                                                                               #
    #  Functions that are called without exiting the program directly after         #
    #  returning. These functions are used as the primary functionality of yt2mp3   #
    #                                                                               #
    #################################################################################

    # check if download path is valid
    yt2mp3.check_folder(flags.download_path)
    
    # check for or set valid youtube url to download from
    if (not flags.get_link()):
        flags.link = get_input("Enter Youtube Download Link: ")

        # Get rid of youtube timestamp in link, youtube-dl gives an error because of this 
        if '&t=' in flags.link:
            flags.link = flags.link.split('&')[0]

    
    #################################################################################
    #                               begin donwload                                  #
    #################################################################################

    yt2mp3.download(flags.download_path, flags.link)

    
    #################################################################################
    #                                 init song                                     #
    #                                                                               #
    #  Set up song class and needed flags to be used through out the program        #
    #                                                                               #
    #################################################################################

    song = Song()
    
    song.set_file_path(flags.download_path)
    # Get tags from user
    song.set_tags()
    # Ask user if they would like to set a custom art or use default
    song.get_alb_art(flags.download_path)

    # if the art_file_path is set to path+output.jpg, in oter words its the default then
    # fetch the art from the mp4 file using pull_alb_art()
    if song.art_file_path == flags.download_path + "/output.jpg":
            yt2mp3.pull_alb_art(song.v_file_path, flags.time, song.art_file_path)

    # add all tags and convert to mp3 using ffmpeg
    yt2mp3.apply_tags(song)
    # Add album art using alb_add()
    yt2mp3.alb_add(song.art_file_path, song.s_file_path)

    # clean up tmp
    if not flags.keep_files:
        yt2mp3.run(yt2mp3.rm_cmd.format(flags.download_path + "/*"))

    draw_screen()
    print("\033[37;3mProgram Summary:\033[0m")
    print("Added {} to {} as album conver!\n".format(WHITE(song.art_file_path), WHITE(song.s_file_path)))
    song.print_tags()
    print("\n" + YELLOW("Finished!") + " Thank you for using" + RED(" Yt2mp3\n"))

if __name__ == "__main__":
    draw_screen() # print splash screen
    main()
