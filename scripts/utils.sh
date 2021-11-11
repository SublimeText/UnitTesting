gitRemoteURL() {
    local repo
    repo=$(git config --local --get remote.origin.url 2>/dev/null || true)
    if [[ "$repo" =~ ^git@github.com:(.*)\.git$ ]]; then
        echo "${BASH_REMATCH[1]}"
    elif [[ "$repo" =~ ^https://github.com/(.*)\.git$ ]]; then
        echo "${BASH_REMATCH[1]}"
    elif [[ "$repo" =~ ^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$ ]]; then
        echo "$repo"
    fi
}

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
    local DEST="$SUBLIME_TEXT_PACKAGES/$1"
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
        rm -rf "$DEST/.git"
    fi
}
