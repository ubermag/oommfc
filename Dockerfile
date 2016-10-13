FROM ubuntu:16.04

RUN apt-get update -y
RUN apt-get install -y git python3-pip curl tk-dev tcl-dev
RUN python3 -m pip install --upgrade pip pytest-cov scipy \
      git+git://github.com/computationalmodelling/nbval.git nbformat \
      git+git://github.com/joommf/micromagneticmodel.git \
      git+git://github.com/joommf/oommfodt.git \
      git+git://github.com/joommf/discretisedfield.git

WORKDIR /usr/local/

RUN git clone https://github.com/fangohr/oommf.git

WORKDIR /usr/local/oommf/

RUN make

ENV OOMMFTCL /usr/local/oommf/oommf/oommf.tcl

WORKDIR /usr/local/

RUN git clone https://github.com/joommf/oommfc.git