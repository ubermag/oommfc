FROM joommf/oommf

RUN apt-get update -y
RUN apt-get install -y python3-pip curl
RUN python3 -m pip install --upgrade pip pytest-cov scipy \
      git+git://github.com/computationalmodelling/nbval.git nbformat \
      git+git://github.com/joommf/discretisedfield.git \
      git+git://github.com/joommf/micromagneticmodel.git \
      git+git://github.com/joommf/oommfodt.git

WORKDIR /usr/local/

RUN git clone https://github.com/joommf/oommfc.git