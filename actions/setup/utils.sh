gitResolvePrefixToTag() {
    local url="$1"
    local prefix="$2"
    local refs=$(git ls-remote --tags --heads "$url")

    # try exact matching ref
    local ref=$(echo "$refs" | sed -E -n "s%.*refs/(heads|tags)/($prefix)\$%\2%p" | head -n1)
    if [ -n "$ref" ]; then
        echo "$ref"
        return 0
    fi

    # find latest ref matching prefix
    local ref=$(
        echo "$refs" \
        | sed -E -n "s%.*refs/tags/${prefix-v?}([0-9]+\.[0-9]+\.[0-9]+)\$%\1%p" \
        | grep -v '\^{}$' \
        | sort -t. -k1,1nr -k2,2nr -k3,3nr \
        | head -n1
    )
    if [ -n "$ref" ]; then
        echo "$prefix$ref"
        return 0
    fi

    return 2
}

InstallPackage() {
    local dest="$SUBLIME_TEXT_PACKAGES/$1"
    local url="$2"
    local prefix="$3"
    local ref=$(gitResolvePrefixToTag "$url" "$prefix")

    if [ -z "$ref" ]; then
        echo No ref found for "$1"
        exit 2;
    fi

    echo Installing "$1" from "$url"@"$ref" to "$dest"
    if [ ! -d "$dest" ]; then
        mkdir -p "$dest"
        git clone --quiet --depth 1 --branch "$ref" "$url" "$dest"
        rm -rf "$dest/.git"
    fi
}
