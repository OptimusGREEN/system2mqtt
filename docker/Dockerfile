FROM ubuntu:20.04

ENV TERM linux
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get dist-upgrade -y && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/OptimusGREEN/system2mqtt.git \
    && chmod +x system2mqtt/run.py \
    && chmod +x system2mqtt/s2m.py \
    && pip install -r system2mqtt/deps.txt \
    && mkdir /config
    
VOLUME /config

CMD ["/usr/bin/python3", "/system2mqtt/run.py", "/config/s2m.conf"]
