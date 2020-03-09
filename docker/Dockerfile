FROM ubermag/oommf

USER root

RUN apt update -y
RUN apt install -y git python3-pip curl
RUN python3 -m pip install --upgrade pip pytest-cov scipy nbval pycodestyle \
      git+git://github.com/ubermag/ubermagutil.git \
      git+git://github.com/ubermag/discretisedfield.git \
      git+git://github.com/ubermag/micromagneticmodel.git \
      git+git://github.com/ubermag/ubermagtable.git

COPY . /usr/local/oommfc/
RUN chown -R oommfuser /usr/local/oommfc/  # Make sure it is owned by the user.
USER oommfuser
WORKDIR /usr/local/oommfc
RUN python3 -m pip install .
