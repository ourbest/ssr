FROM ubuntu:16.04

RUN apt-get update && apt-get install -y supervisor python-pip wget bash unzip

RUN pip install requests Flask

WORKDIR /root/
ADD shadowsocksR.sh /root/install-shadowsocks.sh
RUN sh install-shadowsocks.sh
#RUN wget --no-check-certificate -O shadowsocks-go.sh https://raw.githubusercontent.com/teddysun/shadowsocks_install/master/shadowsocks-go.sh && \
#    chmod +x shadowsocks-go.sh && \
#    ./shadowsocks-go.sh 2>&1 | tee shadowsocks-go.log

RUN mkdir /root/kcptun

ADD /kcptun/ /root/kcptun/

EXPOSE 8989
EXPOSE 6688/udp
EXPOSE 5000

ENV SS_PASSWORD kexueshangwang

ADD ss.conf /etc/supervisor/conf.d/ss.conf
ADD kcp.conf /etc/supervisor/conf.d/kcp.conf
ADD flask.conf /etc/supervisor/conf.d/flask.conf

ADD code /root/code

CMD supervisord -n