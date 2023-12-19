FROM ncbi/blast:2.13.0
ARG pipeline

# Debian packages installed
RUN apt-get update \
    && apt-get install \
         --no-install-recommends \
         --yes python-pip=18.1-5 \
	        python-setuptools=40.8.0-1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install awscli==1.16.96 && \
    pip install pandas==0.23

#COPY common_utils /common_utils
# hadolint ignore=DL3013
#RUN pip install /common_utils

COPY $pipeline/job.sh /usr/local/bin/
#COPY $pipeline/bitscore2int.py /usr/local/bin/

ENTRYPOINT ["job.sh"]
