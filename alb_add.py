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
        print "{} file not found".format(file_name)
        return 1


def main():
    filename = str(sys.argv[1]) # arg 1 sould be filename
    if not filename:
        print "Please use first argument as file name"
        return 3

    if ".jpg" not in str(sys.argv[2]): # if file not .jpg ask for .jpg
        art = input("Enter a .jpg file: ")
    else:
        art = str(sys.argv[2]) # arg 2 will be the picture to add 
    
    if not art:
        print "Please use second argument as .jpg file name"
        return 3

    check_file(filename)
    check_file(art)

    imagedata = open(art, "rb").read() # open image

    audiofile = eyed3.load(filename)
    audiofile.tag.images.set(3, imagedata, "image/jpeg", u" ")
    audiofile.tag.save()
    print "\n\nAdded {} to {} as album conver!\n".format(art, filename)

if __name__ == "__main__":
    main()
