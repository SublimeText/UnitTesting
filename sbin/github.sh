#!/bin/bash

set -e

BASEDIR=`dirname $0`

CISH="/tmp/ci.sh"
if [ -f "$BASEDIR/ci.sh" ]; then
    CISH="$BASEDIR/ci.sh"
elif [ ! -f /tmp/ci.sh ]; then
    TAG=${UNITTESTING_TAG:-master}
    curl -s -L https://raw.githubusercontent.com/SublimeText/UnitTesting/$TAG/sbin/ci.sh -o /tmp/ci.sh
fi

REPONAME="${GITHUB_REPOSITORY#*/}"
PACKAGE=${PACKAGE:-$REPONAME}

. "$CISH"
