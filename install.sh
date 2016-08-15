#!/bin/bash

INSTALL_DIR="/opt/yt2mp3/"
BIN_DIR="/usr/local/bin"

YOUTUBE_DL="/usr/local/bin/youtube-dl"

# Mac OS test dir'
HOMEBREW_MOS="/usr/local/bin/brew"
EYED3_MOS="/usr/local/lib/python2.7/site-packages/eyed3"
PYTHON_MOS="/usr/local/lib/python2.7"
PYTHON3_MOS="/usr/local/lib/python3.5"
FFMPEG_MOS="/usr/local/bin/ffmpeg"

# LINUX test dir's
EYED3_LIN="/usr/local/lib/python2.7/dist-packages/eyed3"
FFMPEG_LIN="/usr/bin/ffmpeg"
PYTHON3_LIN="/usr/bin/python3.4"
PYTHON_LIN="/usr/bin/python2.7"
PIP_LIN="/usr/bin/pip3"

install ()
{
    case $1 in
        $HOMEBREW_MOS)
            printf "\n###### INSTALLING HOMEBREW ######\n\n"
            /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)";;
        $EYED3_LIN)
            printf "\n###### INSTALLING EYED3 ######\n\n"
            sudo pip install eyeD3;;
        $EYED3_MOS)
            printf "\n###### INSTALLING EYED3 ######\n\n"
            sudo pip2.7 install eyed3;;
        $PYTHON_LIN)
            printf "\n###### installing python ######\n\n"
            sudo apt-get install python -y;;
        $PIP_LIN)
            printf "\n###### installing python ######\n\n"
            sudo apt-get install python-pip -y;;
        $PYTHON_MOS)
            printf "\n###### INSTALLING PYTHON ######\n\n"
            brew install python;;
        $PYTHON3_LIN)
            printf "\n###### INSTALLING PYTHON3 ######\n\n"
            sudo apt-get install python3 -y;;
        $PYTHON3_MOS)
            printf "\n###### INSTALLING PYTHON3 ######\n\n"
            brew install python3;;
        $FFMPEG_LIN)
            printf "\n###### INSTALLING FFMPEG ######\n\n"
            sudo apt-get install ffmpeg -y;;
        $FFMPEG_MOS)
            printf "\n###### INSTALLING FFMPEG ######\n\n"
            brew install ffmpeg;;
        $YOUTUBE_DL)
            printf "\n###### INSTALLING YOUTUBE ######\n\n"
            sudo curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl
            sudo chmod a+rx /usr/local/bin/youtube-dl;;
        $BIN_DIR/alb_add)
            printf "\n###### INSTALLING ALB_ADD ######\n\n"
            sudo cp $(dirname $0)/alb_add.py $INSTALL_DIR
            sudo ln -sF $INSTALL_DIR/alb_add.py $BIN_DIR/alb_add
            sudo chmod +x $1;;
        $BIN_DIR/yt2mp3)
            printf "\n###### INSTALLING YT2MP3 ######\n\n"
            sudo cp $(dirname $0)/yt2mp3.py $INSTALL_DIR
            sudo ln -sF $INSTALL_DIR/yt2mp3.py $BIN_DIR/yt2mp3
            sudo chmod +x $1;;
    esac
    check_error $1 # check if installed correctly
}

check_error ()
{
    if [ ! -e $1 ]; then
            printf "Unable to install $1, check installation for errors\n\n"
            exit 0
    fi
}

check_file ()
{
    if [ -e $1 ]; then
        printf "Installed... \t$1\n"
    else
        install $1
    fi
}


mac_install ()
{
    check_file $HOMEBREW_MOS
    check_file $PYTHON_MOS
    check_file $PYTHON3_MOS
    check_file $EYED3_MOS
    check_file $FFMPEG_MOS
    check_file $YOUTUBE_DL
    
    install $BIN_DIR/alb_add
    check_file $BIN_DIR/alb_add

    install $BIN_DIR/yt2mp3
    check_file $BIN_DIR/yt2mp3
}

linux_install ()
{
    check_file $PYTHON_LIN
    check_file $PYTHON3_LIN
    check_file $PIP_LIN
    check_file $EYED3_LIN
    check_file $FFMPEG_LIN
    check_file $YOUTUBE_DL

    install $BIN_DIR/alb_add
    check_file $BIN_DIR/alb_add

    install $BIN_DIR/yt2mp3
    check_file $BIN_DIR/yt2mp3
}

# Create installation dir
sudo mkdir -p $INSTALL_DIR

# Determine the os
if [ $(uname -s) == "Darwin" ]; then
    mac_install
elif [ $(uname -s) == "Linux" ]; then
    linux_install
fi


