#!/bin/bash

music=$HOME/Music
TMP_FILE=/tmp/ytdl
DLFLAGS="-r 25.5M -f 22 -o $TMP_FILE/%(title)s.%(ext)s" # -r downlaod reate -f quality of dl
log=0

# Function to show status indecator
status_ind ()
{
    while kill -0 $1 2> /dev/null; do
        printf "."
        sleep 1
    done
}

# Function for removing tmp files and folders
clean_up ()
{
    if [ -e "$TMP_FILE" ]; then rm -r "$TMP_FILE"; fi
    if [ -e output.jpg ]; then rm output.jpg; fi  # album art file made by alb_add.py
}

# Runs update by giting leatest version and running install.sh
update ()
{
    git clone https://github.com/Tristan2252/yt2mp3 $TMP_FILE
    
    # Linux should update youtube-dl as well, installer will detect that its not installed
    if [ "$(uname -s)" == "Linux" ]; then
        sudo rm -v /usr/bin/youtube-dl
        sudo rm -v /usr/local/bin/yt2mp3
        sudo rm -v /usr/local/bin/alb_add
    elif [ "$(uname -s)" == "Darwin" ]; then
        # youtube-dl is managed by brew in os X
        rm -v /usr/local/bin/yt2mp3
        rm -v /usr/local/bin/alb_add
    fi
    
    $TMP_FILE/install.sh &> /dev/null
    sudo rm -r "$TMP_FILE"
    printf "\nUp to Date!\n\n"
}

# Help menu for users
usage ()
{
    printf "\nYt2mp3\n\n"

    printf "Git Repo:\n"
    printf "\thttps://github.com/Tristan2252/yt2mp3\n\n"

    printf "Download and convert from Youtube:\n"
    printf "\tyt2mp3 https://youtube.com/example\n\n"

    printf "Optional:\n"
    printf "\t-r   Remove temp file located in /tmp/yt2mp3\n"
    printf "\t-h   Help page for yt2mp3\n"
    printf "\t-u   Update current yt2mp3 program\n"
    printf "\t-t [00:00]   Change time in minutes that thumbnail is extracted from video\n\n"
   
    printf "In Program\n"
    printf "Adding Tags\n"
    printf "\t/back  use to redo the previously entered tags\n"
}

# get song info from usr
get_tags ()
{
    TAGS="Artist Song Album Album_Artist Genre"

    ext=1
    while [ $ext == 1 ]; do   
        printf "\n\n"
        for i in $TAGS; do
        
            echo -n "Enter $i: "
            read input
            
            if [ "$input" == "/back" ]; then
                break; # restart inner loop
            fi

            case $i in
                Artist)
                    artist=$input;;
                Song) 
                    title=$input;;
                Album)
                    album=$input;;
                Album_Artist)
                    alb_artist=$input;;
                Genre)
                    genre=$input
                    ext=0;; # set to 0 to break outer loop
            esac
        done
    done
}

get_thumbnail ()
{
        art_path="$TMP_FILE/output.jpg"
        printf "\nGetting video thumbnail."
        ffmpeg -loglevel $log -i "$1" -ss 00:$ftime.000 -vframes 1 $art_path >/dev/null &
        status_ind $! # pass in pid

        if [ ! -e $art_path ]; then
            printf "\nThumbnail not found, ffmpeg extraction faild!\n"
            printf "This may be due to incorrect time input\n"
            exit 2
        fi
}

####  DOWNLOAD ####
get_dl ()
{
    printf "\nDownloading from youtube, please wait."
    youtube-dl $DLFLAGS $1 >/dev/null &
    status_ind $! # pass in pid
}

# if command e arg exists set = to link
case $1 in
    -r)
         clean_up
         exit 0;;
    -u)
         # clean up if needed
         clean_up

         mkdir $TMP_FILE
         update
         exit 0;;
    -h)
         usage
         exit 0;;
    "")
        # while link is null
        while [ -z "$link" ]; do
            echo
            echo -n "Enter video link: "
            read link
            echo
        done;;
     *)
        link=$1;;
esac


# 2nd command line param
case $2 in
    -t)
        ftime=$3;;
esac


# if time is not set, set to default value
if [ -z "$ftime" ]; then
    ftime=00:10
fi


# tmp file to store download
mkdir "$TMP_FILE"
get_dl $link


# search any video format
# if video not found add .ext here
DL_FILE="$TMP_FILE/$(ls $TMP_FILE | grep '.wmv\|.avi\|.mp4\|.mkv')"

####  MP3 CONVERSION  ####
if [ ! -e "$DL_FILE" ]; then
    printf "\nNeed File to convert, \nMake sure that the download is working correctly...\n\n"
    exit 0
fi

get_tags # prompt user for tags
if [ "$title" == "" ]; then # if no title is entered the use file name
    title="$(ls $TMP_FILE | grep '.wmv\|.avi\|.mp4\|.mkv')"
    title="${title%.*}"
fi

# ffmpeg command for converting to mp3
printf "\nConverting download to MP3 and adding tags."
ffmpeg -loglevel $log -i "$DL_FILE" \
    -metadata title="$title" \
    -metadata artist="$artist" \
    -metadata album_artist="$alb_artist" \
    -metadata album="$album" \
    -metadata genre="$genre" \
        -b:a 192K -vn "$title.mp3" &

status_ind $! # pass in pid

# add album art
while [ 1 ]; do # prompt user until correct input
    printf "\n\nWould you like to use custom album art or video album art?\n"
    printf "[V] Video\n"
    printf "[C] Custom\n\n"
    echo -n "Option: "
    read opt

    # conv opt to lower case so that if upper is entered it still works
    if [ "$(echo "$opt" | awk '{print tolower($0)}')" == "c" ]; then
        echo -n "Enter custom album art path: "
        read -e art_path # custom .jpg path, -e enables tab complet :)
        break
    elif [ "$(echo "$opt" | awk '{print tolower($0)}')" == "v" ]; then
        get_thumbnail $DL_FILE
        break
    else
        printf "\n *** Invalid input: $opt ***\n"
        sleep 2
    fi
done

alb_add "$title.mp3" "$art_path" # add album art with python

printf "\nYour song $title is located at $(pwd)\n"
while [ 1 ]; do
    echo -n "Would you like to move it to $music [Y/N]: "
    read opt
    if [ "$(echo "$opt" | awk '{print tolower($0)}')" == "y" ]; then
            mv "$title.mp3" "$music"
            printf "$title moved to $music\n"
            break
    elif [ "$(echo "$opt" | awk '{print tolower($0)}')" == "n" ]; then
            break
    else
            printf "Enter Y or N as an option\n"
    fi
done

echo

# cleaning up
clean_up

exit 0
 
