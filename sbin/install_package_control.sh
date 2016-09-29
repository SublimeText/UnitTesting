#! /usr/bin/env bash

set -e

while [ "$#" -ne 0 ]; do
    key="$1"
    case "$key" in
        --st)
            SUBLIME_TEXT_VERSION="$2"
            shift 2
        ;;
        *)
            echo "Unknown option: $1"
            exit 1
        ;;
    esac
done

if [ -z $SUBLIME_TEXT_VERSION ]; then
    echo "missing Sublime Text version"
    exit 1
fi

if [ $(uname) = 'Darwin' ]; then
    STP="$HOME/Library/Application Support/Sublime Text $SUBLIME_TEXT_VERSION/Packages"
else
    STP="$HOME/.config/sublime-text-$SUBLIME_TEXT_VERSION/Packages"
fi

STIP="${STP%/*}/Installed Packages"

if [ ! -d "$STIP" ]; then
    mkdir -p "$STIP"
fi

PC_PATH="$STIP/Package Control.sublime-package"
if [ ! -f "$PC_PATH" ]; then
    PC_URL="https://packagecontrol.io/Package Control.sublime-package"
    wget -O "$PC_PATH" "$PC_URL"
fi

PCH_PATH="$STP/0_install_package_control_helper"

if [ ! -d "$PCH_PATH" ]; then
    mkdir -p "$PCH_PATH"
    BASE=`dirname "$0"`
    cp "$BASE"/pc_helper.py "$PCH_PATH"/pc_helper.py
fi


# launch sublime text in background
subl &

ENDTIME=$(( $(date +%s) + 60 ))
while true  ; do
    printf "."
    [ -f "$PCH_PATH/success" ] && break
    if [ $(date +%s) -gt $ENDTIME ]; then
        echo ""
        pkill "[Ss]ubl"
        sleep 2
        rm -rf "$PCH_PATH"
        echo "Timeout: Fail to install Package Control."
        exit 1
    fi
    sleep 5
done

sleep 2
echo ""
rm -rf "$PCH_PATH"
echo "Package Control installed."
