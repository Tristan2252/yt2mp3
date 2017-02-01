#!/bin/bash

# globals 
BIN_DIR="/usr/local/bin"
INSTALL_DIR="/opt/yt2mp3"
YOUTUBE_DL="/usr/local/bin/youtube-dl"

install ()
{
    case $1 in

        # Mac OS installs
        $HOMEBREW_MOS)
            printf "\n###### INSTALLING HOMEBREW ######\n\n"
            /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)";;
        $PYTHON3_MOS)
            printf "\n###### INSTALLING PYTHON3 ######\n\n"
            brew install python3;;
        $FFMPEG_MOS)
            printf "\n###### INSTALLING FFMPEG ######\n\n"
            brew install ffmpeg;;

        # Linux  installs
        $PYTHON3_LIN)
            printf "\n###### INSTALLING PYTHON3 ######\n\n"
            sudo apt-get install python3 -y;;
        $PYTHON2_LIN)
            printf "\n###### INSTALLING PYTHON3 ######\n\n"
            sudo apt-get install python -y;;
        $PIP3_LIN)
            printf "\n###### INSTALLING PIP3 ######\n\n"
            sudo apt-get install python3-pip -y;;
        $FFMPEG_LIN)
            printf "\n###### INSTALLING FFMPEG ######\n\n"
            
            # add repo for trusty
            if [ $(lsb_release -c | awk {'print $2'}) == "trusty" ]; then
                sudo add-apt-repository ppa:mc3man/trusty-media -y
            fi

            sudo apt-get update
            sudo apt-get install ffmpeg -y;;


        # General Installs
        $MUTAGEN)
            printf "\n###### INSTALLING MUTAGEN ######\n\n"
            sudo pip3 install mutagen;;
        $YOUTUBE_DL)
            printf "\n###### INSTALLING YOUTUBE ######\n\n"
            sudo curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl
            sudo chmod a+rx /usr/local/bin/youtube-dl;;
        $BIN_DIR/yt2mp3)
            sudo cp $(dirname $0)/yt2mp3.py $INSTALL_DIR # always cp for updates to src

            if [ ! -e $BIN_DIR/yt2mp3 ]; then
                printf "\n###### INSTALLING YT2MP3 ######\n\n"
                sudo ln -s $INSTALL_DIR/yt2mp3.py $BIN_DIR/yt2mp3
                sudo chmod +x $BIN_DIR/yt2mp3
            fi
            ;;
    esac
    check_error $1 # check if installed correctly
}

check_error ()
{
    if [ ! -e $1 ]; then
            printf "Unable to install $1, check installation for errors\n\n"
            exit -1
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
    # Mac OS test dir'
    HOMEBREW_MOS="/usr/local/bin/brew"
    PYTHON3_MOS="/usr/local/lib/python3.5"
    FFMPEG_MOS="/usr/local/bin/ffmpeg"
    MUTAGEN="/usr/local/lib/python3.6/site-packages/mutagen"

    check_file $HOMEBREW_MOS
    check_file $PYTHON3_MOS
    check_file $MUTAGEN
    check_file $FFMPEG_MOS
    check_file $YOUTUBE_DL
    
    install $BIN_DIR/yt2mp3
    check_file $BIN_DIR/yt2mp3
}

linux_install ()
{
    # LINUX test dir's
    FFMPEG_LIN="/usr/bin/ffmpeg"
    PYTHON3_LIN="/usr/bin/python3"
    PYTHON2_LIN="/usr/bin/python2.7" # required for youtube-dl
    PIP3_LIN="/usr/bin/pip3"
    MUTAGEN="/usr/local/lib/python3.5/site-packages/mutagen"

    check_file $PYTHON3_LIN
    check_file $PYTHON2_LIN
    check_file $PIP3_LIN
    check_file $MUTAGEN
    check_file $FFMPEG_LIN
    check_file $YOUTUBE_DL

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


