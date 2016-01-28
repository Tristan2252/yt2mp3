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

def make_path(path):
    if (path[1] & path[-1]) == "'":
        return path[1:-1]
    else:
        return path

def main():
    
    try:
        filename = str(sys.argv[1]) # arg 1 sould be filename
        art = str(sys.argv[2]) # arg 2 will be the picture to add 
    except IndexError:
        help_page()
        return 3

    while check_file(filename):
        in_put = raw_input("Enter valid file path for mp3: ")
        filename = make_path(in_put)

    while check_file(art):
        in_put = raw_input("Enter valid path to art: ")
        art = make_path(in_put)
    
    while ".mp3" not in filename: # if file not .jpg ask for .jpg
        print "Song must be of format .jpg"
        filename = raw_input("Enter a .mp3 file: ")
    
    while ".jpg" not in art: # if file not .jpg ask for .jpg
        print "Art must be of format .jpg"
        art = raw_input("Enter a .jpg file: ")

    imagedata = open(art, "rb").read() # open image

    audiofile = eyed3.load(filename)
    audiofile.tag.images.set(3, imagedata, "image/jpeg", u" ")
    audiofile.tag.save()
    print "\n\nAdded {} to {} as album conver!\n".format(art, filename)

if __name__ == "__main__":
    main()
