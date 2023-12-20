UID:=$(shell id -u)
PWD:=$(shell pwd)
DATA_DIR:="$(PWD)/data"
HOSTNAME:=$(shell hostname)
SCRATCH_BIOINFO:="s3://agbiome-scratchpad-notebooks/finite/220824_nifh_search"
