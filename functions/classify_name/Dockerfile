FROM frolvlad/alpine-glibc:alpine-3.8

ENV CONDA_DIR="/opt/conda"
ENV PATH="$CONDA_DIR/bin:$PATH"

# Install conda
RUN CONDA_VERSION="4.5.4" && \
    CONDA_MD5_CHECKSUM="a946ea1d0c4a642ddf0c3a26a18bb16d" && \
    \
    apk add --no-cache --virtual=.build-dependencies wget ca-certificates bash && \
    \
    mkdir -p "$CONDA_DIR" && \
    wget "http://repo.continuum.io/miniconda/Miniconda3-${CONDA_VERSION}-Linux-x86_64.sh" -O miniconda.sh && \
    echo "$CONDA_MD5_CHECKSUM  miniconda.sh" | md5sum -c && \
    bash miniconda.sh -f -b -p "$CONDA_DIR" && \
    echo "export PATH=$CONDA_DIR/bin:\$PATH" > /etc/profile.d/conda.sh && \
    rm miniconda.sh && \
    \
    conda update --all --yes && \
    conda config --set auto_update_conda False && \
    rm -r "$CONDA_DIR/pkgs/" && \
    \
    apk del --purge .build-dependencies && \
    \
    mkdir -p "$CONDA_DIR/locks" && \
    chmod 777 "$CONDA_DIR/locks"

#RUN conda install -c caffe2 caffe2
RUN conda install pytorch-cpu -c pytorch

# # Install packages necessary for pytorch
# RUN echo "|--> Updating" \
#     && apk update && apk upgrade \
#     && echo http://dl-cdn.alpinelinux.org/alpine/edge/main | tee /etc/apk/repositories \
#     && echo http://dl-cdn.alpinelinux.org/alpine/edge/testing | tee -a /etc/apk/repositories \
#     && echo http://dl-cdn.alpinelinux.org/alpine/edge/community | tee -a /etc/apk/repositories \
#     && echo "|--> Install basics pre-requisites" \
#     && apk add --no-cache tini \
#     curl ca-certificates python3 py3-numpy py3-numpy-f2py \
#     freetype jpeg libpng libstdc++ libgomp graphviz font-noto \
#     && echo "|--> Install build dependencies" \
#     && apk add --no-cache --virtual=.build-deps \
#     build-base linux-headers python3-dev git cmake jpeg-dev bash \
#     libffi-dev gfortran openblas-dev py-numpy-dev freetype-dev libpng-dev \
#     && echo "|--> Cleaning" \
#     && rm -rf /root/.cache \
#     && rm -rf /root/.[acpw]* \
#     && rm -rf /var/cache/apk/* \
#     && echo "|--> Done!"

# Get watchdog
RUN echo "|--> Pulling watchdog binary from Github" \
    && apk --no-cache add curl \
    && curl -sSL https://github.com/openfaas/faas/releases/download/0.8.10/fwatchdog > /usr/bin/fwatchdog \
    && chmod +x /usr/bin/fwatchdog  \
    && apk del curl


WORKDIR /labs/bundle
# Install python dependencies
COPY common /labs/bundle/common
RUN pip install -r common/requirements.txt

# Copy over files
WORKDIR /labs/bundle
COPY index.py .
COPY handler.py .
# remove gcc
#
## Set environment variables
ENV fprocess="python index.py"
ENV cgi_headers="true"
ENV mode="http"
ENV upstream_url="http://127.0.0.1:5000"
ENV LABS_BUNDLE_ROOT='/labs/bundle'
#
HEALTHCHECK --interval=1s CMD [ -e /tmp/.handlelock ] || exit 1
#
#
## Add data processed folder (create first)
RUN mkdir -p /labs/bundle/data/processed/

#
##CMD ["python index.py"]
CMD ["fwatchdog"]