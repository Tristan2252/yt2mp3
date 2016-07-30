#!/usr/bin/env python3
import sys, getopt
import subprocess as sp
import string
import time
import os


"""
Get a frame from downloaded video to add as the album art. Function calls ffmpeg bash command
with flags to extract a picture, output.jpg, from video and store in the temp file.
vid_path: The found path of the downloaded video, see get_path() for more details
vid_time: The time ffmpeg is to grab a video frame from
return: None
"""
def get_frame(vid_path, vid_time):
    output_path = "{}/output.jpg".format(DOWNLOAD_PATH)

    if not check_file(output_path):
        print("Removing old temp files", end="")
        clean_up(output_path)

    command = '{} -i {} -ss {} -vframes 1 {}'.format(FFMPEG_BIN, vid_path, vid_time, output_path)
    bash_call(command)


"""
Finds the absolute path of the downloaded file in the temp folder using ls and piping output to
grep to search for an mkv or mp4 file. The stdout of grep is then piped to head to make sure to
get the latest file in the temp folder. After file is found the output is captured by python and
set to out var to them be processed into a readable string using parse_str function.(see parse_str) for info
return: absolute path string of downloaded file
"""
def get_path(path):
    proc = sp.Popen("ls -t {}".format(path), stdout=sp.PIPE, shell=True) # ls temp dir by date
    grep_proc = sp.Popen("grep '.mkv\|.mp4\|.mp3'", stdin=proc.stdout, stdout=sp.PIPE, shell=True) # grep for video files
    head_proc = sp.Popen("head -1", stdin=grep_proc.stdout, stdout=sp.PIPE, shell=True) # narrow down to leatest file
    out = head_proc.communicate()[0]
    out = out.decode('utf8', errors='ignore') # convert to sting
    return "{}/{}".format(path, parse_str(out)) # parse path before returning


"""
Uses 'pwd' to get the dir that yt2mp3 was ran from. This info can be used to build the absolute
path of the song file after it is converted to mp3 and moved to the current dir.
return: string of absolute path for current working dir
"""
def get_curPath():
    proc = sp.Popen("pwd", stdout=sp.PIPE, shell=True)
    out = proc.communicate()[0]
    out = out.decode('ascii')
    return parse_str(out)


"""
Prompts user for metadata and stores values in a dictionary for easy passing from function to function.
return: a dictionary of the tags and their values
"""
def get_tags():
    tags = {"artist": 1, "song": 2, "album": 3, "alb_artist": 4, "genre": 5}
    sort_tags = sorted(tags, key=lambda key: tags[key]) # sort dict by kay values
    i = 0 

    while i < len(tags):
        print("")
        for key in sort_tags: # make all tags bash compatable
            tag = get_input("Enter {}: ".format(key))
            if tag == '\\back':
                i = 0
                break
            tags[key] = parse_str(tag)
            i = i + 1

    return tags

def get_input(prompt):
    string = input(prompt)
    
    if string == "\exit":
        sys.exit()

    return string


"""
Builds bash command to call ffmpeg and set metadata of the file. The tag dictionary is used to
input user entered data into the command string before it is called using bash_call() to run the command
tag_lst: a dictionary of the user entered tags
file_path: the absolute path of the files to set metadata for
return: none
"""
def set_tags(tag_lst, file_path):

    song_path = tag_lst["song"] + ".mp3"

    while not check_file(song_path): # if file exists in cur dir then prompt user
        opt = get_input(song_path + " exists, Would you like to overwrite it? Y/N: ")
        if opt == 'Y' or opt.lower() == 'y':
            clean_up(song_path)
            break # break so that check_file doesnt run a second time
        elif opt == 'N' or opt.lower() == 'n':
            print("Renaming file to: {}2.mp3").format(tag_lst["song"])
            tag_lst["song"] = tag_lst["song"] + "2"
            break
        else:
            print("ERROR: Incorrect Input")

    cmd = "{} -i {} -metadata title={} -metadata artist={} -metadata album_artist={}"\
            " -metadata album={} -metadata genre={} -b:a 192K -vn {}.mp3".format(FFMPEG_BIN, file_path,
                    tag_lst["song"],
                    tag_lst["artist"],
                    tag_lst["alb_artist"],
                    tag_lst["album"],
                    tag_lst["genre"],
                    tag_lst["song"])

    bash_call(cmd)


