#!/bin/bash

#The preferred way of creating a smb share of a gluster volume has changed.
#The old method was to create a fuse mount of the volume and share the mount
#point through samba.
#
#New method eliminates the requirement of fuse mount and changes in fstab.
#glusterfs_vfs plugin for samba makes call to libgfapi to access the volume.
#
#This hook script automagically creates shares for volume on every volume start
#event by adding the entries in smb.conf file and sending SIGHUP to samba.
#
#In smb.conf:
#glusterfs vfs plugin has to be specified as required vfs object.
#Path value is relative to the root of gluster volume;"/" signifies complete
#volume.

PROGNAME="Ssamba-start"
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

function add_samba_share () {
        volname=$1
        STRING="\n[gluster-$volname]\n"
        STRING+="comment = For samba share of volume $volname\n"
        STRING+="vfs objects = glusterfs\n"
        STRING+="glusterfs:volume = $volname\n"
        STRING+="glusterfs:logfile = /var/log/samba/glusterfs-$volname.%%M.log\n"
        STRING+="glusterfs:loglevel = 7\n"
        STRING+="path = /\n"
        STRING+="read only = no\n"
        STRING+="guest ok = yes\n"
        printf "$STRING"  >> /etc/samba/smb.conf
}

function sighup_samba () {
        pid=`cat /var/run/smbd.pid`
        if [ "x$pid" != "x" ]
        then
                kill -HUP "$pid";
        else
                /etc/init.d/smb condrestart
        fi
}

function get_smb () {
        volname=$1
        uservalue=

        usercifsvalue=$(grep user.cifs /var/lib/glusterd/vols/"$volname"/info |\
                        cut -d"=" -f2)
        usersmbvalue=$(grep user.smb /var/lib/glusterd/vols/"$volname"/info |\
                       cut -d"=" -f2)

        if [[ $usercifsvalue = "disable" || $usersmbvalue = "disable" ]]; then
                uservalue="disable"
        fi
        echo "$uservalue"
}

parse_args $@
if [ $(get_smb "$VOL") = "disable" ]; then
        exit 0
fi

if ! grep --quiet "\[gluster-$VOL\]" /etc/samba/smb.conf ; then
        add_samba_share $VOL
        sighup_samba
fi
