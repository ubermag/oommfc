FROM joommf/oommf

RUN apt update -y
RUN apt install -y apt-transport-https ca-certificates \
      lxc iptables curl python3-pip

RUN python3 -m pip install --upgrade pip pytest-cov scipy sarge nbval testpath \
      git+git://github.com/joommf/discretisedfield.git \
      git+git://github.com/joommf/micromagneticmodel.git \
      git+git://github.com/joommf/oommfodt.git

# Enable running Docker inside Docker taken from
# https://github.com/jpetazzo/dind where the license can be found.
RUN curl -sSL https://get.docker.com/ | sh
ADD ./wrapdocker /usr/local/bin/wrapdocker
RUN chmod +x /usr/local/bin/wrapdocker
VOLUME /var/lib/docker
CMD ["wrapdocker"]

# Intentionally wrong OOMMF paths for testing.
ENV OOMMFWRONGPATH /usr/local/oommf/oommf/oommf/oommf.tcl
ENV OOMMFWRONGFILE /usr/local/oommfc/Dockerfile

WORKDIR /usr/local
RUN git clone https://github.com/joommf/oommfc.git
WORKDIR /usr/local/oommfc
RUN python3 -m pip install .
