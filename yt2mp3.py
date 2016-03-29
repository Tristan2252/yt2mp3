import sys, getopt
import subprocess as sp
import os

STATUS_FLAGS='& while kill -0 $! 2> /dev/null; do printf "."; sleep 1; done'
OUTPUT_FLAGS='> /dev/null'
FFMPEG_BIN ='ffmpeg'

# Update youtube-dl for unix based systems by downloding current
# version and makeing exe
def update_yt():
    update_cmd = 'sudo curl https://yt-dl.org/downloads/2016.03.06/youtube-dl -o /usr/local/bin/youtube-dl'
    cmd = os.popen(update_cmd, "r") # run update bash command
    
    # print output to the user
    while 1:
        line = cmd.readline() 
        if not line:
            break
        print("{}".format(line))

    # makeing exe
    chmod_cmd = 'sudo chmod a+rx /usr/local/bin/youtube-dl'
    cmd = os.popen(chmod_cmd, "r")

    while 1:
        line = cmd.readline() 
        if not line:
            break
        print("{}".format(line))


def get_frame(vid_path, vid_time='00:00:10.000'):
    
    command = "{} -i {} -ss {} -vframes 1 output.jpg {} {}".format(FFMPEG_BIN, vid_path, vid_time,OUTPUT_FLAGS, STATUS_FLAGS)
    sp.call(command, shell=True)

def ytdl(url):

    #try:
    command = "youtube-dl {} {} {}".format(url, OUTPUT_FLAGS, STATUS_FLAGS)
    sp.call(command, shell=True)
    #except KeyboardInterrupt:
    #    sys.exit()

# use os.path to check if file exists or not
def check_file(path):
    if os.path.isfile(path):
        return 0
    else:
        print("Error: check_file: FILE NOT FOUND")
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

    if '-v' in flags:
        OUTPUT_FLAGS = ''

    url = check_url(flags)
    if url:
        ytdl(url)

    for opt, arg in opts: # loop through opts and args
        if opt == '-u':
            update_yt()
        if opt == '-f':
            file_path = arg.replace(" ", "\ ") # FFMPEG runs through bash witch needs '\ ' as a space
            get_frame(file_path)

    return
    print("Error: main: NOT A VALID OPTION")

if __name__ == "__main__":
    main()
