#!/bin/bash
for TRIES in {1..20}; do
    echo "Trying to connect on port 22 to FTD at location $1 (${TRIES})"
    nc -w 1 -z $1 22 && break;
    echo "FTDv not yet available, sleeping for 60 seconds"
    sleep 60
done
