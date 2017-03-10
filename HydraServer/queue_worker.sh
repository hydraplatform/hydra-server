#!/bin/bash
#
# (c) Copyright 2013, 2014, University of Manchester
#
# HydraPlatform is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HydraPlatform is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HydraPlatform.  If not, see <http://www.gnu.org/licenses/>

QUEUEROOT=~/.hydra/jobqueue

QUEUEDDIR=queued
RUNNINGDIR=running
FINISHEDDIR=finished
FAILEDDIR=failed

while true
do

    QJOBS=$(ls $QUEUEROOT/$QUEUEDDIR)

    NJOBS=${#QJOBS}

    if [ $NJOBS -eq 0 ];
    then
        echo "Waiting for jobs ..."
        sleep 10
    fi

    for JOB in $QJOBS
    do
        echo $JOB
        mv $QUEUEROOT/$QUEUEDDIR/$JOB $QUEUEROOT/$RUNNINGDIR/
        bash $QUEUEROOT/$RUNNINGDIR/$JOB
        STATUS=$?
        if [ $STATUS -ne 0 ]; 
        then
            mv $QUEUEROOT/$RUNNINGDIR/$JOB $QUEUEROOT/$FAILEDDIR/
        else
            mv $QUEUEROOT/$RUNNINGDIR/$JOB $QUEUEROOT/$FINISHEDDIR/
        fi
    done

done
