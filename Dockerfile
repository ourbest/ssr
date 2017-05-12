#
# Dockerfile for shadowsocks-libev
#

FROM alpine
MAINTAINER kev <noreply@datageek.info>

ARG SS_VER=2.4.1
ARG SS_URL=https://github.com/shadowsocksr/shadowsocksr-libev/archive/$SS_VER.zip

RUN set -ex && \
    apk add --no-cache --virtual .build-deps \
                                asciidoc \
                                autoconf \
                                build-base \
                                curl \
                                libtool \
                                linux-headers \
                                openssl-dev \
                                pcre-dev \
                                tar \
                                xmlto && \
    cd /tmp && \
    curl -sSL $SS_URL | tar xz --strip 1 && \
    ./configure --prefix=/usr --disable-documentation && \
    make install && \
    cd .. && \

    runDeps="$( \
        scanelf --needed --nobanner /usr/bin/ss-* \
            | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
            | xargs -r apk info --installed \
            | sort -u \
    )" && \
    apk add --no-cache --virtual .run-deps $runDeps && \
    apk del .build-deps && \
    rm -rf /tmp/*

RUN apk add --no-cache python3

ADD get-pip.py .

RUN python3 get-pip.py

ENV SERVER_ADDR 0.0.0.0
ENV SERVER_PORT 8388
ENV PASSWORD    kexueshangwang
ENV METHOD      aes-256-cfb
ENV TIMEOUT     300
ENV DNS_ADDR    8.8.8.8
ENV DNS_ADDR_2  8.8.4.4


EXPOSE $SERVER_PORT/tcp $SERVER_PORT/udp 5000/tcp

RUN mkdir -p /root

ADD kcptun /root/kcptun

WORKDIR /root

ADD code /root/code

ADD entrypoint .

ENV KCP_PORT 6688

RUN chmod +x /root/kcptun/server_linux_amd64

EXPOSE $KCP_PORT/udp

RUN pip3 install flask requests

ENTRYPOINT ["sh", "entrypoint", "-k", "${PASSWORD}"]
