#!/bin/bash

# This script is used to remove xattrs set related to quota functionality by
# quota, marker and posix translators on the path received as argument.
# It is generally invoked from quota-metadata-cleanup.sh, but can
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
    [ $# -ne 1 ] && usage $0

    MOUNT_DIR=$1;
    PREV_DIR=`pwd`;
    cd $MOUNT_DIR;
    for i in `find .`;
    do
            setfattr -n $XATTR_KEY -v 1 $i
    done
    cd $PREV_DIR;
}

main $@
