# Modified script taken from https://github.com/jpetazzo/dind

FROM joommf/oommf

RUN apt-get update -y
RUN apt-get install -y apt-transport-https ca-certificates \
      lxc iptables curl python3-pip

RUN python3 -m pip install --upgrade pip pytest-cov scipy \
      git+git://github.com/joommf/discretisedfield.git \
      git+git://github.com/joommf/micromagneticmodel.git \
      git+git://github.com/joommf/oommfodt.git

# Enable running Docker inside Docker.
RUN curl -sSL https://get.docker.com/ | sh
ADD ./wrapdocker /usr/local/bin/wrapdocker
RUN chmod +x /usr/local/bin/wrapdocker
VOLUME /var/lib/docker
CMD ["wrapdocker"]

WORKDIR /usr/local
RUN git clone https://github.com/joommf/oommfc.git

WORKDIR /usr/local/oommfc