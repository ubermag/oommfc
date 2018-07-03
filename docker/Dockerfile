FROM joommf/oommf

USER root

RUN apt update -y
RUN apt install -y apt-transport-https ca-certificates \
      lxc iptables curl python3-pip

RUN python3 -m pip install --upgrade pip pytest-cov scipy sarge nbval testpath \
      git+git://github.com/joommf/joommfutil.git \
      git+git://github.com/joommf/discretisedfield.git \
      git+git://github.com/joommf/micromagneticmodel.git \
      git+git://github.com/joommf/oommfodt.git

COPY . /usr/local/oommfc/
WORKDIR /usr/local/oommfc
RUN python3 -m pip install .
