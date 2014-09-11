#!/bin/bash

set -e

Provision() {
    STP=/home/vagrant/.config/sublime-text-$SUBLIME_TEXT_VERSION/Packages

    if [ -z $(which subl) ]; then
        apt-get update
        apt-get install python-software-properties -y
        apt-get install git -y
        apt-get install curl -y
        apt-get install xvfb libgtk2.0-0 -y
        if [ $SUBLIME_TEXT_VERSION -eq 2 ]; then
            echo installing sublime 2
            add-apt-repository ppa:webupd8team/sublime-text-2 -y
            apt-get update
            apt-get install sublime-text -y
        elif [ $SUBLIME_TEXT_VERSION -eq 3 ]; then
            echo installing sublime 3
            add-apt-repository ppa:webupd8team/sublime-text-3 -y
            apt-get update
            apt-get install sublime-text-installer -y
        fi
    fi

    if [ ! -d $STP ]; then
        mkdir -p $STP
    fi

    if [ ! -d $STP/$PACKAGE ]; then
        ln -s /vagrant $STP/$PACKAGE
    fi

    if [ ! -d $STP/UnitTesting ]; then
        git clone https://github.com/randy3k/UnitTesting $STP/UnitTesting
    fi

    if [ ! -f /etc/init.d/xvfb ]; then
        echo installing xvfb controller
        curl https://gist.githubusercontent.com/randy3k/9337122/raw/xvfb | sudo tee /etc/init.d/xvfb > /dev/null
        chmod +x /etc/init.d/xvfb
    fi

    if [ -z $DISPLAY ]; then
        export DISPLAY=:1
        sh -e /etc/init.d/xvfb start
    fi

    if ! grep DISPLAY /etc/environment > /dev/null; then
        echo "DISPLAY=$DISPLAY" >> /etc/environment
    fi

    if ! grep SUBLIME_TEXT_VERSION /etc/environment > /dev/null; then
        echo "SUBLIME_TEXT_VERSION=$SUBLIME_TEXT_VERSION" >> /etc/environment
    fi

    if ! grep PACKAGE /etc/environment > /dev/null; then
        echo "PACKAGE=$PACKAGE" >> /etc/environment
    fi

    chown vagrant -R /home/vagrant/.config
}

RunTests() {
    STP=/home/vagrant/.config/sublime-text-$SUBLIME_TEXT_VERSION/Packages

    UT="$STP/UnitTesting"
    if [ -z "$1" ]; then
        python "$UT/sbin/run.py" "$PACKAGE"
    else
        python "$UT/sbin/run.py" "$1" "$PACKAGE"
    fi
    killall sublime_text
}


COMMAND=$1
echo "Running command: ${COMMAND}"
shift
case $COMMAND in
    "provision")
        Provision
        ;;
    "run_tests")
        RunTests "$@"
        ;;
esac
