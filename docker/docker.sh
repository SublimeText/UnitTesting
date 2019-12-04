#!/bin/bash

set -e

BASEDIR=`dirname $0`

CISH="/tmp/ci.sh"
if [ ! -f "$CISH" ]; then
    curl -s -L https://raw.githubusercontent.com/SublimeText/UnitTesting/ci/sbin/ci.sh -o "$CISH"
fi

if [ -z "$PACKAGE" ]; then
    echo '$PACKAGE is missing'
    exit 1
fi

. "$CISH"
