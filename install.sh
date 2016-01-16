#!/bin/bash

INSTALL_DIR="/usr/local/bin"


EYED3="/usr/local/lib/python2.7/site-packages/eyed3"
FFMPEG="/usr/local/bin/ffmpeg"
PYTHON="/usr/bin/python2.7"

yt2mp3_install ()
{
	cp yt2mp3.sh $INSTALL_DIR/yt2mp3 # copy bash script to bin

	# if system has other python versions and user wants it installed there,
	# then change the path below
	python_dir="/usr/local/lib/python2.7/site-packages/yt2mp3"
	mkdir $python_dir
	cp alb_add.py $python_dir
	
	if [ -e $python_dir/alb_add.py ]; then
		printf "alb_add installed\n"
	fi
	if [ -e $INSTALL_DIR/yt2mp3 ]; then
		printf "Yt2mp3 installed\n"
	fi
}

hb_install ()
{
	while [ 1 ]; do
		echo -n "Homebrew is needed to run installer, would you like to install it [Y/N]: "
		read opt
		if [ $opt == "N" ]; then
			exit 0
		elif [ $opt == "Y" ]; then
			ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
			printf "\n\nHomebrew Installed\n"
			printf "Learn more about homebrew at: \n"
			printf "https://github.com/Homebrew/homebrew/tree/master/share/doc/homebrew#readme\n\n"
			break
		else
			printf "\n\n**** Invalid Input: $opt ****"
		fi
	done
}

eyed3_install ()
{
	brew install eyeD3
	if [ -e $EYED3 ]; then # make sure it installed
		printf "\nffmpeg missing or not installed correctly\n"
		exit 1
	fi
}

ffmpeg_install ()
{
	brew install ffmpeg
	if ! [ -e $FFMPEG ]; then # make sure it installed
		printf "\nffmpeg missing or not installed correctly\n"
		exit 1
	fi
}

python_install ()
{
	brew install python
	if ! [ -e  $PYTHON ]; then
		printf "\npython missing or not installed correctly\n"
		exit 1
	fi
}


darwin_install (){
	
	if ! [ -e $HOMEBREW ]; then
		hb_install
	fi
	printf "Homebrew installed\n"

	if ! [ -e $EYED3 ]; then
		eyed3_install
	fi
	printf "eyeD3 installed\n"

	if ! [ -e $FFMPEG ]; then
		ffmpeg_install
	fi
	printf "ffmpeg installed\n"

	if ! [ -e $PYTHON ]; then
		python_install
	fi
	printf "python2.7 installed\n"
	
	yt2mp3_install
}


# check what os is running
if [ $(uname -s) == "Darwin" ]; then
	darwin_install
	printf "\n\nInstall Finished!"
elif [ $(uname -s) == "Linux" ]; then
	echo
fi

#ppa:mc3man/trusty-media
