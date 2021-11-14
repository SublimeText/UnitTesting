gitResolvePrefixToTag() {
    local url="$1"
    local prefix="$2"
    local refs=$(git ls-remote --tags --heads "$url")

    local exact_match=$(echo "$refs" | sed -E -n "s%.*refs/(heads|tags)/($prefix)\$%\2%p" | head -n1)
    if [ -n "$exact_match" ]; then
        echo "$exact_match"
        return 0
    fi

    if [ -z "$prefix" ]; then
        prefix="v?"
    fi

    local matched_tags=$(echo "$refs" | sed -E -n "s%.*refs/tags/($prefix[0-9]+\.[0-9]+\.[0-9]+)\$%\1%p" | grep -v '\^{}$')

    echo "$matched_tags" | sort -t. -k1,1nr -k2,2nr -k3,3nr | head -n1
}

InstallPackage() {
    local dest="$SUBLIME_TEXT_PACKAGES/$1"
    local url="$2"
    local prefix="$3"
    local tag=$(gitResolvePrefixToTag "$url" "$prefix")
    echo Installing "$1" from "$url"@"$tag" to "$dest"
    if [ ! -d "$dest" ]; then
        mkdir -p "$dest"
        git clone --quiet --depth 1 --branch "$tag" "$url" "$dest"
    fi
}
