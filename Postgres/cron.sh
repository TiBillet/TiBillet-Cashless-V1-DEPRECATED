#!/bin/bash

#réalise un dump de la DB :
pg_dumpall -c -U postgres > /SaveDb/dump_`date +%d-%m-%Y"_"%H_%M_%S`_V3.sql 2>&1
# efface les dumps de plus de 10 jours :
find /SaveDb -mtime +10 -type f -delete
