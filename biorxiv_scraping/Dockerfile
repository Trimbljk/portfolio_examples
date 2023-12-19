FROM jupyter/datascience-notebook:3d1dfb045378

USER root

RUN apt update && apt-get install --yes apt-transport-https \
    graphviz \
    libgraphviz-dev pkg-config

USER $NB_USER

RUN pip install graphviz==0.20.1 \
    && pip install --ignore-installed pyathena==3.0.6 \
    && pip install awscli==1.29.42 \
    && pip install biopython==1.78 \
    && pip install --upgrade google-auth \
    && pip install google-api-python-client \
    && pip install spacy==3.7.2 \
    && pip install pygraphviz==1.11 \
    && pip install pyarrow==12.0.0 \
    && pip install zipfile39
