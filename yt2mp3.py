import sys, getopt
import subprocess as sp
import eyed3
import time
import os

UPDATE_CMD = 'sudo curl https://yt-dl.org/downloads/2016.03.06/youtube-dl -o /usr/local/bin/youtube-dl; sudo chmod a+rx /usr/local/bin/youtube-dl'
DOWNLOAD_PATH = "/tmp"
FFMPEG_BIN ='ffmpeg'

def get_frame(vid_path, verbose, vid_time='00:00:10.000'):
    output_path = "{}/output.jpg".format(DOWNLOAD_PATH)

    if not check_file(output_path):
        bash_call("rm {}".format(output_path), verbose)

    command = '{} -i {} -ss {} -vframes 1 {}'.format(FFMPEG_BIN, vid_path, vid_time, output_path)
    bash_call(command, verbose)

def get_path():
    proc = sp.Popen("ls " + DOWNLOAD_PATH, stdout=sp.PIPE, shell=True) # pipe stdout to proc
    grep_proc = sp.Popen("grep .mkv\|.mp4".split(), stdin=proc.stdout, stdout=sp.PIPE) # pipe proc.stdout to grep
    out = grep_proc.communicate()[0]
    #out = out.decode('ascii') # convert to sting
    return "{}/{}".format(DOWNLOAD_PATH, parce_path(out))

def get_tags():
    artist = input("Enter Artist: ")
    song = input("Enter Song Name: ")
    album = input("Enter Album Name: ")
    alb_artist = input("Enter Album Artist: ")
    genre = input("Enter Genre: ")

    tags = {"artist": artist, "song": song, "album": album, "alb_artist": alb_artist, "genre": genre}
    return tags

def set_tags(tag_lst, file_path, verbose):
    cmd = "ffmpeg -i {} -metadata title={} -metadata artist={} -metadata album_artist={}"\
            " -metadata album={} -metadata genre={} -b:a 192K -vn {}.mp3".format(file_path,
                    tag_lst["song"],
                    tag_lst["artist"],
                    tag_lst["alb_artist"],
                    tag_lst["album"],
                    tag_lst["genre"],
                    tag_lst["song"])

    bash_call(cmd, verbose)

def set_art(file_path, verbose):
    bash_call("alb_add {} {}/output.jpg".format(file_path, DOWNLOAD_PATH), verbose)

def parce_path(string):
    path = string.decode('ascii')
    path = path.replace(" ", "\ ")
    path = path.replace("(", "\(")
    path = path.replace(")", "\)")
    path = path.rstrip("\n") # remove newline
    return path

def bash_call(cmd, verbose):
    if verbose:
        print(cmd)
        try:
            proc = sp.Popen(cmd, shell=True)
            proc.wait()
        except KeyboardInterrupt:
            print("\nProgram Stopped: BY USER")
            return 1

    else:
        try:
            proc = sp.Popen(cmd, stdout=sp.PIPE, shell=True, stderr=sp.PIPE)
            status(proc)
        except KeyboardInterrupt:
            print("\nProgram Stopped: BY USER")
            return 1

def status(p):
    while True:
        if p.poll() != None:
            break
        print('.', end="", flush=True) # print status
        time.sleep(1)
    print("") # extra print line becase of no \n after previous print

# use os.path to check if file exists or not
def check_file(path):
    if os.path.isfile(path):
        return 0
    else:
        return 1


def check_url(strings):
    url_str = ""
    for i, string in enumerate(strings):
        for letter in string:
                url_str += str(letter)
                if url_str == "https://www.youtube.com/":
                    print(string)
                    return string
                if url_str == "http://www.youtube.com/":
                    print(string)
                    return string
    return False


def main():
    try:
        flags = sys.argv[1:]
        opts, args = getopt.getopt(flags, "f:u")
    except getopt.GetoptError as err:
        print("Error")

    verbose = 0
    if '-v' in flags:
        verbose = 1

    url = check_url(flags)
    if url:
        bash_call('youtube-dl -r 25.5M -f 22 -o "{}/%(title)s.%(ext)s" {}'.format(DOWNLOAD_PATH, url), verbose)
        file_path = get_path()

        print("\nGetting Album Art")
        get_frame(file_path, verbose)
        
        song_tags = get_tags()
        print("\nSetting Song Tags")
        set_tags(song_tags, file_path, verbose)
        print("\nSetting Album Art")
        set_art("Test.mp3", verbose)

        for opt, arg in opts: # loop through opts and args
            if opt == '-u':
                bash_call(UPDATE_CMD)
            if opt == '-f':
                file_path = input("enter file path: ")
                get_frame(file_path, verbose)

        print("")

if __name__ == "__main__":
    main()
    
