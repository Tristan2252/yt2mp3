#!/bin/bash

tmp_file=/tmp/ytdl
dl_quality="22"
log=0 # amout of output for ffmpeg, check man page for more info

# Function to show status indecator
status_ind (){
	while kill -0 $1 2> /dev/null; do
		printf "."
		sleep 1
	done
}

# if command line arg exists set = to link
if [ $1 ]; then
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

mkdir "$tmp_file" # tmp file to store download
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
echo -n "Enter Genre: "
read genre

# ffmpeg command for converting to mp3
printf "\nConverting download to MP3 and adding tags."
ffmpeg -loglevel $log -i "$file" \
	-metadata title="$title" \
	-metadata artist="$artist" \
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
			
python2.7 alb_add.py "$title.mp3" "$art_path" # add album art with python

# cleaning up
rm -r "$tmp_file"
if [ -e output.jpg ]; then rm output.jpg; fi  # album art file made by alb_add.py

exit 0
 
