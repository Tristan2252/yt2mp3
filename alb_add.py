#!/usr/bin/env python

import os.path as path
import eyed3
import sys

"""
Funcint uses os.path to check if file exists
returns 0 if file found and 1 if not
:param file_name: the path of the file to test
:return 0 if found and 1 if not
"""
def check_file(file_name):
    if path.isfile(file_name):
        return 0
    else:
        print "{} is not a file or was not found".format(file_name)
        return 1

"""
Help page function, prings help page for user to see
correct input syntax
"""
def help_page():
    print "\nAlb_add\n"
    print "To add album art to .mp3 use:"
    print "\t$ alb_add /path/to/song.mp3 /path/to/art.jpg\n"

"""
Parces path inputed by user and converts it into an acceptable
path for python to use
:param path: the path to parce
:reurn new_str: the converted path
"""
def parce_path(path):
    cnt = 0 # index counter
    new_str = "" # empty string to append to

   # remove potential space at end of path
    if path[-1] == " ": 
        path = path[:-1]

    for i in path:
        if (cnt == 0) & (i == "'"): # remove single quotes if fount at index 0
            pass
        elif (cnt == len(path) - 1) & (i == "'"): # remove single quotes at end of path
            pass
        elif path[cnt:cnt+2] == "\ ":
            # remove bash space special character
            pass
        else:
            new_str += i
        cnt += 1

    return new_str

def main():
    
    try:
        filename = parce_path(sys.argv[1]) # arg 1 sould be filename
        art = parce_path(sys.argv[2]) # arg 2 will be the picture to add 
    except IndexError:
        help_page()
        return 3

    while check_file(filename):
        in_put = raw_input("Enter valid file path for mp3: ")
        filename = parce_path(in_put) # convert to acceptable path

    while check_file(art):
        in_put = raw_input("Enter valid path to art: ")
        art = parce_path(in_put)
    
    while ".mp3" not in filename:
        print "Song must be of format .jpg"
        in_put = raw_input("Enter a .mp3 file: ")
        filename = parce_path(in_put)
    
    while ".jpg" not in art: # if file not .jpg ask for .jpg
        print "Art must be of format .jpg"
        in_put = raw_input("Enter a .jpg file: ")
        art = parce_path(in_put)

    imagedata = open(art, "rb").read() # open image

    audiofile = eyed3.load(filename) # load image into eyed3
    audiofile.tag.images.set(3, imagedata, "image/jpeg", u" ")
    audiofile.tag.save()
    print "\n\nAdded {} to {} as album conver!\n".format(art, filename)

if __name__ == "__main__":
    main()
    
