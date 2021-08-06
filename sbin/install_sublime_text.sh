#! /usr/bin/env bash

set -e

while [ "$#" -ne 0 ]; do
    key="$1"
    case "$key" in
        --st)
            SUBLIME_TEXT_VERSION="$2"
            shift 2
            continue
        ;;
        --arch)
            SUBLIME_TEXT_ARCH="$2"
            shift 2
            continue
        ;;
        *)
            echo "Unknown option: $1"
            exit 1
        ;;
    esac
done

if [ -z $SUBLIME_TEXT_VERSION ]; then
    echo "Missing Sublime Text version"
    exit 1
fi

if [ -z $SUBLIME_TEXT_ARCH ]; then
    SUBLIME_TEXT_ARCH=x64
fi

if [ $SUBLIME_TEXT_VERSION -ge 4 ] && [ "$SUBLIME_TEXT_ARCH" != "x64" ]; then
    echo "wrong value of $SUBLIME_TEXT_ARCH for Sublime Text version $SUBLIME_TEXT_VERSION"
    exit 1
fi

if [ $SUBLIME_TEXT_VERSION -ge 4 ]; then
    STWEB="https://www.sublimetext.com/download"
else
    STWEB="https://www.sublimetext.com/$SUBLIME_TEXT_VERSION"
fi

if [ $SUBLIME_TEXT_VERSION -ge 4 ]; then
    if [ $(uname) = 'Darwin' ]; then
        STP="$HOME/Library/Application Support/Sublime Text/Packages"
    else
        STP="$HOME/.config/sublime-text/Packages"
    fi
else
    if [ $(uname) = 'Darwin' ]; then
        STP="$HOME/Library/Application Support/Sublime Text $SUBLIME_TEXT_VERSION/Packages"
    else
        STP="$HOME/.config/sublime-text-$SUBLIME_TEXT_VERSION/Packages"
    fi
fi

if [ $(uname) = 'Darwin'  ]; then
    if [ -z $(which subl) ]; then
        if [ $SUBLIME_TEXT_VERSION -eq 2 ]; then
            SUBLIME_TEXT="Sublime Text 2"
        else
            SUBLIME_TEXT="Sublime Text"
        fi
        echo "installing sublime text $SUBLIME_TEXT_VERSION"
        for i in {1..20}; do
            if [ $SUBLIME_TEXT_VERSION -ge 4 ]; then
                URL=$(curl -L -s "$STWEB" | sed -n 's/.*href="\([^"]*_mac\.zip\)".*/\1/p')
            else
                URL=$(curl -L -s "$STWEB" | sed -n 's/.*href="\([^"]*\.dmg\)".*/\1/p')
            fi
            [ -n "$URL" ] && break || sleep 3
        done
        if [ -z "$URL" ]; then
            echo "could not download Sublime Text binary"
            exit 1
        fi
        URL=$(echo "$URL" | sed 's/ /%20/')
        echo "downloading $URL"
        for i in {1..20}; do
            if [ $SUBLIME_TEXT_VERSION -ge 4 ]; then
                curl -L "$URL" -o ~/Downloads/sublimetext.zip && break || sleep 3
            else
                curl -L "$URL" -o ~/Downloads/sublimetext.dmg && break || sleep 3
            fi
        done
        if [ $SUBLIME_TEXT_VERSION -ge 4 ]; then
            mkdir -p "$HOME/Applications"
            unzip ~/Downloads/sublimetext.zip -d "$HOME/Applications/"
        else
            hdiutil attach ~/Downloads/sublimetext.dmg
            mkdir -p "$HOME/Applications"
            cp -r "/Volumes/$SUBLIME_TEXT/$SUBLIME_TEXT.app" "$HOME/Applications/$SUBLIME_TEXT.app"
        fi
        mkdir -p $HOME/.local/bin
        ln -s "$HOME/Applications/$SUBLIME_TEXT.app/Contents/SharedSupport/bin/subl" \
            $HOME/.local/bin/subl

        if [ ! -f "$STP/User/Preferences.sublime-settings" ]; then
            echo creating sublime package directory
            mkdir -p "$STP/User"
            # make sure a new window will be opened
            echo '{"close_windows_when_empty": false }' > "$STP/User/Preferences.sublime-settings"
        fi

        # make `subl` available
        open "$HOME/Applications/$SUBLIME_TEXT.app"
        sleep 2
        pkill '[Ss]ubl' || true
        pkill 'plugin_host' || true
        sleep 2
    else
        echo "Sublime Text was installed already!"
        exit 1
    fi
else
    if [ -z $(which subl) ]; then
        if [ $SUBLIME_TEXT_VERSION -eq 2 ]; then
            SUBLIME_TEXT="Sublime Text 2"
        elif [ $SUBLIME_TEXT_VERSION -eq 3 ]; then
            SUBLIME_TEXT="sublime_text_3"
        else
            SUBLIME_TEXT="sublime_text"
        fi
        echo "installing sublime text $SUBLIME_TEXT_VERSION"
        for i in {1..20}; do
            if [ $SUBLIME_TEXT_VERSION -ge 4 ]; then
                URL=$(curl -s "$STWEB" | sed -n 's/.*href="\([^"]*_x64\.tar\.xz\)".*/\1/p')
            else
                if [ "$SUBLIME_TEXT_ARCH" = "x64" ]; then
                    URL=$(curl -s "$STWEB" | sed -n 's/.*href="\([^"]*x64\.tar\.bz2\)".*/\1/p')
                else
                    URL=$(curl -s "$STWEB" | sed -n 's/.*href="\([^"]*x32\.tar\.bz2\)".*/\1/p')
                fi
            fi
            [ -n "$URL" ] && break || sleep 3
        done
        if [ -z "$URL" ]; then
            echo "could not download Sublime Text binary"
            exit 1
        fi
        echo "downloading $URL"
        for i in {1..20}; do
            if [ $SUBLIME_TEXT_VERSION -ge 4 ]; then
                curl "$URL" -o ~/sublimetext.tar.xz && break || sleep 3
            else
                curl "$URL" -o ~/sublimetext.tar.bz2 && break || sleep 3
            fi
        done
        if [ $SUBLIME_TEXT_VERSION -ge 4 ]; then
            # FIXME, move it to DOckerfile
            sudo apt-get install -y xz-utils
            tar xf ~/sublimetext.tar.xz -C ~/
        else
            tar jxf ~/sublimetext.tar.bz2 -C ~/
        fi
        mkdir -p $HOME/.local/bin
        ln -sf "$HOME/$SUBLIME_TEXT/sublime_text" $HOME/.local/bin/subl

        # make `subl` available
        "$HOME/$SUBLIME_TEXT/sublime_text" &
        sleep 2
        pkill '[Ss]ubl' || true
        pkill 'plugin_host' || true
        sleep 2
    else
        echo "Sublime Text was installed already!"
        exit 1
    fi
fi
