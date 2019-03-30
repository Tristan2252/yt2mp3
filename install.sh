#!/bin/bash

SRC_DST=/usr/local/src/yt2mp3
INSTALL_DST=/usr/local/bin/yt2mp3

###### Remove Old Versions ######
if [ -e /opt/yt2mp3 ]; then
    sudo rm -rf /opt/yt2mp3
fi
if [ -e /usr/local/bin/yt2mp3 ]; then 
    sudo rm /usr/local/bin/yt2mp3
fi

if [ $(uname -s) = "Darwin" ]; then
    DISTRO="mac"
    PKG_MGR="brew install"
    if [ ! -e /usr/local/bin/brew ]; then
        printf "You need Homebrew to install via this script\nGo to https://brew.sh/ to install\n"
	exit 0
    fi
elif [ ! -e /etc/lsb_release ]; then 
    DISTRO="ubuntu"
    PKG_MGR="sudo apt install -y"
elif [ ! -e /etc/fedora-release ]; then 
    DISTRO="fedora"
    PKG_MGR="sudo yum install -y"
fi

echo "OS: $DISTRO"

###### PACKAGE INSTALLS ######
if ! which python3 &>/dev/null; then 
    $PKG_MGR  python3
fi
if ! which pip3 &>/dev/null; then 
    $PKG_MGR install python3-pip
fi
if ! which ffmpeg &>/dev/null; then 

    # add repo for trusty
    if [ $DISTRO = "ubuntu" ] && [ $(lsb_release -c | awk {'print $2'}) == "trusty" ]; then
        sudo add-apt-repository ppa:mc3man/trusty-media -y
        sudo apt update
    fi

    if [ $DISTRO = "fedora" ]; then
        sudo yum install \
        https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm \
        https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm -y
    fi 

    $PKG_MGR ffmpeg
fi


###### PIP INSTALLS ######
if ! pip3 show youtube-dl &>/dev/null; then 
    pip3 install youtube-dl
fi
if ! pip3 show mutagen &>/dev/null; then 
    pip3 install mutagen
fi

if [ ! -e $SRC_DST ]; then 
    sudo mkdir -p $SRC_DST
    sudo cp -r . $SRC_DST
fi

if [ ! -e $INSTALL_DST ]; then 
    sudo ln -s $SRC_DST/yt2mp3.py $INSTALL_DST
fi

