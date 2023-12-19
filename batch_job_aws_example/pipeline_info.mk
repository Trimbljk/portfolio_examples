ifeq ($(STAGE), dev)
	PIPELINE=awsbatch_update_internal_aim_blast_dev
	STACK_NAME=AwsBatchUpdateInternalBlastdb-dev
else ifeq ($(STAGE), prod)
	PIPELINE=awsbatch_update_internal_aim_blast
	STACK_NAME=AwsBatchUpdateInternalBlastdb
endif
