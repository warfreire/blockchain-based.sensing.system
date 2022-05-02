FROM prnascimento/blockchain-client-base:1.0.0 as base-fabric

RUN groupadd -g 999 python && \
    useradd -r -u 999 -g python python

RUN mkdir /usr/src/app &&  chown python:python /usr/src/app
WORKDIR /usr/src/app

USER 999

WORKDIR /usr/src/app/fabpki-cli
ENV PATH="/usr/src/venv/bin:$PATH"

CMD ["/usr/src/venv/bin/python3", "message-ecdsa.py"]