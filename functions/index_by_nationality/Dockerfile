FROM python:3-slim
# Alternatively use ADD https:// (which will not be cached by Docker builder)
RUN apt-get update \
    && apt-get install -y curl \
    && echo "Pulling watchdog binary from Github." \
    && curl -sSL https://github.com/openfaas-incubator/of-watchdog/releases/download/0.2.3/of-watchdog > /usr/bin/fwatchdog \
    && chmod +x /usr/bin/fwatchdog 

WORKDIR /labs/bundle
# Copy the contents of the function folder to the image.
COPY  index_by_nationality-requirements.txt . 
# Install required modules.
RUN pip install -r index_by_nationality-requirements.txt
COPY  . . 
# Switch to non-root user.
RUN useradd guest
USER guest
# Watchdog configuration
ENV fprocess="python index.py"
ENV cgi_headers="true"
ENV mode="http"
ENV upstream_url="http://127.0.0.1:5000"
ENV LABS_BUNDLE_ROOT='/labs/bundle'
  
HEALTHCHECK --interval=1s CMD [ -e /tmp/.lock ] || exit 1
# Run the watchdog
CMD ["fwatchdog"]