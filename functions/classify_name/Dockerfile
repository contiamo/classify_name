FROM debian:stable-slim


RUN apt-get update && apt-get -qq -y install curl bzip2 \
    && curl -sSL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -bfp /usr/local \
    && rm -rf /tmp/miniconda.sh \
    && conda install -y python=3 \
    && conda update conda \
    && apt-get -qq -y remove curl bzip2 \
    && apt-get -qq -y autoremove \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* /var/log/dpkg.log \
    && conda clean --all --yes

ENV PATH /opt/conda/bin:$PATH

#RUN conda install -c caffe2 caffe2
RUN conda install pytorch-cpu -c pytorch

# Get watchdog
RUN echo "|--> Pulling watchdog binary from Github" \
    && apt-get update \
    && apt-get install -y curl \
    && curl -sSL https://github.com/openfaas/faas/releases/download/0.8.10/fwatchdog > /usr/bin/fwatchdog \
    && chmod +x /usr/bin/fwatchdog  


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