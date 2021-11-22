FROM python:3.9

WORKDIR $HOME
RUN apt-get install libssl-dev
RUN pip3 install ecdsa

RUN git clone https://github.com/hyperledger/fabric-sdk-py.git
WORKDIR $HOME/fabric-sdk-py
RUN git checkout tags/v0.8.0
RUN make install


WORKDIR /usr/src/app/fabpki-cli
CMD ["python3", "message-ecdsa.py"]


