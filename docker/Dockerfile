FROM ubuntu:latest

USER root
RUN apt-get update
RUN apt-get install --no-install-recommends sudo apt-utils  -y
RUN apt-get install --no-install-recommends python software-properties-common  -y
RUN apt-get install --no-install-recommends git curl xvfb  -y
RUN apt-get install --no-install-recommends libglib2.0-0 libgtk-3-0 -y
RUN apt-get install --no-install-recommends psmisc -y
RUN apt-get install --no-install-recommends locales locales-all -y

ARG arch
RUN if [ "$arch" = "i386" ]; then dpkg --add-architecture i386; fi
RUN if [ "$arch" = "i386" ]; then apt-get update; fi
RUN if [ "$arch" = "i386" ]; then apt-get install --no-install-recommends libc6:i386 libncurses5:i386 libstdc++6:i386 -y; fi
RUN if [ "$arch" = "i386" ]; then apt-get install --no-install-recommends libglib2.0-0:i386 libgtk-3-0:i386 libx11-6:i386 -y; fi

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

ENV DISPLAY=:1
COPY xvfb /etc/init.d/xvfb
RUN chmod +x /etc/init.d/xvfb
COPY docker.sh /docker.sh
RUN chmod +x /docker.sh
COPY entrypoint.sh /entrypoint.sh
RUN chmod 666 /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /project
ENTRYPOINT ["/entrypoint.sh"]
