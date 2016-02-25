#!/bin/bash

INSTALL_DIR="/usr/local/bin"
BASEDIR="$(dirname $0)" # dir of install.sh

# MAC OS test dir's
HOMEBREW_MOS="/usr/local/bin/brew"
EYED3_MOS="/usr/local/lib/python2.7/site-packages/eyed3"
PYTHON_MOS="/usr/local/lib/python2.7"
FFMPEG_MOS="/usr/local/bin/ffmpeg"
YOUTUBE_MOS="/usr/local/bin/youtube-dl"

# LINUX test dir's
YOUTUBE_LIN="/usr/bin/youtube-dl"
EYED3_LIN="/usr/local/lib/python2.7/dist-packages/eyed3"
FFMPEG_LIN="/usr/bin/ffmpeg"
PYTHON_LIN="/usr/bin/python2.7"
PIP_LIN="/usr/bin/pip3"

# Installes yt2mp3 by copying alb_add and yt2mp3 to install dir and
# making exacutable
yt2mp3_install ()
{
    echo # for clean output 
    if [ "$1" == "Linux" ]; then
        sudo cp -v $BASEDIR/yt2mp3.sh $INSTALL_DIR/yt2mp3 # copy bash script to bin
        sudo chmod +x $INSTALL_DIR/yt2mp3
        sudo cp -v $BASEDIR/alb_add.py $INSTALL_DIR/alb_add
        sudo chmod +x $INSTALL_DIR/alb_add

    elif [ "$1" == "Darwin" ]; then
        cp -v $BASEDIR/yt2mp3.sh $INSTALL_DIR/yt2mp3 # copy bash script to bin
        chmod +x $INSTALL_DIR/yt2mp3
        cp -v $BASEDIR/alb_add.py $INSTALL_DIR/alb_add
        chmod +x $INSTALL_DIR/alb_add
    fi
    echo # for clean output 
    
    # check if installed correctly
    if [ -e $INSTALL_DIR/alb_add ]; then
        printf "alb_add installed\n"
    fi
    if [ -e $INSTALL_DIR/yt2mp3 ]; then
        printf "Yt2mp3 installed\n"
    fi
}

# HomeBrew installer for Mac OS
hb_install ()
{
    if [ -e $HOMEBREW_MOS ]; then
            return 
    fi

    while [ 1 ]; do
        echo -n "Homebrew is needed to run installer, would you like to install it [Y/N]: "
        read opt
        if [ $opt == "N" ]; then
            exit 0
        elif [ $opt == "Y" ]; then
            ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
            printf "\n\nHomebrew Installed\n"
            printf "Learn more about homebrew at: \n" # tell user about homebrew if they dont know
            printf "https://github.com/Homebrew/homebrew/tree/master/share/doc/homebrew#readme\n\n"
            break
        else
            printf "\n\n**** Invalid Input: $opt ****"
        fi
    done
}

# Youtube-dl install, manual install used for linux to get
# the latest version (older version has a bug)
youtube_install ()
{
    if ! [ -e $YOUTUBE_MOS ] && ! [ -e $YOUTUBE_LIN ]; then
        printf "installing youtube-dl...\n"
        if [ "$1" == "Linux" ]; then
            sudo wget https://yt-dl.org/latest/youtube-dl -O /usr/local/bin/youtube-dl
            sudo chmod a+x /usr/local/bin/youtube-dl
            hash -r
        elif [ "$1" == "Darwin" ]; then
            brew install youtube-dl
        fi
    fi
    printf "youtube-dl installed\n"
}

# Installes eyed3 python modual for alb_add script
eyed3_install ()
{
    if ! [ -e $EYED3_MOS ] && ! [ -e $EYED3_LIN ]; then
        printf "installing eyeD3...\n"
        if [ "$1" == "Linux" ]; then
            sudo pip install eyeD3
        elif [ "$1" == "Darwin" ]; then
            pip2.7 install eyed3
        fi
    fi
    printf "eyeD3 installed\n"
}

# ffmpeg installer 
ffmpeg_install ()
{
    if ! [ -e $FFMPEG_MOS ] && ! [ -e $FFMPEG_LIN ]; then
        printf "installing ffmpeg...\n"
        if [ "$1" == "Linux" ]; then
            sudo apt-get install ffmpeg -y
        elif [ "$1" == "Darwin" ]; then
            brew install ffmpeg
        fi
    fi
    printf "ffmpeg installed\n"
}

# Python installer, installes python as well as pip for 
# linux.
python_install ()
{
    if ! [ -e $PYTHON_MOS ] && ! [ -e $PYTHON_LIN ]; then
        printf "installing python...\n"
        if [ "$1" == "Linux" ]; then
            sudo apt-get install python -y
        elif [ "$1" == "Darwin" ]; then
            brew install python
        fi
    fi
    
    if [ "$1" == "Linux" ]; then
        if ! [ -e $PIP_LIN ]; then
            sudo apt-get install python-pip -y
        fi
    fi
    printf "python installed\n"
}

# Determine the os
if [ $(uname -s) == "Darwin" ]; then
    os="Darwin"
    hb_install # only for mac os
elif [ $(uname -s) == "Linux" ]; then
    os="Linux"
fi

python_install $os # python install must be before eyed3

eyed3_install $os

ffmpeg_install $os

youtube_install $os

yt2mp3_install $os
printf "\nInstallation files no loager needed be sure to remove\n"
printf "them after installation is done\n"

#ppa:mc3man/trusty-media
