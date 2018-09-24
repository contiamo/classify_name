FROM python:3-alpine

# Get watchdog
RUN apk --no-cache add curl ${ADDITIONAL_PACKAGE} \ 
    && echo "Pulling watchdog binary from Github." \
    && curl -sSL https://github.com/openfaas/faas/releases/download/0.8.10/fwatchdog > /usr/bin/fwatchdog \
    && chmod +x /usr/bin/fwatchdog \
    && apk del curl --no-cache   

# Copy over files
WORKDIR /labs/bundle
COPY /common .
RUN pip install -r requirements.txt
COPY index.py .
COPY handler.py .
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