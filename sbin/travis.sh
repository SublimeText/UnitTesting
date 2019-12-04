#!/bin/bash

set -e

if [ "$TRAVIS_OS_NAME" = "linux" ] && [ -z $DISPLAY ]; then
    echo "Xvfb is not running"
    echo "check https://github.com/SublimeText/UnitTesting/issues/74"
    exit 1
fi

BASEDIR=`dirname $0`

if [ -f "$BASEDIR/ci.sh" ]; then
    CISH="$BASEDIR/ci.sh"
elif [ ! -f /tmp/ci.sh ]; then
    curl -L https://raw.githubusercontent.com/SublimeText/UnitTesting/master/sbin/ci.sh -o /tmp/ci.sh
    CISH="/tmp/ci.sh"
fi

REPONAME="${TRAVIS_REPO_SLUG#*/}"
PACKAGE=${PACKAGE:-$REPONAME}

. "$CISH"
