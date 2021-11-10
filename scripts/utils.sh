if [ $SUBLIME_TEXT_VERSION -ge 4 ]; then
    if [ $(uname) = 'Darwin' ]; then
        STP="$HOME/Library/Application Support/Sublime Text/Packages"
    elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
        STP="$HOME/.config/sublime-text/Packages"
    else
        STP="/c/st/Data/Packages/"
    fi
else
    if [ $(uname) = 'Darwin' ]; then
        STP="$HOME/Library/Application Support/Sublime Text $SUBLIME_TEXT_VERSION/Packages"
    elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
        STP="$HOME/.config/sublime-text-$SUBLIME_TEXT_VERSION/Packages"
    else
        STP="/c/st/Data/Packages/"
    fi
fi

gitCloneTag() {
    local URL="$1"
    local TAG="$2"
    local DEST="$3"
    git clone --quiet --depth 1 --branch "$TAG" "$URL" "$DEST"
}

gitFetchLatestTagFromRepository() {
    local URL="$1"
    local LSTAGS
    LSTAGS=$(git ls-remote --tags "$URL")
    local TAG=$(echo "$LSTAGS" | grep -E '/v?[0-9]+\.[0-9]+\.[0-9]+$' |
      sed -E 's|.*/v?([^/]*)$|\1|' |
      sort -t. -k1,1nr -k2,2nr -k3,3nr | head -n1)
    echo "$LSTAGS" | grep -F "$TAG" | sed -E 's|.*/([^/]*)$|\1|' | grep -v '\^' | head -n1
}

InstallPackage() {
    local DEST="$STP/$1"
    local URL="$2"
    local PreferredTag="$3"
    if [ -z "$PreferredTag" ]; then
        local TAG=$(gitFetchLatestTagFromRepository "$URL")
    else
        local TAG="$PreferredTag"
    fi
    echo Installing "$1" from "$URL"@"$TAG" to "$DEST"
    if [ ! -d "$DEST" ]; then
        mkdir -p "$DEST"
        gitCloneTag "$URL" "$TAG" "$DEST"
        [ -d "$DEST/.git" ] && rm -rf "$DEST/.git"
    fi
}
