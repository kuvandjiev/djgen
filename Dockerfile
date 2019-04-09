FROM ubuntu:18.04

RUN mkdir -p /webapps/djgen
WORKDIR /webapps/djgen
ADD . /webapps/djgen

RUN apt update && apt install python3 python3-dev python3-pip -y
RUN apt install /webapps/djgen/build/salt/wkhtmltox/files/wkhtmltox_0.12.5-1.bionic_amd64.deb -y

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

CMD bash