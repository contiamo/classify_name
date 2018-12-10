FROM python:3-slim
# Alternatively use ADD https:// (which will not be cached by Docker builder)
RUN apt-get update \
    && apt-get install -y curl \
    && echo "Pulling watchdog binary from Github." \
    && curl -sSL https://github.com/openfaas/faas/releases/download/0.9.4/fwatchdog > /usr/bin/fwatchdog \
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
ENV fprocess="python3 index.py"
ENV LABS_BUNDLE_ROOT='/labs/bundle'
EXPOSE 8080  
HEALTHCHECK --interval=1s CMD [ -e /tmp/.lock ] || exit 1
# Run the watchdog
CMD ["fwatchdog"]