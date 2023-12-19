#!/usr/bin/env bash
BLASTDBFILE="internal-blastdb-0.txt"

docker run \
  -it \
  -w $PWD \
  -v $PWD:$PWD \
  -v $HOME/.aws:/root/.aws \
  -e BLASTDB="/blastdb" \
  -e BLASTDBFILE="internal-blastdb-10.txt" \
  awsbatch/awsbatch_update_internal_genomes 
