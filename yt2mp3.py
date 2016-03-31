import sys, getopt
import subprocess as sp
import time
import os

"""
To change the folder where yt2mp3 stores temp data such as the downloaded mp4 or
output.jpg (album art) as well as any other logs for debuging
"""
DOWNLOAD_PATH = "/tmp"

"""
Update command string for youtube-dl, should NOT be changed unless the update command
incorrect on has changed
"""
UPDATE_CMD = 'sudo curl https://yt-dl.org/downloads/2016.03.06/youtube-dl -o /usr/local/bin/youtube-dl; sudo chmod a+rx /usr/local/bin/youtube-dl'

"""ffmpeg binary uses to call ffmpeg when bash string command is called"""
FFMPEG_BIN ='ffmpeg'


def yt2mp3(url):

        bash_call('youtube-dl -r 25.5M -f 22 -o "{}/%(title)s.%(ext)s" {}'.format(DOWNLOAD_PATH, url))
        file_path = get_path()

        print("\nGetting Album Art")
        get_frame(file_path)

        song_tags = get_tags()
        new_file_name = song_tags["song"] + ".mp3"
        print("\nSetting Song Tags")
        set_tags(song_tags, file_path)

        print("\nSetting Album Art")
        set_art(new_file_name)


"""
Get a frame from downloaded video to add as the album art. Function calles ffmpeg bash command
with flags to extract a picture, output.jpg, from video and store in the temp file.
vid_path: The found path of the downloaded video, see get_path() for more details
vid_time: The time ffmpeg is to grab a video frame from
return: None
"""
def get_frame(vid_path, vid_time='00:00:10.000'):
    output_path = "{}/output.jpg".format(DOWNLOAD_PATH)

    if not check_file(output_path):
        print("Removing old temp files", end="")
        bash_call("rm {}".format(output_path))

    command = '{} -i {} -ss {} -vframes 1 {}'.format(FFMPEG_BIN, vid_path, vid_time, output_path)
    bash_call(command)


"""
Finds the absolute path of the downloaded file in the temp folder using ls and piping output to
grep to search for an mkv or mp4 file. The stdout of grep is then piped to head to make sure to 
get the latest file in the temp folder. After file is found the output is captured by python and 
set to out var to them be processed into a readable string using parce_str function.(see parce_str) for info
return: absolute path string of downloaded file
"""
def get_path():
    proc = sp.Popen("ls -t {}".format(DOWNLOAD_PATH), stdout=sp.PIPE, shell=True) # ls temp dir by date
    grep_proc = sp.Popen("grep '.mkv\|.mp4'", stdin=proc.stdout, stdout=sp.PIPE, shell=True) # grep for video files
    head_proc = sp.Popen("head -1", stdin=grep_proc.stdout, stdout=sp.PIPE, shell=True) # narrow down to leatest file
    out = head_proc.communicate()[0]
    out = out.decode('ascii') # convert to sting
    return "{}/{}".format(DOWNLOAD_PATH, parce_str(out)) # parce path before returning


"""
Prompts user for metadata and stores values in a dictionary for easy passing from function to function.
return: a dictionary of the tags and their values
"""
def get_tags():
    artist = input("Enter Artist: ")
    song = input("Enter Song Name: ")
    album = input("Enter Album Name: ")
    alb_artist = input("Enter Album Artist: ")
    genre = input("Enter Genre: ")

    tags = {"artist": artist, "song": song, "album": album, "alb_artist": alb_artist, "genre": genre}
    for key in tags:
        tags[key] = parce_str(tags[key])

    return tags


"""
Builds bash command to call ffmpeg and set metadata of the file. The tag dictionary is used to
imput user entered data into the command string before it is called using bash_call() to run the command
tag_lst: a dictionary of the user entered tags
file_path: the absolute path of the files to set metadata for
return: none
"""
def set_tags(tag_lst, file_path):
    cmd = "ffmpeg -i {} -metadata title={} -metadata artist={} -metadata album_artist={}"\
            " -metadata album={} -metadata genre={} -b:a 192K -vn {}.mp3".format(file_path,
                    tag_lst["song"],
                    tag_lst["artist"],
                    tag_lst["alb_artist"],
                    tag_lst["album"],
                    tag_lst["genre"],
                    tag_lst["song"])

    bash_call(cmd)


"""
Prompt user for option to use a custom album art or on grabed from get_frame(). If the user
enters the custom option then they will asked to enter the absolute path of the custom album art.
the users input is then parced for readability and then passes via bash to alb_add.py. If user
enters video option the path of output.jpg crated by get_frame() is passed to alb_add via bash.
NOTE: The paths are passed to alb_add.py via bash because alb_add.py runs on python2.7 becasue of eyed3
file_path: path of the file to add album art to
return: none
"""
def set_art(file_path):
    print("Use custom album art or keep videos?")
    print("\tV: keep video album art")
    print("\tC: use custom")
    opt = input("Option: ")

    if opt == 'V' or opt.lower() == 'v':
        bash_call("alb_add {} {}/output.jpg".format(file_path, DOWNLOAD_PATH))

    else:
        art_path = input("Enter path of custom album art: ")
        art_path = parce_str(art_path)
        bash_call("alb_add {} {}".format(file_path, art_path))


"""
Parces string to be readable by bash. Uses replace to switch patters such as ' ' with
bash space '\ '. This is done to enable path to be read correctly by bash when it is
passed to bash_call() to call the command string
string: the string to parce
"""
def parce_str(string):
    path = string.replace(" ", "\ ")
    path = path.replace("(", "\(")
    path = path.replace(")", "\)")
    path = path.rstrip("\n") # remove newline
    return path

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
            proc = sp.Popen(cmd, stdout=sp.PIPE, shell=True, stderr=sp.PIPE)
            status(proc)
            proc.wait() # wait just in case
        except KeyboardInterrupt:
            print("\n\nProgram Stopped: BY USER\n")
            sys.exit(2)

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
    for string in strings:

        if len(string) < len("http://www.youtube.com"): # if less then len of a link the not a link
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
    
    return False


def main():
    print("")
    print("\t\t###########################")
    print("\t\t#### -- Yt2mp3 BETA -- ####")
    print("\t\t###########################")
    print("")

    flags = sys.argv[1:]
    if not flags:
        flags = [input("Enter video url: ")] # flags needs to be a list to be read correctly
    
    global verbose # global so that it doesnt need to be passed to every function
    if '-v' in flags:
        verbose = 1
    else:
        verbose = 0


    link = check_url(flags)

    if link:
        yt2mp3(link)
    else:
        while link == 0: # until url is correct ask user
            link = input("Enter video url: ")
        yt2mp3(link)


    for opt in flags: # loop through opts and args
        if opt == '-u':
            bash_call(UPDATE_CMD)
        if opt == '-f':
            file_path = input("enter file path: ")
            get_frame(file_path)

if __name__ == "__main__":
    main()
