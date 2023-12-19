FROM jupyter/datascience-notebook:6d91620dbb99

USER root

RUN apt update && apt-get install --yes graphviz=2.42.2-3build2 \
    libgraphviz-dev=2.42.2-3build2 pkg-config

USER $NB_USER

RUN pip install --no-cache-dir --ignore-installed pyathena==2.4.1 \
    && pip install --ignore-installed awscli==1.27.27 \
    && pip install biopython==1.78 \
    && pip install --upgrade google-auth \
    && pip install google-api-python-client \
    && pip install pygraphviz==1.9
    

