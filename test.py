#!/usr/bin/env python3
import subprocess as sp
import string
import sys

def get_path(path):
    proc = sp.Popen("ls -t {}".format(path), stdout=sp.PIPE, shell=True) # ls temp dir by date
    grep_proc = sp.Popen("grep '.mkv\|.mp4\|.mp3'", stdin=proc.stdout, stdout=sp.PIPE, shell=True) # grep for video files
    head_proc = sp.Popen("head -1", stdin=grep_proc.stdout, stdout=sp.PIPE, shell=True) # narrow down to leatest file
    out = head_proc.communicate()[0]
    print(out)
    out = out.decode('utf8', errors='ignore') # convert to sting
    new_path = cvt_ascii(out)
    path += "/"
    print("mv {} {}".format(path + out, path + new_path))
    #sp.Popen("mv {} {}".format(out, new_path), stdout=sp.PIPE, shell=True)
    return "{}{}".format(path, parse_str(out)) # parse path before returning


def parse_str(string):
    path = string.replace(" ", "\ ")
    path = path.replace("(", "\(")
    path = path.replace(")", "\)")
    path = path.rstrip("\n") # remove newline
    return path


def cvt_ascii(string):
    ascii_str = ""
    for i in string:
        if ord(i) < 127 and ord(i) > 20:
            ascii_str += i
    
    print(ascii_str)
    return ascii_str


def main():
    
    string = get_path("/Users/tristan/Documents/test")
    print(string)

if __name__ == "__main__":
    main()