"""
Prompt user for option to use a custom album art or one from get_frame(). If the user
enters the custom option then they will asked to enter the absolute path of the custom album art.
The users input is then parsed for readability and then passes via bash to alb_add.py. If user
enters video option the path of output.jpg crated by get_frame() is passed to alb_add via bash.
NOTE: The paths are passed to alb_add.py via bash because alb_add.py runs on python2.7 because of eyed3
song_path: path of the file to add album art to
vid_path: the path of the video to get the art from
frame_time: the time of the video to get art from
return: none
"""
def set_art(song_path, vid_path, frame_time):

    print("Use custom album art or keep videos?")
    print("\tV: keep video album art")
    print("\tC: use custom")
    opt = get_input("Option: ")

    if opt == 'V' or opt.lower() == 'v':
        print("\nGetting Album Art")
        get_frame(vid_path, frame_time)
        proc = sp.Popen("alb_add {} {}/output.jpg".format(song_path, DOWNLOAD_PATH), shell=True)
        proc.wait()

    elif opt == 'C' or opt.lower() == 'c':
        art_path = get_input("Enter path of custom album art: ")
        art_path = parse_str(art_path)
        proc = sp.Popen("alb_add {} {}".format(song_path, art_path), shell=True)
        proc.wait()

    else:
        return 2 # if user input is not right dont return success '0'

    verbose = 0 # to show output of alb_add.py

    return 0


"""
Parses string to be readable by bash. Uses replace to switch patters such as ' ' with
bash space '\ '. This is done to enable path to be read correctly by bash when it is
passed to bash_call() to call the command string
string: the string to parse
"""
def parse_str(string):
    path = string.replace(" ", "\ ")
    path = path.replace("(", "\(")
    path = path.replace(")", "\)")
    path = path.rstrip("\n") # remove newline
    return path


"""
Calls command using subprocess. Also reads verbose flag and preforms wait function. If verbose
flag is set then the command is ran without piping stdout so that user can view output.
cmd: a string of the command to execute with subprocess
"""
def bash_call(cmd):
    if verbose:
        print(cmd)
        try:
            proc = sp.Popen(cmd, shell=True)
            proc.wait()
        except KeyboardInterrupt:
            print("\nProgram Stopped: BY USER")
            sys.exit(2)
    else:
        try:
            proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
            status(proc)
            proc.wait() # wait just in case
        except KeyboardInterrupt:
            print("\n\nProgram Stopped: BY USER\n")
            sys.exit(2)


"""
Prints status indicator for user to view while subprocess is running bash command
While poll == none or while the proc is stil running print '.' to screen and then
sleep, or wait, one second, then re-poll proc
p: the subprocess command class to print indicator for
"""
def status(p):
    while p.poll() == None:
        print('.', end="", flush=True) # print status
        time.sleep(1)
    print("") # extra print line becase of no \n after previous print


"""
Check if path exists as a file or a dir, if so return 0 for success, if neither
file of dir then return 1 or fail
return: True or False if file or dir exists
"""
def check_file(path):
    if os.path.isfile(path):
        return 0
    elif os.path.isdir(path):
        return 0
    else:
        return 1


"""
Check list of strings for proper url format for sending to youtube-dl.
If the string is less then the len of the youtube url then it is not valid and
is passed, if it isn't then test if the url contains the basic youtube url.
If all tests are true return string eles return false. Program takes in a list
of strings because the function is used to pick out the url within the list of
opts and args passed to yt2mp3
strings: list of strings to search
return: url if true and false otherwise
"""
def check_url(strings):
    url_str = ""
    for string in strings:
        if len(string) < len("http://www.youtube.com"): # if less then len of a link the not a link
            pass
        elif "http" not in string: # if http is not in string its not a link
            pass
        else:
            for letter in string:
                    url_str += str(letter)
                    if url_str == "https://www.youtube.com/":
                        print("Downloading from: " + string)
                        return string
                    if url_str == "http://www.youtube.com/":
                        print("Downloading from: " + string)
                        return string
            print("URL ERROR: url must be a valid youtube url")
    
    print("URL ERROR: no or inproper link found, use -h for help")

    return False


"""
Find the flag (opt), in the list of strings (flags), then return the next
element in the list. This is used to find the argument of a flag.
opt: a string of the flag to search for
flags: the list of all the entered opts and args
return: next string in list
"""
def get_arg(opt, flags):

    for i, flag in enumerate(flags):
        if flag == opt:
            return flags[i+1]


