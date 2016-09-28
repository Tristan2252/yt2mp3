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
    grep_proc = sp.Popen("grep '.mkv\|.mp4\|.mp3\|.webm'", stdin=proc.stdout, stdout=sp.PIPE, shell=True) # grep for video files
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
            " -metadata album={} -metadata genre={} -b:a 192K -vn {}.mp3".format(