#! /bin/bash

#The preferred way of creating a smb share of a gluster volume has changed.
#The old method was to create a fuse mount of the volume and share the mount
#point through samba.
#
#New method eliminates the requirement of fuse mount and changes in fstab.
#glusterfs_vfs plugin for samba makes call to libgfapi to access the volume.
#
#This hook script automagically removes shares for volume on every volume stop
#event by removing the volume related entries(if any) in smb.conf file.

PROGNAME="Ssamba-stop"
OPTSPEC="volname:"
VOL=

function parse_args () {
        ARGS=$(getopt -l $OPTSPEC  -name $PROGNAME $@)
        eval set -- "$ARGS"

        while true; do
        case $1 in
        --volname)
         shift
         VOL=$1
         ;;
        *)
         shift
         break
         ;;
        esac
        shift
        done
}

function del_samba_share () {
        volname=$1
        sed -i "/\[gluster-$volname\]/,/^$/d" /etc/samba/smb.conf
}

function sighup_samba () {
        pid=`cat /var/run/smbd.pid`
        if [ "x$pid" != "x" ]
        then
                kill -HUP $pid;
        else
                /etc/init.d/smb condrestart
        fi
}

parse_args $@
del_samba_share $VOL
sighup_samba
