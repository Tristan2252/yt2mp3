import subprocess as sp
import sys, getopt
#import string
import eyed3
import time
import os



"""
Lambda's for Print escape sequences 
http://www.tldp.org/HOWTO/Bash-Prompt-HOWTO/x361.html
http://ascii-table.com/ansi-escape-sequences.php
"""
#########################  COLORS  #################################
RED = lambda string: "\033[31;1m{}\033[0m".format(string)
YELLOW = lambda string: "\033[33;1m{}\033[0m".format(string)
WHITE = lambda string: "\033[37;1m{}\033[0m".format(string)

##################  STDOUT Manipulation  ###########################
CLEAR_REPLACE = lambda line_num: "\033[{}A\033[K".format(line_num)
CLEAR_LINE = lambda: "\033[K"
REPLACE = lambda line_num: "\033[{}A".format(line_num)

def draw_screen():
    print("\033[2J\033[0;0H")
    print("")
    print("\t\t#############################")
    print("\t\t#### -- " + RED("Yt2mp3 BETA 2") + " -- ####")
    print("\t\t#############################")
    print("\n")

"""
Print out usage for user
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
          "\n"\
          "In App Commands:\n"\
          "[\exit]              exit program at any input\n"\
          "[\help]              print out usage in app\n"\
          "[\\back]              use to redo tags ONLY\n"\
          "\n")



"""
Custom input function to allow for an exit string that stops program at any input 
by the user typing '\exit'
"""
def get_input(string):
    while True:
        ans = input("{}".format(string))
        
        if ans == '\exit':
            sys.exit()
        elif ans == "\help":
            usage()
        else:
            return ans

"""
Parses string to be readable by bash. Uses replace to switch patters such as ' ' with
bash space '\ '. This is done to enable path to be read correctly by bash when it is
passed to bash_call() to call the command string
string: the string to parse
"""
def parse_str(string):
    nu_str = string
    chars = {" ": "\ ",
            "(": "\(",
            ")": "\(",
            "'": "\\'"}
   
    for key in chars:
        nu_str = nu_str.replace(key, chars[key])

    nu_str = nu_str.rstrip("\n") # remove newline
    return nu_str

class Flags(object):
    def __init__(self, args):

        """
        Arguments passed into program are them passed into Flags as a list and then
        used to identify what flags need to be set. See 'def usage()' for details on 
        flags and their meaning. 
        """
        self.arg_lst = args 

        ############### PROGRAM DEFAULT VALUES  ##############
        """
        Verbose flag to run program in verbose mode or not. If set to 0 no debug output
        is printed to screen. If 1 all bash commands print output to stdout
        """
        self.verbose = 0
        """
        Flag to keep or delete temp folder after program is done running. If set to
        1 the clean_up function is not run
        """
        self.keep_files = 0
        self.update = 0
        self.remove_tmp = 0
        self.usage = 0
        """
        Time to get frame from video for song album art. If changed must be in format
        Hr:Min:Sec.000 so the ffmpeg can read it in as a valid argument
        """
        self.download_path = "/tmp/yt2mp3"
        """
        Home Music filder var. Can be used to change the destination to move song at the
        end of the program
        """
        self.music_folder = "$HOME/Music"
        """
        To change the folder where yt2mp3 stores temp data such as the downloaded mp4 or
        output.jpg (album art) as well as any other logs for debuging
        """
        self.time = '00:00:10.000'
        self.link = ""
        self.file_path = ""
        self.alb_add = None


    def print_flag_status(self):
        print("\nArg List: {}\n".format(self.arg_lst))
        print("Verbose: {}".format(self.verbose))
        print("Keep Files: {}".format(self.keep_files))
        print("Update: {}".format(self.update))
        print("Remove: {}".format(self.remove_tmp))
        print("Usage: {}".format(self.usage))
        print("Download Path: {}".format(self.download_path))
        print("Music Folder: {}".format(self.music_folder))
        print("Time: {}".format(self.time))
        print("FFMPEG flags: {}".format(self.FFMPEG_BIN))
        print("Download Link: {}".format(self.link))

    def set_flags(self):
        if '-u' in self.arg_lst:
            # set verbose to see output of rm and mv command
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
        """
        self.song MUST always be set because it is what yt2mp3 uses to set the file name 
        of the song
        """
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
        print("Enter the fallowing info, all fields can be skipped except the Song Name")
        print("by pressing Enter. Use '\\back' to redo current field.\n")
        
        while True:
            for i,prompt in enumerate(self.prompt_lst):
                self.print_tags()
                tmp_str = get_input(CLEAR_LINE() + prompt)

                if tmp_str == '\\back':
                    print(REPLACE(8))
                    break
               
                # take care of special chars for bash 
                tmp_str = parse_str(tmp_str)

                if i == 0:
                    self.song = tmp_str

                    # Fail safe for song title, see self.song description
                    if self.song == "":
                        self.song = "Dutchman\ must\ have\ a\ captain"
                    
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
                
                # idk why i need two of these but 9 doesnt work -__-
                print(CLEAR_REPLACE(7))
                print(CLEAR_REPLACE(2))

    def get_alb_art(self, tmp_folder):

        opt = get_input("Would you like to Add a custom Album art? y/N: ")
        if opt == "y" or opt == "yes" or opt == "Y":
            while True:
                self.art_file_path = get_input(CLEAR_LINE() + "Enter custom art path here: ")

                if os.path.isfile(self.art_file_path):
                    if ".jpg" in self.art_file_path:
                        break
                else:
                    print(CLEAR_REPLACE(2) + YELLOW("File not fond or invalid type"))

        else:
            self.art_file_path = tmp_folder + "/output.jpg"
        

    def print_tags(self):
        print("Song Name         : {}\t File Name: {}".format(WHITE(self.song), WHITE(self.s_file_path)))
        print("Artist Name       : {}".format(WHITE(self.artist)))
        print("Album Name        : {}".format(WHITE(self.album)))
        print("Album Artist Name : {}".format(WHITE(self.alb_artist)))
        print("Genre             : {}".format(WHITE(self.genre)))
        print() # adding some white space


class Command(object):
    
    def __init__(self, verbose):
        self.verbose = verbose

        self.update_cmd = "git clone https://github.com/Tristan2252/yt2mp3; yt2mp3/install.sh; sudo rm -r yt2mp3/"
        self.rm_cmd = "sudo rm -r {}" # left blank so that path can be added to it
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
            song_obj.s_file_path = parse_str(get_input(CLEAR_LINE() + "Enter New file name: "))
           
            # update file status in tag list
            draw_screen()
            song_obj.print_tags()
        
        print(CLEAR_REPLACE(2))

        self.run(self.ffmpeg_conv.format(
                    song_obj.v_file_path,
                    song_obj.song,
                    song_obj.artist,
                    song_obj.alb_artist,
                    song_obj.album,
                    song_obj.genre,
                    song_obj.s_file_path))

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
        # exit program after update
        sys.exit()

    def print_usage(self):
        usage()
        sys.exit()

    def remove_tmp(self, path):
        
        # only attempt to remove if folder exists
        if os.path.isdir(path):
            self.run(self.rm_cmd.format(path))

        print("\n Temp Files removed\n")
        sys.exit()

    def alb_add(self, song_path, art_path):

        ##########################################################################
        #          Conditons to allow for alb_add to be ran standalone           #
        ##########################################################################
        rm_comma = lambda string: string[1:-1] if string[0] == "\\'" else string

        if not song_path:
            while True:
                song_path = rm_comma(get_input("Enter song file path: "))
                if os.path.isfile(song_path) and ".mp3" in song_path:
                    break
                draw_screen()
                print(YELLOW("File not found or invalid type"))

        if not art_path:
            while True:
                art_path = rm_comma(get_input("Enter art file path: "))
                if os.path.isfile(art_path) and ".jpg" in art_path:
                    break
                draw_screen()
                print(YELLOW("File not found or invalid type"))
        
        #TODO: eyed3 only works with python2.7  >:(
        imagedata = open(art_path, "rb").read() # open image
        audiofile = eyed3.load(song_path) # load mp3 into eyed3
        audiofile.tag.images.set(3, imagedata, "image/jpeg", u" ")
        audiofile.tag.save()
        
        draw_screen()
        print("Added {} to {} as album conver!\n".format(WHITE(art_path), WHITE(song_path)))

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
    flags = Flags(sys.argv[1:])
    flags.set_flags()

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
        yt2mp3.update()

    if (flags.usage):
        yt2mp3.print_usage()

    if (flags.remove_tmp):
        yt2mp3.remove_tmp(flags.download_path)

    if (flags.alb_add):
        
        try:
            song = Alb_Add(flags.arg_lst[1], flags.arg_lst[2])
        except IndexError:
            song = Alb_Add(None, None)

        sys.exit()
    
    #################################################################################
    #                           Primary Functions start here                        #
    #################################################################################
    yt2mp3.check_folder(flags.download_path)
    
    # check for or set valid youtube url to download from
    if (not flags.get_link()):
        flags.link = get_input("Enter Youtube Download Link: ")

        # Get rid of youtube timestamp in link, youtube-dl give an error becaus of this 
        if '&t=' in flags.link:
            flags.link = flags.link.split('&')[0]

    
    ###########################     begin donwload     ##############################
    yt2mp3.download(flags.download_path, flags.link)

    
    ###############################   init song   ###################################
    song = Song()
    
    song.set_file_path(flags.download_path)
    song.set_tags()
    song.get_alb_art(flags.download_path)

    if song.art_file_path == flags.download_path + "/output.jpg":
            yt2mp3.pull_alb_art(song.v_file_path, flags.time, song.art_file_path)

    yt2mp3.apply_tags(song)
    yt2mp3.alb_add(song.s_file_path, song.art_file_path)
    

if __name__ == "__main__":
    draw_screen()
    main()
