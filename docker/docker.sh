#!/bin/bash

set -e

BASEDIR=`dirname $0`

UNITTESTING_SOURCE=${UNITTESTING_SOURCE:-/unittesting}
SOURCE_CISH="$UNITTESTING_SOURCE/sbin/ci.sh"
CISH="/tmp/ci.sh"
if [ -f "$SOURCE_CISH" ]; then
    # Normalize CRLF from mounted Windows checkouts.
    sed 's/\r$//' "$SOURCE_CISH" > "$CISH"
elif [ ! -f "$CISH" ]; then
    curl -s -L https://raw.githubusercontent.com/SublimeText/UnitTesting/master/sbin/ci.sh -o "$CISH"
fi

if [ -z "$PACKAGE" ]; then
    echo '$PACKAGE is missing'
    exit 1
fi

. "$CISH"
