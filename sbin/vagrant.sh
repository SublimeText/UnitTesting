#! /bin/bash
echo I am provisioning...

export SUBLIME_TEXT_VERSION=$1
export PACKAGE="$2"
export STP=/home/vagrant/.config/sublime-text-$SUBLIME_TEXT_VERSION/Packages

if [ -z $(which subl) ]; then
    apt-get update
    apt-get install python-software-properties -y
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
    apt-get install git -y
    apt-get install curl -y
    apt-get install xvfb libgtk2.0-0 -y
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
export DISPLAY=:1
if ! grep DISPLAY /etc/environment > /dev/null; then
    echo "DISPLAY=$DISPLAY" >> /etc/environment
fi
/etc/init.d/xvfb start

chown vagrant -R /home/vagrant/.config
