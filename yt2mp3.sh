#!/bin/bash

music=$HOME/Music
tmp_file=/tmp/ytdl
dl_quality="22"
log=0 # amout of output for ffmpeg, check man page for more info

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
    rm -r "$tmp_file"
    if [ -e output.jpg ]; then rm output.jpg; fi  # album art file made by alb_add.py
}

update ()
{
    git clone https://github.com/Tristan2252/yt2mp3 $tmp_file
    $tmp_file/install.sh &> /dev/null
    sudo rm -r "$tmp_file"
    printf "\nUp to Date!\n\n"
}

mkdir "$tmp_file" # tmp file to store download

# if command line arg exists set = to link
if [ "$1" == "-r" ]; then
    clean_up
    exit 0
elif [ "$1" == "-u" ]; then
    update
    exit 0
elif [ $1 ]; then
    link=$1
else
    while [ -z "$link" ]; do # while link is null
        echo
        echo -n "Enter video link: "
        read link
        echo
    done
fi

####  DOWNLOAD ####

printf "\nDownloading from youtube, please wait."
youtube-dl -f "$dl_quality" -o "$tmp_file/ytdl_out.%(ext)s" $link >/dev/null &
status_ind $! # pass in pid

# search any video format
file="$tmp_file/$(ls $tmp_file | grep '.wmv\|.avi\|.mp4\|.mkv')" # if video not found add .ext here



####  MP3 CONVERSION  ####

if ! [ -e $file ]; then
    printf "\nNeed File to convert, \nMake sure that the download is working correctly...\n\n"
    exit 0
fi

# get song info from usr
printf "\n\n"
echo -n "Enter artist name: "
read artist
echo -n "Enter Song Title: "
read title
echo -n "Enter Album name: "
read album
echo -n "Enter Album Artist name: "
read alb_artist
echo -n "Enter Genre: "
read genre

# ffmpeg command for converting to mp3
printf "\nConverting download to MP3 and adding tags."
ffmpeg -loglevel $log -i "$file" \
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
    if [ $opt == "C" ]; then
        echo -n "Enter custom album art path: "
        read -e art_path # custom .jpg path, -e enables tab complet :)
        break
    elif [ $opt == "V" ]; then
        art_path="output.jpg"
        printf "\nGetting video thumbnail."
        ffmpeg -loglevel $log -i $file -ss 00:00:14.000 -vframes 1 $art_path >/dev/null &
        status_ind $! # pass in pid
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
    if [ $opt == "Y" ]; then
            mv "$title.mp3" "$music"
            printf "$title moved to $music\n"
            break
    elif [ $opt == "N" ]; then
            break
    else
            printf "Enter Y or N as an option\n"
    fi
done

echo

# cleaning up

exit 0
 
