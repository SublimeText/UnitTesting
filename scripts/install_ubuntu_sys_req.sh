#! /usr/bin/env bash

set -e

apt-get update
apt-get install --no-install-recommends -y \
    libglib2.0-0 \
    libgtk-3-0 \
    psmisc \
    locales \
    locales-all


if [ "$SUBLIME_TEXT_ARCH" = "x32" ]; then
    dpkg --add-architecture i386
    apt-get update
    apt-get install --no-install-recommends -y \
        libc6:i386 \
        libncurses5:i386 \
        libstdc++6:i386 \
        libglib2.0-0:i386 \
        libgtk-3-0:i386 \
        libx11-6:i386
fi
