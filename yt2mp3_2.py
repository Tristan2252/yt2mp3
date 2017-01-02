import sys, getopt
import subprocess as sp
import string
import time
import os

        
"""
Print out usage for user
"""
def usage():
    print("")
    print("$ yt2mp3 [YOUTUBE URL] [OPTIONS]")
    print("")
    print("Options:")
    print("[-u]                 run update for yt2mp3 and youtube-dl")
    print("[-v]                 run yt2mp3 in verbose mode (display all output)")
    print("[-t] [00:00:00.000]  set time to get album art from")
    print("[-r]                 remove all temp files")
    print("[-k]                 keep all temp files")
    print("[-h]                 print help screen")
    print("[-d] [PATH]          set a custom download path")
    print("")
    print("In App Commands:")
    print("[\exit]              exit program at any input")
    print("[\\back]              use to redo tags")
    print("[\help]              print out usage in app")
    print("")



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
        """
        ffmpeg binary uses to call ffmpeg when bash string command is called
        """
        self.FFMPEG_BIN = 'ffmpeg -loglevel panic -nostats'

        self.link = ""
        self.file_path = ""


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
            if os.path.getctime(i) > os.path.getctime(cur_file):
                cur_file = i

        self.v_file_path = cur_file

    def set_tags(self):
        print("Enter the fallowing info, all fields can be skipped except the Song Name")
        print("by pressing Enter. Use '\\back' to redo current field.\n")
        
        while True:
            for i,prompt in enumerate(self.prompt_lst):
                self.print_tags()
                tmp_str = get_input("\033[K" + prompt)

                if tmp_str == '\\back':
                    print("\033[8A")
                    break
               
                # take care of special chars for bash 
                tmp_str = parse_str(tmp_str)

                if i == 0:
                    self.song = tmp_str

                    # Fail safe for song title, see self.song description
                    if self.song == "":
                        self.song = "Dutchman\ must\ have\ a\ captain"

                elif i == 1:
                    self.artist = tmp_str
                elif i == 2:
                    self.album = tmp_str
                elif i == 3:
                    self.alb_artist = tmp_str
                elif i == 4:
                    self.genre = tmp_str
                    print("\033[8A")
                    self.print_tags()
                    return

                print("\033[8A") # ascii escape sequences are awesome!!


    def print_tags(self):
        print("Song Name         : {}".format(self.song))
        print("Artist Name       : {}".format(self.artist))
        print("Album Name        : {}".format(self.album))
        print("Album Artist Name : {}".format(self.alb_artist))
        print("Genre             : {}".format(self.genre))
        print() # adding some white space



class Command(object):
    
    def __init__(self, verbose):
        self.verbose = verbose

        self.update_cmd = "git clone https://github.com/Tristan2252/yt2mp3; yt2mp3/install.sh; sudo rm -r yt2mp3/"
        self.rm_cmd = "sudo rm -r {}" # left blank so that path can be added to it
        self.youtube_dl_cmd = 'youtube-dl -r 25.5M -f 22/18/43/36/17 -o "{}/DLSONG.%(ext)s" {}'
        """
        -loglevel error: Show all errors, including ones which can be recovered from.
        """
        self.ffmpeg_conv = "ffmpeg -loglevel error -nostats -i {}"\
                           " -metadata title={} -metadata artist={} -metadata album_artist={}"\
                           " -metadata album={} -metadata genre={} -b:a 192K -vn {}.mp3"
        self.ffmpeg_art = "ffmpeg -loglevel error -nostats -i {} -ss {} -vframes 1 {}"
        
    def download(self, path, link):
        print("\033[1A" + "\033[K")
        # ugh, I dont like this its too hard to read and fallow... TODO: A better way?
        self.youtube_dl_cmd = self.youtube_dl_cmd.format(path, link)
        self.run(self.youtube_dl_cmd)

    def apply_tags(self, song_obj):
        print(song_obj.song)
        self.run(self.ffmpeg_conv.format(
                    song_obj.v_file_path,
                    song_obj.song,
                    song_obj.artist,
                    song_obj.alb_artist,
                    song_obj.album,
                    song_obj.genre,
                    song_obj.song))

    def get_vid_art(self, vid_path, vid_time, tmp_folder):
        print() # account for loading animation printing 
        self.run(self.ffmpeg_art.format(
            vid_path, vid_time, tmp_folder + "/output.jpg"))

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

    def run(self, cmd):

        """
        if verbose is set run Popen with no piping so that the user can see 
        output for temselvs
        """
        if self.verbose:
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

        error = proc.communicate()[1]
        if str(error) != "b''":
            print("Error Faild Subprocess: {}\n\n".format(cmd))
            sys.exit()

    """
    The CR character '\r' goes to the begining of the current line and writes from 
    there 
    CREDIT: http://stackoverflow.com/questions/5290994/python-remove-and-replace-printed-items
    """
    def progress(self, p):
        
        cnt = 0
        while p.poll() == None:
            string = "\033[1A\033[KLoading" + "." * cnt
            print(string)
            time.sleep(1)

            cnt += 1
            if cnt == 5:
                # clear out dots with spaces
                print ("Loading     ", end="\r")
                cnt = 0

        print("\033[2A\033[K")

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
    
    #################################################################################
    #                           Primary Functions start here                        #
    #################################################################################
    
    # check for or set valid youtube url to download from
    if (not flags.get_link()):
        flags.link = get_input("Enter Youtube Download Link: ")

    
    ###########################     begin donwload     ##############################
    yt2mp3.download(flags.download_path, flags.link)

    
    ###############################   init song   ###################################
    song = Song()
    song.set_file_path(flags.download_path)
    song.set_tags()

    yt2mp3.apply_tags(song)
    yt2mp3.get_vid_art(song.v_file_path, flags.time, flags.download_path)

if __name__ == "__main__":
   
    # clear screen and print at top: see http://www.tldp.org/HOWTO/Bash-Prompt-HOWTO/x361.html
    print("\033[2J\033[0;0H")
    print("")
    print("\t\t#############################")
    print("\t\t#### -- Yt2mp3 BETA 2 -- ####")
    print("\t\t#############################")
    print("")

    main()
