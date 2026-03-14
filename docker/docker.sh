#!/bin/bash

set -e

BASEDIR=`dirname $0`

UNITTESTING_SOURCE=${UNITTESTING_SOURCE:-/unittesting}
CISH="$UNITTESTING_SOURCE/sbin/ci.sh"
if [ ! -f "$CISH" ]; then
    CISH="/tmp/ci.sh"
    if [ ! -f "$CISH" ]; then
        curl -s -L https://raw.githubusercontent.com/SublimeText/UnitTesting/master/sbin/ci.sh -o "$CISH"
    fi
fi

if [ -z "$PACKAGE" ]; then
    echo '$PACKAGE is missing'
    exit 1
fi

. "$CISH"
