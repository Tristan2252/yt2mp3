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

def help_page():
    print "\nAlb_add\n"
    print "To add album art to .mp3 use:"
    print "\t alb_add /path/to/song.mp3 /path/to/art.jpg\n"

def parce_path(path):
    cnt = 0
    new_str = ""

    if path[-1] == " ":
        path = path[:-1]

    for i in path:
        if (cnt == 0) & (i == "'"):
            pass
        elif (cnt == len(path) - 1) & (i == "'"):
            pass
        elif path[cnt:cnt+2] == "\ ":
            pass
        else:
            new_str += i
        cnt += 1

    return new_str

def main():
    
    try:
        filename = str(sys.argv[1]) # arg 1 sould be filename
        art = str(sys.argv[2]) # arg 2 will be the picture to add 
    except IndexError:
        help_page()
        return 3

    while check_file(filename):
        in_put = raw_input("Enter valid file path for mp3: ")
        filename = parce_path(in_put)

    while check_file(art):
        in_put = raw_input("Enter valid path to art: ")
        art = parce_path(in_put)
    
    while ".mp3" not in filename: # if file not .jpg ask for .jpg
        print "Song must be of format .jpg"
        in_put = raw_input("Enter a .mp3 file: ")
        filename = parce_path(in_put)
    
    while ".jpg" not in art: # if file not .jpg ask for .jpg
        print "Art must be of format .jpg"
        in_put = raw_input("Enter a .jpg file: ")
        art = parce_path(in_put)

    imagedata = open(art, "rb").read() # open image

    audiofile = eyed3.load(filename)
    audiofile.tag.images.set(3, imagedata, "image/jpeg", u" ")
    audiofile.tag.save()
    print "\n\nAdded {} to {} as album conver!\n".format(art, filename)

if __name__ == "__main__":
    main()
    
