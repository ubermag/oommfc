FROM ubuntu:16.04

MAINTAINER Marijan Beg <m.beg@soton.ac.uk>

RUN apt-get update -y && \
    apt-get install -y git python3-pip curl tk-dev tcl-dev && \
    python3 -m pip install --upgrade pip pytest-cov codecov nbval \
      git+git://github.com/joommf/discretisedfield.git \
      git+git://github.com/joommf/micromagneticmodel.git \
      git+git://github.com/joommf/oommfodt.git

# Set locale environment variables for nbval tests.
RUN locale-gen en_GB.UTF-8
ENV LANG en_GB.UTF-8
ENV LANGUAGE en_GB:en
ENV LC_ALL en_GB.UTF-8

WORKDIR /usr/local/

RUN git clone https://github.com/fangohr/oommf.git

WORKDIR /usr/local/oommf/

RUN make

ENV OOMMFTCL /usr/local/oommf/oommf/oommf.tcl

WORKDIR /usr/local/

RUN git clone https://github.com/joommf/oommfc.git