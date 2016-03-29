import sys, getopt
import subprocess as sp
import time
import os

UPDATE_CMD = 'sudo curl https://yt-dl.org/downloads/2016.03.06/youtube-dl -o /usr/local/bin/youtube-dl; sudo chmod a+rx /usr/local/bin/youtube-dl'
DOWNLOAD_PATH = "/tmp"
FFMPEG_BIN ='ffmpeg'

def get_frame(vid_path, verbose, vid_time='00:00:10.000'):
    output_path = "{}/output.jpg".format(DOWNLOAD_PATH)

    if not check_file(output_path):
        bash_call("rm {}".format(output_path), verbose)

    command = "{} -i {} -ss {} -vframes 1 {}".format(FFMPEG_BIN, vid_path, vid_time, output_path)
    bash_call(command, verbose)

def get_path():
    proc = sp.Popen("ls " + DOWNLOAD_PATH, stdout=sp.PIPE, shell=True) # pipe stdout to proc
    grep_proc = sp.Popen("grep .mkv\|.mp4".split(), stdin=proc.stdout, stdout=sp.PIPE) # pipe proc.stdout to grep
    out = grep_proc.communicate()[0]
    out = out.decode('ascii') # convert to sting
    out = out.rstrip("\n") # remove newline
    return "{}/{}".format(DOWNLOAD_PATH, out.replace(" ", "\ "))

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

    #proc.communicate()[0] # allow for ctl-c and print stderr
        
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

    for opt, arg in opts: # loop through opts and args
        if opt == '-u':
            bash_call(UPDATE_CMD)
        if opt == '-f':
            get_frame(file_path)

    print("")

if __name__ == "__main__":
    main()
