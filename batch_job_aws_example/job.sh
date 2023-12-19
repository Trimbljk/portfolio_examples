#!/usr/bin/env bash

set -eo pipefail
trap finish EXIT

finish () {
  echo "Cleaning up..."
}

### LOGGING ###
echo "AWS_BATCH_CE_NAME: $AWS_BATCH_CE_NAME"
echo "AWS_BATCH_JOB_ARRAY_INDEX: $AWS_BATCH_JOB_ARRAY_INDEX"
echo "AWS_BATCH_JOB_ATTEMPT: $AWS_BATCH_JOB_ATTEMPT"
echo "AWS_BATCH_JOB_ID: $AWS_BATCH_JOB_ID"
echo "AWS_BATCH_JQ_NAME: $AWS_BATCH_JQ_NAME"
echo "BLASTDB: $BLASTDB"
#echo "BLASTDBFILE: $BLASTDBFILE"
echo "TAG: $TAG"
echo "###########################################################"

DB_NAME="agbiome-genomes"

for f in asms/*.fasta; do cat $f; done > "${DB_NAME}.fasta.tmp"

echo "#########################################################"

mv "${DB_NAME}.fasta.tmp" "${DB_NAME}.fasta"

#aws s3 cp "s3://agbiome-awsbatch/internal-blastdbs/${BLASTDBFILE}" .
#
#while read -r line; do
#  aws s3 cp "s3://agbiome-isolate-assemblies/$line" .
#done <$BLASTDBFILE
#
#for f in *.fasta; do cat $f; done > "${DB_NAME}.fasta.tmp"
#
#
#mv "${DB_NAME}.fasta.tmp" "${DB_NAME}.fasta"

echo "Finished making Fasta file for database..."

echo "Building BLAST database at ${BLASTDB}/${DB_NAME} ..."

echo "###########################################################"
mkdir -p "${BLASTDB}"

makeblastdb \
  -in "${DB_NAME}.fasta" \
  -dbtype nucl \
  -out "${BLASTDB}/${DB_NAME}" \
  -title "${DB_NAME}" \
  -logfile "${BLASTDB}/${DB_NAME}.log"

echo "BLAST database complete."

cat ${BLASTDB}/agbiome-genomes.njs