"""
Clean up function used to remove temp files. Runs rm /path/to/file
by building command and sending to subprocess to call. If verbose
flag is set, verbose rm flag is used
file_path: string of file or folder to remove
"""
def clean_up(file_path):
    if verbose:
        sp.Popen("rm -r -v {}".format(file_path), shell=True)
        return

    sp.Popen("rm -r {}".format(file_path), shell=True)


"""
Call mv command to move file to new dest. the -i flag is used to prompt the user
if there is a replica of the file being moved
file_path: the path of the file to move
dest_location: the location to move the file to
return 0 if success and 2 if not
"""
def mv_file(file_path, dest_location):
    
    # if something other than default then bypas prompt
    if dest_location != "~/Music":
        proc = sp.Popen("mv -i {} {}".format(file_path, dest_location), shell=True)
        proc.wait()
        return 0

    print("Current location of song is " + file_path)
    opt = get_input("Would you like to move file to music folder? Y/N: ")
    if opt == 'Y' or opt.lower() == 'y':
        proc = sp.Popen("mv -i {} {}".format(file_path, dest_location), shell=True)
        proc.wait()
        return 0
    elif opt == 'N' or opt.lower() == 'n':
        return 0
    else:
        return 2


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
    print("")


def main():
    print("")
    print("\t\t###########################")
    print("\t\t#### -- Yt2mp3 BETA -- ####")
    print("\t\t###########################")
    print("")

    flags = sys.argv[1:] # get list of opts and args
    if not flags:
        flags = [get_input("Enter video url: ")] # flags needs to be a list to be read correctly

    global verbose # global so that it doesnt need to be passed to every function
    global DOWNLOAD_PATH
    global FFMPEG_BIN

    ############### PROGRAM DEFAULT VALUES  ##############
    """
    Verbose flag to run program in verbose mode or not. If set to 0 no debug output
    is printed to screen. If 1 all bash commands print output to stdout
    """
    verbose = 0
    """
    Flag to keep or delete temp folder after program is done running. If set to
    1 the clean_up function is not run
    """
    keep_files = 0
    """
    Time to get frame from video for song album art. If changed must be in format
    Hr:Min:Sec.000 so the ffmpeg can read it in as a valid argument
    """
    time = '00:00:10.000'
    """
    Home Music filder var. Can be used to change the destination to move song at the
    end of the program
    """
    music_folder = "~/Music"
    """
    To change the folder where yt2mp3 stores temp data such as the downloaded mp4 or
    output.jpg (album art) as well as any other logs for debuging
    """
    DOWNLOAD_PATH = "/tmp/yt2mp3"
    """
    ffmpeg binary uses to call ffmpeg when bash string command is called
    """
    FFMPEG_BIN ='ffmpeg -loglevel panic -nostats'


    if check_file(DOWNLOAD_PATH):
        sp.Popen("mkdir {}".format(DOWNLOAD_PATH), shell=True)

    ############### TEST FOR FLAGS #######################

    if '-u' in flags:
        verbose = 1
        bash_call("sudo rm /opt/yt2mp3/*")
        bash_call("git clone https://github.com/Tristan2252/yt2mp3; yt2mp3/install.sh; sudo rm -r yt2mp3/")
        return # dont run program after update
    if '-v' in flags:
        verbose = 1
    if '-t' in flags:
        time = get_arg('-t', flags)
    if '-r' in flags:
        clean_up(DOWNLOAD_PATH)
        print("\n Temp Files removed\n")
        return # dont run program after update
    if '-k' in flags:
        keep_files = 1
    if '-h' in flags:
        usage()
        return # dont run program after update
    if '-d' in flags:
        music_folder = get_arg('-d', flags)

    link = check_url(flags)
    while link == 0: # until url is correct ask user
        link = get_input("Enter video url: ")

    ############### RUN COMMANDS #######################
    bash_call('youtube-dl -r 25.5M -f 22 -o "{}/DLSONG.%(ext)s" {}'.format(DOWNLOAD_PATH, link))
    file_path = get_path(DOWNLOAD_PATH)

    song_tags = get_tags()
    song_path = get_curPath() + "/" + song_tags["song"] + ".mp3"
    print("\nSetting Song Tags")
    set_tags(song_tags, file_path)

    print("\nSetting Album Art")
    while set_art(song_path, file_path, time): # loop until user input is correct
        pass

    while mv_file(song_path, music_folder):
        pass

    if not keep_files: # keep temp files
        clean_up(DOWNLOAD_PATH)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt: #accept ctl-c by user
        print("\nProgram Stopped: BY USER")
