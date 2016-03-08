import sys, getopt
import cv2
import os

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


def get_frame(vid_path, vid_time=12000):
    vid_pic = cv2.VideoCapture(vid_path) 
    vid_pic.set(cv2.CAP_PROP_POS_MSEC, vid_time) # video time to capture from

    pic = vidcap.read()
    if pic: # if read was successful the write to file
        cv2.imwrite("thumbnail.jpg", pic)
    else:
        print("Error: get_frame: READ ERROR")
        print("Input Path: {}".format(path))


# use os.path to check if file exists or not
def check_file(path):
    if os.path.isfile(path):
        pass
    else:
        print("Error: check_file: FILE NOT FOUND")


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:u")
    except getopt.GetoptError as err:
        print("Error")

    for opt, arg in opts: # loop through opts and args
        if opt == "-u":
            update_yt()
        elif opt == "-f":
            check_file(arg) # check if file exists
            get_frame(arg)
        else:
            print("Error: main: NOT A VALID OPTION")

if __name__ == "__main__":
    main()
