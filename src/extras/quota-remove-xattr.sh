#!/bin/bash

# This script is used to remove xattrs set related to quota functionality by
# quota, marker and posix translators on the path received as argument.
# It is generally invoked from glusterd upon quota disable command, but can
# also be used stand-alone.
#
# xattrs cleaned up are
# trusted.glusterfs.quota* and trusted.pgfid*

XATTR_KEY="glusterfs.quota-xattr-cleanup"
usage ()
{
    echo >&2 "usage: $0 <path>"
}

main ()
{
    if [ $# -ne 1 -o "$1" == "-h" -o "$1" == "--help" ]
    then
            usage $0
            exit;
    fi

    MOUNT_DIR=$1;
    PREV_DIR=`pwd`;
    cd $MOUNT_DIR || exit $?;

    for i in `find .`;
    do
            setfattr -n $XATTR_KEY -v 1 $i
    done

    cd $PREV_DIR;
}

main $@
