%global _hardened_build 1

%global _for_fedora_koji_builds 0

# uncomment and add '%' to use the prereltag for pre-releases
# %%global prereltag qa3

##-----------------------------------------------------------------------------
## All argument definitions should be placed here and keep them sorted
##

# if you wish to compile an rpm with cmocka unit testing...
# rpmbuild -ta glusterfs-3.7.5.tar.gz --with cmocka
%{?_with_cmocka:%global _with_cmocka --enable-cmocka}

# if you wish to compile an rpm without rdma support, compile like this...
# rpmbuild -ta glusterfs-3.7.5.tar.gz --without rdma
%{?_without_rdma:%global _without_rdma --disable-ibverbs}

# No RDMA Support on s390(x)
%ifarch s390 s390x
%global _without_rdma --disable-ibverbs
%endif

# if you wish to compile an rpm without epoll...
# rpmbuild -ta glusterfs-3.7.5.tar.gz --without epoll
%{?_without_epoll:%global _without_epoll --disable-epoll}

# if you wish to compile an rpm without fusermount...
# rpmbuild -ta glusterfs-3.7.5.tar.gz --without fusermount
%{?_without_fusermount:%global _without_fusermount --disable-fusermount}

# if you wish to compile an rpm without geo-replication support, compile like this...
# rpmbuild -ta glusterfs-3.7.5.tar.gz --without georeplication
%{?_without_georeplication:%global _without_georeplication --disable-georeplication}

# Disable geo-replication on EL5, as its default Python is too old
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
%global _without_georeplication --disable-georeplication
%endif

# if you wish to compile an rpm without the OCF resource agents...
# rpmbuild -ta glusterfs-3.7.5.tar.gz --without ocf
%{?_without_ocf:%global _without_ocf --without-ocf}

# if you wish to build rpms without syslog logging, compile like this
# rpmbuild -ta glusterfs-3.7.5.tar.gz --without syslog
%{?_without_syslog:%global _without_syslog --disable-syslog}

# disable syslog forcefully as rhel <= 6 doesn't have rsyslog or rsyslog-mmcount
# Fedora deprecated syslog, see 
#  https://fedoraproject.org/wiki/Changes/NoDefaultSyslog
# (And what about RHEL7?)
%if ( 0%{?fedora} && 0%{?fedora} >= 20 ) || ( 0%{?rhel} && 0%{?rhel} <= 6 )
%global _without_syslog --disable-syslog
%endif

# if you wish to compile an rpm without the BD map support...
# rpmbuild -ta glusterfs-3.7.5.tar.gz --without bd
%{?_without_bd:%global _without_bd --disable-bd-xlator}

%if ( 0%{?rhel} && 0%{?rhel} < 6 || 0%{?sles_version} )
%define _without_bd --disable-bd-xlator
%endif

# if you wish to compile an rpm without the qemu-block support...
# rpmbuild -ta glusterfs-3.7.5.tar.gz --without qemu-block
%{?_without_qemu_block:%global _without_qemu_block --disable-qemu-block}

%if ( 0%{?rhel} && 0%{?rhel} < 6 )
# xlators/features/qemu-block fails to build on RHEL5, disable it
%define _without_qemu_block --disable-qemu-block
%endif

# Disable data-tiering on EL5, sqlite is too old
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
%global _without_tiering --disable-tiering
%endif

# if you wish not to build server rpms, compile like this.
# rpmbuild -ta glusterfs-3.7.5.tar.gz --without server

%global _build_server 1
%if "%{?_without_server}"
%global _build_server 0
%endif

%if ( "%{?dist}" == ".el6rhs" ) || ( "%{?dist}" == ".el7rhs" ) || ( "%{?dist}" == ".el7rhgs" )
%global _build_server 1
%else
%global _build_server 0
%global _without_georeplication --disable-georeplication
%endif

%global _without_extra_xlators 1
%global _without_regression_tests 1

%global _build_server 1
##-----------------------------------------------------------------------------
## All %global definitions should be placed here and keep them sorted
##

%if ( 0%{?fedora} && 0%{?fedora} > 16 ) || ( 0%{?rhel} && 0%{?rhel} > 6 )
%global _with_systemd true
%endif

%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 7 )
%global _with_firewalld --enable-firewalld
%endif

%if 0%{?_tmpfilesdir:1}
%define _with_tmpfilesdir --with-tmpfilesdir=%{_tmpfilesdir}
%else
%define _with_tmpfilesdir --without-tmpfilesdir
%endif

# there is no systemtap support! Perhaps some day there will be
%global _without_systemtap --enable-systemtap=no

# From https://fedoraproject.org/wiki/Packaging:Python#Macros
%if ( 0%{?rhel} && 0%{?rhel} <= 5 )
%{!?python_sitelib: %global python_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%if ( 0%{?_with_systemd:1} )
%define _init_enable()  /bin/systemctl enable %1.service ;
%define _init_disable() /bin/systemctl disable %1.service ;
%define _init_restart() /bin/systemctl try-restart %1.service ;
%define _init_start()   /bin/systemctl start %1.service ;
%define _init_stop()    /bin/systemctl stop %1.service ;
%define _init_install() install -D -p -m 0644 %1 %{buildroot}%{_unitdir}/%2.service ;
# can't seem to make a generic macro that works
%define _init_glusterd   %{_unitdir}/glusterd.service
%define _init_glusterfsd %{_unitdir}/glusterfsd.service
%else
%define _init_enable()  /sbin/chkconfig --add %1 ;
%define _init_disable() /sbin/chkconfig --del %1 ;
%define _init_restart() /sbin/service %1 condrestart &>/dev/null ;
%define _init_start()   /sbin/service %1 start &>/dev/null ;
%define _init_stop()    /sbin/service %1 stop &>/dev/null ;
%define _init_install() install -D -p -m 0755 %1 %{buildroot}%{_sysconfdir}/init.d/%2 ;
# can't seem to make a generic macro that works
%define _init_glusterd   %{_sysconfdir}/init.d/glusterd
%define _init_glusterfsd %{_sysconfdir}/init.d/glusterfsd
%endif

%if ( 0%{_for_fedora_koji_builds} )
%if ( 0%{?_with_systemd:1} )
%global glusterfsd_service glusterfsd.service
%else
%global glusterfsd_service glusterfsd.init
%endif
%endif

%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}-%{version}}

%if ( 0%{?rhel} && 0%{?rhel} < 6 )
   # _sharedstatedir is not provided by RHEL5
   %define _sharedstatedir /var/lib
%endif

# We do not want to generate useless provides and requires for xlator
# .so files to be set for glusterfs packages.
# Filter all generated:
#
# TODO: RHEL5 does not have a convenient solution
%if ( 0%{?rhel} == 6 )
    # filter_setup exists in RHEL6 only
    %filter_provides_in %{_libdir}/glusterfs/%{version}/
    %global __filter_from_req %{?__filter_from_req} | grep -v -P '^(?!lib).*\.so.*$'
    %filter_setup
%else
    # modern rpm and current Fedora do not generate requires when the
    # provides are filtered
    %global __provides_exclude_from ^%{_libdir}/glusterfs/%{version}/.*$
%endif


##-----------------------------------------------------------------------------
## All package definitions should be placed here and keep them sorted
##
Summary:          Distributed File System
%if ( 0%{_for_fedora_koji_builds} )
Name:             glusterfs
Version:          3.5.0
Release:          0.1%{?prereltag:.%{prereltag}}%{?dist}
Vendor:           Fedora Project
%else
Name:             glusterfs
Version:          3.7.5
Release:          19%{?dist}
ExclusiveArch:    x86_64 aarch64
%endif
License:          GPLv2 or LGPLv3+
Group:            System Environment/Base
URL:              http://www.gluster.org/docs/index.php/GlusterFS
%if ( 0%{_for_fedora_koji_builds} )
Source0:          http://bits.gluster.org/pub/gluster/glusterfs/src/glusterfs-%{version}%{?prereltag}.tar.gz
Source1:          glusterd.sysconfig
Source2:          glusterfsd.sysconfig
Source6:          rhel5-load-fuse-modules
Source7:          glusterfsd.service
Source8:          glusterfsd.init
%else
Source0:          glusterfs-3.7.5.tar.gz
Source9:	enable-server-packages.patch
Source10:	glusterfs.S56copy.patch
Source11:	glusterfs.ini
%endif

BuildRoot:        %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

%if ( 0%{?rhel} && 0%{?rhel} <= 5 )
BuildRequires:    python-simplejson
%endif
%if ( 0%{?_with_systemd:1} )
BuildRequires:    systemd-units
%endif

Requires:         %{name}-libs = %{version}-%{release}
BuildRequires:    bison flex
BuildRequires:    gcc make automake libtool
BuildRequires:    ncurses-devel readline-devel
BuildRequires:    libxml2-devel openssl-devel
BuildRequires:    libaio-devel libacl-devel
BuildRequires:    python-devel
BuildRequires:    python-ctypes
BuildRequires:    userspace-rcu-devel >= 0.7
%if ( 0%{?rhel} && 0%{?rhel} <= 5 )
BuildRequires:    e2fsprogs-devel
%else
BuildRequires:    libuuid-devel
%endif
%if ( 0%{?_with_cmocka:1} )
BuildRequires:    libcmocka-devel >= 1.0.1
%endif
%if ( 0%{!?_without_tiering:1} )
BuildRequires:    sqlite-devel
%endif
%if ( 0%{!?_without_systemtap:1} )
BuildRequires:    systemtap-sdt-devel
%endif
%if ( 0%{!?_without_bd:1} )
BuildRequires:    lvm2-devel
%endif
%if ( 0%{!?_without_qemu_block:1} )
BuildRequires:    glib2-devel
%endif
%if ( 0%{!?_without_georeplication:1} )
BuildRequires:    libattr-devel
%endif

%if (0%{?_with_firewalld:1})
BuildRequires:    firewalld
%endif

Obsoletes:        hekafs
Obsoletes:        %{name}-common < %{version}-%{release}
Obsoletes:        %{name}-core < %{version}-%{release}
Obsoletes:        %{name}-ufo
Provides:         %{name}-common = %{version}-%{release}
Provides:         %{name}-core = %{version}-%{release}

# Patch0001: 0001-Update-rfc.sh-to-rhgs-3.1.2.patch
Patch0002: 0002-tier-ctr-CTR-DB-named-lookup-heal-of-cold-tier-durin.patch
Patch0003: 0003-tier-ctr-Solution-for-db-locks-for-tier-migrator-and.patch
Patch0004: 0004-firewall-spec-Create-glusterfs-firewall-service-if-f.patch
Patch0005: 0005-glusterd-disable-ping-timer-b-w-glusterd-and-make-ep.patch
Patch0006: 0006-event-epoll-Use-pollers-to-check-if-event_pool_dispa.patch
Patch0007: 0007-Tier-cli-Change-detach-tier-commit-force-to-detach-t.patch
Patch0008: 0008-Tier-glusterd-Do-not-allow-attach-tier-if-remove-bri.patch
Patch0009: 0009-glusterd-add-brick-change-add-brick-implementation-t.patch
Patch0010: 0010-tier-glusterd-volume-status-failed-after-detach-star.patch
Patch0011: 0011-tier-dht-unlink-fails-after-lookup-in-a-directory.patch
Patch0012: 0012-fuse-resolve-complete-path-after-a-graph-switch.patch
Patch0013: 0013-tiering-glusterd-keep-afr-ec-xlators-name-constant.patch
Patch0014: 0014-tier-shd-create-shd-volfile-for-tiering.patch
Patch0015: 0015-tier-shd-inline-warning-when-compiled-with-gcc-v.5.patch
Patch0016: 0016-tier-shd-make-shd-commands-compatible-with-tiering.patch
Patch0017: 0017-cli-quota-rm-rf-on-mountpoint-dir-is-not-showing-quo.patch
Patch0018: 0018-cli-freeing-the-allocated-memory.patch
Patch0019: 0019-gluster-v-status-xml-for-a-replicated-hot-tier-volum.patch
Patch0020: 0020-Tier-cli-number-of-bricks-remains-the-same-in-v-info.patch
Patch0021: 0021-Accidentally-merged-before-proper-ACKs-in-bug.patch
Patch0022: 0022-Accidentally-merged-before-proper-ACKs-in-bug.patch
Patch0023: 0023-cluster-tier-add-watermarks-and-policy-driver.patch
Patch0024: 0024-libglusterfs-pass-buffer-size-to-gf_store_read_and_t.patch
Patch0025: 0025-glusterd-probing-a-new-node-which-is-part-of-another.patch
Patch0026: 0026-extra-enable-shared-storage-key-should-create-shared.patch
Patch0027: 0027-glusterd-disabling-enable-shared-storage-option-shou.patch
Patch0028: 0028-glusterd-spec-fixing-autogen-issue.patch
Patch0029: 0029-tier-cli-throw-a-warning-when-user-issues-a-detach-t.patch
Patch0030: 0030-systemd-spec-glusterd-Adding-EnvironmentFile-in-glus.patch
Patch0031: 0031-cluster-tier-remove-suprious-log-messages-on-valid-f.patch
Patch0032: 0032-server-protocol-option-for-dynamic-authorization-of-.patch
Patch0033: 0033-quota-use-copy_frame-when-creating-new-frame-during-.patch
Patch0034: 0034-quota-fix-crash-in-quota_fallocate.patch
Patch0035: 0035-quota-marker-marker-code-cleanup.patch
Patch0036: 0036-quota-marker-dir_count-accounting-is-not-atomic.patch
Patch0037: 0037-Revert-rpc-By-default-set-allow-insecure-bind-insecu.patch
Patch0038: 0038-cluster-dht-Do-not-migrate-files-with-POSIX-locks-he.patch
Patch0039: 0039-cluster-tier-Changed-tier-xattr-name-value.patch
Patch0040: 0040-cluster-tier-update-man-pages-for-tier-feature.patch
Patch0041: 0041-cluster-tier-do-not-abort-migration-if-a-single-bric.patch
Patch0042: 0042-cluster-tier-add-pause-tier-for-snapshots.patch
Patch0043: 0043-Tier-cli-removing-warning-message-for-tiering.patch
Patch0044: 0044-features-snap-cleanup-the-root-loc-in-statfs.patch
Patch0045: 0045-cluster-dht-op_ret-not-set-correctly-in-dht_fsync_cb.patch
Patch0046: 0046-tier-ctr-Correcting-the-internal-fop-calculation.patch
Patch0047: 0047-snapshot-Fix-snapshot-clone-postvalidate.patch
Patch0048: 0048-build-remove-ghost-directory-entries.patch
Patch0049: 0049-glusterd-call-glusterd_store_volinfo-in-bump-up-op-v.patch
Patch0050: 0050-afr-fixes-in-transaction-code.patch
Patch0051: 0051-build-add-RHGS-specific-changes.patch
Patch0052: 0052-secalert-remove-setuid-bit-for-fusermount-glusterfs.patch
Patch0053: 0053-build-packaging-corrections-for-RHEL-5.patch
Patch0054: 0054-build-introduce-security-hardening-flags-in-gluster.patch
Patch0055: 0055-spec-fix-add-pre-transaction-scripts-for-geo-rep-and.patch
Patch0056: 0056-rpm-glusterfs-devel-for-client-builds-should-not-dep.patch
Patch0057: 0057-build-add-pretrans-check.patch
Patch0058: 0058-build-exclude-libgfdb.pc-conditionally.patch
Patch0059: 0059-cluster-ec-update-version-and-size-on-good-bricks.patch
Patch0060: 0060-tier-Typo-while-setting-the-wrong-value-of-low-hi-wa.patch
Patch0061: 0061-features-ctr-Reduce-the-log-level-for-ctr-disabled-m.patch
Patch0062: 0062-cluster-tier-do-not-log-error-message-on-lookup-heal.patch
Patch0063: 0063-features-changelog-ignore-recording-tiering-rebalanc.patch
Patch0064: 0064-features-changelog-record-mknod-if-tier-dht-linkto-i.patch
Patch0065: 0065-geo-rep-Avoid-cold-tier-bricks-during-ENTRY-operatio.patch
Patch0066: 0066-geo-rep-Add-data-operation-if-mknod-with-tier-attrib.patch
Patch0067: 0067-afr-write-zeros-to-sink-for-non-sparse-files.patch
Patch0068: 0068-cluster-dht-rebalance-rebalance-failure-handling.patch
Patch0069: 0069-build-exclude-glusterfs.xml-on-rhel-7-client-build.patch
Patch0070: 0070-glusterd-fix-op-versions-for-RHS-backwards-compatabi.patch
Patch0071: 0071-cluster-ec-Remove-index-entries-if-file-dir-does-not.patch
Patch0072: 0072-cluster-tier-enable-CTR-on-attach-tier.patch
Patch0073: 0073-mount-fuse-use-a-queue-instead-of-pipe-to-communicat.patch
Patch0074: 0074-nfs-avoid-invalid-usage-of-cs-variable-in-nfs-fops.patch
Patch0075: 0075-glusterd-fix-info-file-checksum-mismatch-during-upgr.patch
Patch0076: 0076-Revert-rpc-fix-binding-brick-issue-while-bind-insecu.patch
Patch0077: 0077-glusterd-move-new-feature-tiering-enum-op-to-the-las.patch
Patch0078: 0078-cluster-afr-Handle-stack-reset-failures.patch
Patch0079: 0079-cluster-ec-Implement-gfid-hash-read-policy.patch
Patch0080: 0080-geo-rep-Update-geo-rep-status-if-monitor-process-is-.patch
Patch0081: 0081-rpc-Set-allow-insecure-to-on-by-default.patch
Patch0082: 0082-quota-add-version-to-quota-xattrs.patch
Patch0083: 0083-v-info-for-disperse-count-fails-while-upgrading.patch
Patch0084: 0084-correction-of-message-displayed-after-attach-tier.patch
Patch0085: 0085-tier-dht-Ignoring-replica-for-migration-counting.patch
Patch0086: 0086-tests-tier-Move-common-functions-to-tier.rc.patch
Patch0087: 0087-cluster-tier-fix-lookup-unhashed-on-tiered-volumes.patch
Patch0088: 0088-tier-ctr-Ignore-CTR-Lookup-heal-insert-errors.patch
Patch0089: 0089-tier-libgfdb-Replacing-ASCII-query-file-with-binary.patch
Patch0090: 0090-tier-ctr-Ignore-bitrot-related-fops.patch
Patch0091: 0091-cluster-tier-correct-promotion-cycle-calculation.patch
Patch0092: 0092-common-ha-Corrected-refresh-config-output-parsing.patch
Patch0093: 0093-Revert-fuse-resolve-complete-path-after-a-graph-swit.patch
Patch0094: 0094-dht-heal-directory-path-if-the-directory-is-not-pres.patch
Patch0095: 0095-marker-do-remove-xattr-only-for-last-link.patch
Patch0096: 0096-tiering-Message-shown-in-gluster-vol-tier-volname-st.patch
Patch0097: 0097-dht-update-cached-subvolume-during-readdirp-cbk.patch
Patch0098: 0098-tier-ctr-resolving-redefination-of-get_db_path_key_t.patch
Patch0099: 0099-tier-ctr-ignoring-bitrot-scrubber-fops.patch
Patch0100: 0100-tier-libgfdb-Extending-log-level-flexibity-in-libgfd.patch
Patch0101: 0101-cluster-ec-fix-bug-in-update_good.patch
Patch0102: 0102-Remove-selinux-mount-option-from-man-mount.glusterfs.patch
Patch0103: 0103-extras-Exit-with-SUCCESS-if-no-processes-to-stop.patch
Patch0104: 0104-cluster-tier-Disallow-detach-commit-when-detach-in-p.patch
Patch0105: 0105-extras-hooks-Fix-parsing-of-args-in-S30samba-set.sh.patch
Patch0106: 0106-snapshot-Don-t-display-snapshot-s-hard-limit-and-sof.patch
Patch0107: 0107-snapshot-copying-nfs-ganesha-export-file.patch
Patch0108: 0108-tier-ctr-Providing-option-to-record-or-ignore-metada.patch
Patch0109: 0109-md-cache-Remove-readdirp-fop-for-md-cache.patch
Patch0110: 0110-snapshot-Inherit-snap-max-hard-limit-from-original-v.patch
Patch0111: 0111-gfapi-xattr-key-length-check-to-avoid-brick-crash.patch
Patch0112: 0112-tools-glusterfind-Do-not-show-session-corrupted-if-n.patch
Patch0113: 0113-tools-glusterfind-password-prompts-for-peer-nodes-on.patch
Patch0114: 0114-cluster-tier-Do-not-delete-linkto-file-on-demotion.patch
Patch0115: 0115-cluster-tier-make-cache-mode-default-for-tiered-volu.patch
Patch0116: 0116-mgmt-gluster-Handle-tier-brick-volgen.patch
Patch0117: 0117-cluster-ec-Mark-self-heal-fops-as-internal.patch
Patch0118: 0118-cluster-ec-Mark-internal-fops-appropriately.patch
Patch0119: 0119-tools-glusterfind-Prepend-prefix-in-case-of-delete.patch
Patch0120: 0120-geo-rep-Don-t-log-geo-rep-safe-errors-in-mount-logs.patch
Patch0121: 0121-geo-rep-Fix-FD-leak-from-Active-Geo-rep-worker.patch
Patch0122: 0122-tools-glusterfind-Handle-Keyboard-interrupt.patch
Patch0123: 0123-build-fix-ecdh.h-and-dh.h-deps.patch
Patch0124: 0124-glusterd-brick-failed-to-start.patch
Patch0125: 0125-Tiering-Adding-space-between-error-message-for-detac.patch
Patch0126: 0126-glusterd-cli-command-implementation-for-bitrot-scrub.patch
Patch0127: 0127-features-bit-rot-stub-changes-for-showing-bad-object.patch
Patch0128: 0128-features-bit-rot-scrubber-changes-for-getting-the-li.patch
Patch0129: 0129-cluster-tier-readdirp-to-cold-tier-only.patch
Patch0130: 0130-quota-fix-backward-compatibility-of-quota-xattr-vers.patch
Patch0131: 0131-glusterd-bitrot-Integration-of-bad-files-from-bitd-w.patch
Patch0132: 0132-glusterd-Change-volume-start-into-v3-framework.patch
Patch0133: 0133-cluster-afr-Remember-flags-sent-by-create-fop.patch
Patch0134: 0134-Tiering-change-of-error-message-for-v-tier-vname-det.patch
Patch0135: 0135-tier-ctr-Correcting-rename-logic.patch
Patch0136: 0136-features-bit-rot-Fix-NULL-dereference.patch
Patch0137: 0137-glusterd.service-Ensure-rpcbind-is-started-before-gl.patch
Patch0138: 0138-glusterd-copy-snapshot-object-during-duplication-of-.patch
Patch0139: 0139-tools-glusterfind-add-query-command-to-list-files.patch
Patch0140: 0140-glusterfsd-To-support-volfile-server-transport-type-.patch
Patch0141: 0141-glusterd-glusterfsd-to-support-volfile-server-transp.patch
Patch0142: 0142-quota-vol-quota-fails-when-transport.socket.bind-add.patch
Patch0143: 0143-cluster-ec-Create-copy-of-dict-for-setting-internal-.patch
Patch0144: 0144-libgfapi-To-support-set_volfile-server-transport-typ.patch
Patch0145: 0145-afr-vol-heal-info-fails-when-transport.socket.bind-a.patch
Patch0146: 0146-geo-rep-Allow-setting-config-remote_gsyncd.patch
Patch0147: 0147-glusterd-geo-rep-Adding-ssh-port-option-for-geo-rep-.patch
Patch0148: 0148-geo-rep-Make-restrictive-ssh-keys-optional.patch
Patch0149: 0149-geo-rep-New-Config-option-for-ssh_port.patch
Patch0150: 0150-geo-rep-fd-close-and-fcntl-issue.patch
Patch0151: 0151-tier-glusterd-Validation-for-frequency-thresholds-an.patch
Patch0152: 0152-glusterd-Removing-error-message-in-glusterd-log-duri.patch
Patch0153: 0153-tier-libgfdb-sql-Correcting-logic-in-sql-query-for-r.patch
Patch0154: 0154-afr-glusterd-Fix-naming-issue-in-tier-related-change.patch
Patch0155: 0155-glusterd-tier-Reset-to-reconfigured-values-after-det.patch
Patch0156: 0156-snapshot-clone-Fix-tier-pause-failure-for-snapshot-c.patch
Patch0157: 0157-glusterd-afr-Readdirp-performance-improvement.patch
Patch0158: 0158-features-index-Readdirp-performance-improvement.patch
Patch0159: 0159-cluster-afr-Readdirp-performance-enhancement.patch
Patch0160: 0160-heal-Changed-heal-info-to-process-all-indices-direct.patch
Patch0161: 0161-geo-rep-geo-rep-to-handle-CAPS-based-Hostname.patch
Patch0162: 0162-geo-rep-use-cold-tier-bricks-for-namespace-operation.patch
Patch0163: 0163-cluster-tier-fix-loading-tier.so-into-glusterd.patch
Patch0164: 0164-tier-tier-Ignoring-status-of-already-migrated-files.patch
Patch0165: 0165-snapshot-Fix-quorum-check-for-clone.patch
Patch0166: 0166-tier-dht-Fix-mem-leak-from-lookup-response-dict.patch
Patch0167: 0167-mount-fuse-Fix-use-after-free-crash.patch
Patch0168: 0168-Upcall-Read-gfid-from-iatt-in-case-of-invalid-inode.patch
Patch0169: 0169-quota-add-quota-version-to-xlator-volume_options-str.patch
Patch0170: 0170-posix-fix-posix_fgetxattr-to-return-the-correct-erro.patch
Patch0171: 0171-quota-copy-quota_version-value-in-func-glusterd_voli.patch
Patch0172: 0172-glusterd-quota-quota-version-conflict-in-export-impo.patch
Patch0173: 0173-glusterd-fix-the-build.patch
Patch0174: 0174-tier-Spawn-promotion-or-demotion-thread-depending-on.patch
Patch0175: 0175-tier-ctr-Check-filename-in-ctr_lookup-for-nameless-l.patch
Patch0176: 0176-glusterd-add-pending_node-only-if-hxlator_count-is-v.patch
Patch0177: 0177-tier-dht-files-are-still-going-to-decommissioned-sub.patch
Patch0178: 0178-tier-glusterd-Check-before-starting-tier-daemon-duri.patch
Patch0179: 0179-cluster-tier-Fix-double-free-in-tier-process.patch
Patch0180: 0180-dht-rebalance-Use-seperate-return-variable-for-desti.patch
Patch0181: 0181-storage-posix-fix-dict-leak-in-posix_fgetxattr.patch
Patch0182: 0182-protocol-client-give-preference-to-loc-gfid-over-ino.patch
Patch0183: 0183-features-index-Prevent-logging-due-to-NULL-dict.patch
Patch0184: 0184-afr-refresh-inode-using-fstat.patch
Patch0185: 0185-tier-glusterd-Only-positive-values-for-freq-threshol.patch
Patch0186: 0186-nfs-Inform-client-to-perform-extra-GETATTR-call-for-.patch
Patch0187: 0187-tier-unlink-during-migration.patch
Patch0188: 0188-tier-glusterd-making-new-tier-detach-command-throw-w.patch
Patch0189: 0189-glusterd-fix-info-file-checksum-mismatch-during-upgr.patch
Patch0190: 0190-bitrot-getting-correct-value-of-scrub-stat-s.patch
Patch0191: 0191-features-bit-rot-stub-delete-the-link-for-bad-object.patch
Patch0192: 0192-storage-posix-Implement-.unlink-directory.patch
Patch0193: 0193-cluster-afr-During-name-heal-propagate-EIO-only-on-g.patch
Patch0194: 0194-afr-Fix-bug-in-afr_inode_refresh_do.patch
Patch0195: 0195-hook-scripts-fix-S30Samba-scripts-on-systemd-systems.patch
Patch0196: 0196-hook-scripts-don-t-let-ctdb-script-change-samba-conf.patch
Patch0197: 0197-cluster-tier-fix-tier-max-files-bookeeping-and-help.patch
Patch0198: 0198-afr-handle-bad-objects-during-lookup-inode_refresh.patch
Patch0199: 0199-cli-xml-display-correct-xml-output-of-tier-volume.patch
Patch0200: 0200-tier-dht-Properly-free-file-descriptors-during-data-.patch
Patch0201: 0201-tier-Demotion-failed-if-the-file-was-renamed-when-it.patch
Patch0202: 0202-tier-unlink-open-fd-for-special-file-for-fdstat.patch
Patch0203: 0203-cluster-tier-do-not-block-in-synctask-created-from-p.patch
Patch0204: 0204-heal-Do-not-print-heal-count-on-ENOTCONN.patch
Patch0205: 0205-performance-write-behind-retry-failed-syncs-to-backe.patch
Patch0206: 0206-tier-delete-the-linkfile-if-data-file-creation-fails.patch
Patch0207: 0207-ctr-sql-Providing-for-vol-set-for-sqlcachesize-and-s.patch
Patch0208: 0208-cluster-afr-Fix-data-loss-due-to-race-between-sh-and.patch
Patch0209: 0209-geo-rep-Fix-getting-subvol-number.patch
Patch0210: 0210-geo-rep-Fix-getting-subvol-count.patch
Patch0211: 0211-tier-glusterd-reset-to-gd_op_3_7_6-from-gd_op_3_7_7.patch
Patch0212: 0212-cluster-ec-Get-size-and-config-for-invalid-inode.patch
Patch0213: 0213-cluster-dht-Ftruncate-on-migrating-file-fails-with-E.patch
Patch0214: 0214-Tier-tier-start-force-command-implementation.patch
Patch0215: 0215-glusterd-reduce-friend-update-flood.patch
Patch0216: 0216-glusterfsd-Initialize-ctx-cmd_args.patch
Patch0217: 0217-quota-limit-xattr-for-subdir-not-healed-on-newly-add.patch
Patch0218: 0218-tier-ctr-sql-Dafault-values-for-sql-cache-and-wal-si.patch
Patch0219: 0219-dht-changing-variable-type-to-avoid-overflow.patch
Patch0220: 0220-Tier-typo-in-tier-help.patch
Patch0221: 0221-tier-create-Dynamically-allocate-gfid-memory.patch
Patch0222: 0222-tier-glusterd-tier-daemon-not-updating-the-status.patch
Patch0223: 0223-tier-unlink-symlink-failed-to-unlink.patch
Patch0224: 0224-cluster-tier-Additional-details-in-error-messages.patch
Patch0225: 0225-cluster-tier-Additional-details-in-error-messages.patch
Patch0226: 0226-tier-create-store-TIER_LINKFILE_GFID-in-xattr-dictio.patch
Patch0227: 0227-cluster-tier-check-watermark-during-migration.patch
Patch0228: 0228-cluster-dht-Handle-failure-in-getxattr.patch
Patch0229: 0229-tier-glusterd-Corrected-default-values-for-sql-cache.patch
Patch0230: 0230-performance-write-behind-maintain-correct-transit-si.patch
Patch0231: 0231-features-bitrot-Fail-node-uuid-getxattr-if-file-is-m.patch
Patch0232: 0232-glusterd-register-rpc-notification-for-unix-sockets.patch
Patch0233: 0233-quota-fix-quota-hook-script-for-add-brick.patch
Patch0234: 0234-snapd-Do-not-persist-snapd-port.patch
Patch0235: 0235-glusterd-cli-mask-out-inaccurate-scrub-statistics.patch
Patch0236: 0236-revert-commit-62ff30a.patch
Patch0237: 0237-cluster-tier-allow-db-queries-to-be-interruptable.patch
Patch0238: 0238-cluster-dht-Rebalance-process-crashes-due-to-double-.patch
Patch0239: 0239-features-bitrot-add-check-for-corrupted-object-in-f-.patch
Patch0240: 0240-nfs-send-lookup-if-inode_ctx-is-not-set.patch
Patch0241: 0241-snapview-client-remove-check-for-parent-inode-type.patch
Patch0242: 0242-fuse-sent-at-least-one-lookup-before-actual-fop.patch
Patch0243: 0243-fuse-send-lookup-if-inode_ctx-is-not-set.patch
Patch0244: 0244-gfapi-send-lookup-if-inode_ctx-is-not-set.patch
Patch0245: 0245-performance-write-behind-fix-memory-corruption.patch
Patch0246: 0246-glusterd-GD_OP_VERSION-should-not-be-a-released-one.patch
Patch0247: 0247-glusterd-define-GD_OP_VERSION_MAX.patch
Patch0248: 0248-glusterd-cli-mask-out-inaccurate-scrub-statistics.patch
Patch0249: 0249-snapshot-Return-before-redundant-quorum-check.patch
Patch0250: 0250-quota-start-aux-mount-from-glusterd-with-inet-addres.patch
Patch0251: 0251-tier-dht-Default-value-for-demote-freq-max-files-and.patch
Patch0252: 0252-cluster-tier-Ignore-quota-deem-statfs-for-watermark-.patch
Patch0253: 0253-geo-rep-Handle-hardlink-in-Tiering-based-volume.patch
Patch0254: 0254-afr-Fix-excessive-logging-in-afr_accuse_smallfiles.patch
Patch0255: 0255-cluster-tier-Reset-watermarks-in-tier.patch
Patch0256: 0256-libgfapi-glfd-close-is-not-correctly-handled-for-asy.patch
Patch0257: 0257-quota-Fix-incorrect-disk-usage-shown-on-a-tiered-vol.patch
Patch0258: 0258-cluster-tier-Create-linkfiles-to-hardlinks-correctly.patch

%description
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package includes the glusterfs binary, the glusterfsd daemon and the
libglusterfs and glusterfs translator modules common to both GlusterFS server
and client framework.

%package api
Summary:          GlusterFS api library
Group:            System Environment/Daemons
Requires:         %{name} = %{version}-%{release}
Requires:         %{name}-client-xlators = %{version}-%{release}
# we provide the Python package/namespace 'gluster'
#Provides:         python-gluster = %{version}-%{release}

%description api
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the glusterfs libgfapi library.

%package api-devel
Summary:          Development Libraries
Group:            Development/Libraries
Requires:         %{name} = %{version}-%{release}
Requires:         %{name}-devel = %{version}-%{release}
Requires:         libacl-devel

%description api-devel
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the api include files.

%package cli
Summary:          GlusterFS CLI
Group:            Applications/File
Requires:         %{name}-libs = %{version}-%{release}

%description cli
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the GlusterFS CLI application and its man page

%package devel
Summary:          Development Libraries
Group:            Development/Libraries
Requires:         %{name} = %{version}-%{release}
# Needed for the Glupy examples to work
%if ( 0%{!?_without_extra_xlators:1} )
Requires:         %{name}-extra-xlators = %{version}-%{release}
%endif

%description devel
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the development libraries and include files.

%if ( 0%{!?_without_extra_xlators:1} )
%package extra-xlators
Summary:          Extra Gluster filesystem Translators
Group:            Applications/File
# We need python-gluster rpm for gluster module's __init__.py in Python
# site-packages area
Requires:         python-gluster = %{version}-%{release}
Requires:         python python-ctypes

%description extra-xlators
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides extra filesystem Translators, such as Glupy,
for GlusterFS.
%endif

%package fuse
Summary:          Fuse client
Group:            Applications/File
BuildRequires:    fuse-devel
Requires:         attr

Requires:         %{name} = %{version}-%{release}
Requires:         %{name}-client-xlators = %{version}-%{release}

Obsoletes:        %{name}-client < %{version}-%{release}
Provides:         %{name}-client = %{version}-%{release}

%description fuse
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides support to FUSE based clients and inlcudes the
glusterfs(d) binary.

%if ( 0%{?_build_server} )
%package ganesha
Summary:          NFS-Ganesha configuration
Group:            Applications/File

Requires:         %{name}-server = %{version}-%{release}
Requires:         nfs-ganesha-gluster
Requires:         pcs

%description ganesha
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the configuration and related files for using
NFS-Ganesha as the NFS server using GlusterFS
%endif

%if ( 0%{?_build_server} )
%if ( 0%{!?_without_georeplication:1} )
%package geo-replication
Summary:          GlusterFS Geo-replication
Group:            Applications/File
Requires:         %{name} = %{version}-%{release}
Requires:         %{name}-server = %{version}-%{release}
Requires:         python python-ctypes
Requires:         rsync

%description geo-replication
GlusterFS is a distributed file-system capable of scaling to several
peta-bytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file system in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in userspace and easily manageable.

This package provides support to geo-replication.
%endif
%endif

%package libs
Summary:          GlusterFS common libraries
Group:            Applications/File
%if ( 0%{!?_without_syslog:1} )
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} > 6 )
Requires:         rsyslog-mmjsonparse
%endif
%if ( 0%{?rhel} && 0%{?rhel} == 6 )
Requires:         rsyslog-mmcount
%endif
%endif

%description libs
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the base GlusterFS libraries

%package -n python-gluster
Summary:          GlusterFS python library
Group:            Development/Tools
%if ( ! ( 0%{?rhel} && 0%{?rhel} < 6 || 0%{?sles_version} ) )
# EL5 does not support noarch sub-packages
BuildArch:        noarch
%endif
Requires:         python

%description -n python-gluster
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package contains the python modules of GlusterFS and own gluster
namespace.


%if ( 0%{!?_without_rdma:1} )
%package rdma
Summary:          GlusterFS rdma support for ib-verbs
Group:            Applications/File
BuildRequires:    libibverbs-devel
BuildRequires:    librdmacm-devel >= 1.0.15
Requires:         %{name} = %{version}-%{release}

%description rdma
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides support to ib-verbs library.
%endif

%if ( 0%{?_build_server} )
%if ( 0%{!?_without_regression_tests:1} )
%package regression-tests
Summary:          Development Tools
Group:            Development/Tools
Requires:         %{name} = %{version}-%{release}
Requires:         %{name}-fuse = %{version}-%{release}
Requires:         %{name}-server = %{version}-%{release}
## thin provisioning support
Requires:         lvm2 >= 2.02.89
Requires:         perl(App::Prove) perl(Test::Harness) gcc util-linux-ng
Requires:         python attr dbench file git libacl-devel net-tools
Requires:         nfs-utils xfsprogs yajl

%description regression-tests
The Gluster Test Framework, is a suite of scripts used for
regression testing of Gluster.
%endif
%endif

%if ( 0%{?_build_server} )
%if ( 0%{!?_without_ocf:1} )
%package resource-agents
Summary:          OCF Resource Agents for GlusterFS
License:          GPLv3+
%if ( ! ( 0%{?rhel} && 0%{?rhel} < 6 || 0%{?sles_version} ) )
# EL5 does not support noarch sub-packages
BuildArch:        noarch
%endif
# this Group handling comes from the Fedora resource-agents package
%if ( 0%{?fedora} || 0%{?centos_version} || 0%{?rhel} )
Group:            System Environment/Base
%else
Group:            Productivity/Clustering/HA
%endif
# for glusterd
Requires:         %{name}-server
# depending on the distribution, we need pacemaker or resource-agents
Requires:         %{_prefix}/lib/ocf/resource.d

%description resource-agents
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the resource agents which plug glusterd into
Open Cluster Framework (OCF) compliant cluster resource managers,
like Pacemaker.
%endif
%endif

%if ( 0%{?_build_server} )
%package server
Summary:          Clustered file-system server
Group:            System Environment/Daemons
Requires:         %{name} = %{version}-%{release}
Requires:         %{name}-libs = %{version}-%{release}
Requires:         %{name}-cli = %{version}-%{release}
# some daemons (like quota) use a fuse-mount, glusterfsd is part of -fuse
Requires:         %{name}-fuse = %{version}-%{release}
# self-heal daemon, rebalance, nfs-server etc. are actually clients
Requires:         %{name}-client-xlators = %{version}-%{release}
# psmisc for killall, lvm2 for snapshot, and nfs-utils and
# rpcbind/portmap for gnfs server
Requires:         psmisc
Requires:         lvm2
Requires:         nfs-utils
%if ( 0%{?_with_systemd:1} )
Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
%else
Requires(post):   /sbin/chkconfig
Requires(preun):  /sbin/service
Requires(preun):  /sbin/chkconfig
Requires(postun): /sbin/service
%endif
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
Requires:         rpcbind
%else
Requires:         portmap
%endif
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
Obsoletes:        %{name}-geo-replication = %{version}-%{release}
%endif
%if ( 0%{?rhel} && 0%{?rhel} <= 6 )
Requires:         python-argparse
%endif
Requires:         pyxattr

%description server
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the glusterfs server daemon.
%endif

%package client-xlators
Summary:          GlusterFS client-side translators
Group:            Applications/File

%description client-xlators
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the translators needed on any GlusterFS client.

%prep
%setup -q -n %{name}-%{version}%{?prereltag}
# %patch0001 -p1
%patch0002 -p1
%patch0003 -p1
%patch0004 -p1
%patch0005 -p1
%patch0006 -p1
%patch0007 -p1
%patch0008 -p1
%patch0009 -p1
%patch0010 -p1
%patch0011 -p1
%patch0012 -p1
%patch0013 -p1
%patch0014 -p1
%patch0015 -p1
%patch0016 -p1
%patch0017 -p1
%patch0018 -p1
%patch0019 -p1
%patch0020 -p1
%patch0021 -p1
%patch0022 -p1
%patch0023 -p1
%patch0024 -p1
%patch0025 -p1
%patch0026 -p1
%patch0027 -p1
%patch0028 -p1
%patch0029 -p1
%patch0030 -p1
%patch0031 -p1
%patch0032 -p1
%patch0033 -p1
%patch0034 -p1
%patch0035 -p1
%patch0036 -p1
%patch0037 -p1
%patch0038 -p1
%patch0039 -p1
%patch0040 -p1
%patch0041 -p1
%patch0042 -p1
%patch0043 -p1
%patch0044 -p1
%patch0045 -p1
%patch0046 -p1
%patch0047 -p1
%patch0048 -p1
%patch0049 -p1
%patch0050 -p1
%patch0051 -p1
%patch0052 -p1
%patch0053 -p1
%patch0054 -p1
%patch0055 -p1
%patch0056 -p1
%patch0057 -p1
%patch0058 -p1
%patch0059 -p1
%patch0060 -p1
%patch0061 -p1
%patch0062 -p1
%patch0063 -p1
%patch0064 -p1
%patch0065 -p1
%patch0066 -p1
%patch0067 -p1
%patch0068 -p1
%patch0069 -p1
%patch0070 -p1
%patch0071 -p1
%patch0072 -p1
%patch0073 -p1
%patch0074 -p1
%patch0075 -p1
%patch0076 -p1
%patch0077 -p1
%patch0078 -p1
%patch0079 -p1
%patch0080 -p1
%patch0081 -p1
%patch0082 -p1
%patch0083 -p1
%patch0084 -p1
%patch0085 -p1
%patch0086 -p1
%patch0087 -p1
%patch0088 -p1
%patch0089 -p1
%patch0090 -p1
%patch0091 -p1
%patch0092 -p1
%patch0093 -p1
%patch0094 -p1
%patch0095 -p1
%patch0096 -p1
%patch0097 -p1
%patch0098 -p1
%patch0099 -p1
%patch0100 -p1
%patch0101 -p1
%patch0102 -p1
%patch0103 -p1
%patch0104 -p1
%patch0105 -p1
%patch0106 -p1
%patch0107 -p1
%patch0108 -p1
%patch0109 -p1
%patch0110 -p1
%patch0111 -p1
%patch0112 -p1
%patch0113 -p1
%patch0114 -p1
%patch0115 -p1
%patch0116 -p1
%patch0117 -p1
%patch0118 -p1
%patch0119 -p1
%patch0120 -p1
%patch0121 -p1
%patch0122 -p1
%patch0123 -p1
%patch0124 -p1
%patch0125 -p1
%patch0126 -p1
%patch0127 -p1
%patch0128 -p1
%patch0129 -p1
%patch0130 -p1
%patch0131 -p1
%patch0132 -p1
%patch0133 -p1
%patch0134 -p1
%patch0135 -p1
%patch0136 -p1
%patch0137 -p1
%patch0138 -p1
%patch0139 -p1
%patch0140 -p1
%patch0141 -p1
%patch0142 -p1
%patch0143 -p1
%patch0144 -p1
%patch0145 -p1
%patch0146 -p1
%patch0147 -p1
%patch0148 -p1
%patch0149 -p1
%patch0150 -p1
%patch0151 -p1
%patch0152 -p1
%patch0153 -p1
%patch0154 -p1
%patch0155 -p1
%patch0156 -p1
%patch0157 -p1
%patch0158 -p1
%patch0159 -p1
%patch0160 -p1
%patch0161 -p1
%patch0162 -p1
%patch0163 -p1
%patch0164 -p1
%patch0165 -p1
%patch0166 -p1
%patch0167 -p1
%patch0168 -p1
%patch0169 -p1
%patch0170 -p1
%patch0171 -p1
%patch0172 -p1
%patch0173 -p1
%patch0174 -p1
%patch0175 -p1
%patch0176 -p1
%patch0177 -p1
%patch0178 -p1
%patch0179 -p1
%patch0180 -p1
%patch0181 -p1
%patch0182 -p1
%patch0183 -p1
%patch0184 -p1
%patch0185 -p1
%patch0186 -p1
%patch0187 -p1
%patch0188 -p1
%patch0189 -p1
%patch0190 -p1
%patch0191 -p1
%patch0192 -p1
%patch0193 -p1
%patch0194 -p1
%patch0195 -p1
%patch0196 -p1
%patch0197 -p1
%patch0198 -p1
%patch0199 -p1
%patch0200 -p1
%patch0201 -p1
%patch0202 -p1
%patch0203 -p1
%patch0204 -p1
%patch0205 -p1
%patch0206 -p1
%patch0207 -p1
%patch0208 -p1
%patch0209 -p1
%patch0210 -p1
%patch0211 -p1
%patch0212 -p1
%patch0213 -p1
%patch0214 -p1
%patch0215 -p1
%patch0216 -p1
%patch0217 -p1
%patch0218 -p1
%patch0219 -p1
%patch0220 -p1
%patch0221 -p1
%patch0222 -p1
%patch0223 -p1
%patch0224 -p1
%patch0225 -p1
%patch0226 -p1
%patch0227 -p1
%patch0228 -p1
%patch0229 -p1
%patch0230 -p1
%patch0231 -p1
%patch0232 -p1
%patch0233 -p1
%patch0234 -p1
%patch0235 -p1
%patch0236 -p1
%patch0237 -p1
%patch0238 -p1
%patch0239 -p1
%patch0240 -p1
%patch0241 -p1
%patch0242 -p1
%patch0243 -p1
%patch0244 -p1
%patch0245 -p1
%patch0246 -p1
%patch0247 -p1
%patch0248 -p1
%patch0249 -p1
%patch0250 -p1
%patch0251 -p1
%patch0252 -p1
%patch0253 -p1
%patch0254 -p1
%patch0255 -p1
%patch0256 -p1
%patch0257 -p1
%patch0258 -p1

%build
# In RHEL7 few hardening flags are available by default, however the RELRO
# default behaviour is partial, convert to full
%if ( 0%{?rhel} && 0%{?rhel} >= 7 )
LDFLAGS="$RPM_LD_FLAGS -Wl,-z,relro,-z,now"
export LDFLAGS
%else
%if ( 0%{?rhel} && 0%{?rhel} == 6 )
CFLAGS="$RPM_OPT_FLAGS -fPIE -DPIE"
LDFLAGS="$RPM_LD_FLAGS -pie -Wl,-z,relro,-z,now"
%else
#It appears that with gcc-4.1.2 in RHEL5 there is an issue using both -fPIC and
 # -fPIE that makes -z relro not work; -fPIE seems to undo what -fPIC does
CFLAGS="$RPM_OPT_FLAGS"
LDFLAGS="$RPM_LD_FLAGS -Wl,-z,relro,-z,now"
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
CFLAGS="$CFLAGS -DUSE_INSECURE_OPENSSL"
%endif
%endif
export CFLAGS
export LDFLAGS
%endif

./autogen.sh && %configure \
        %{?_with_cmocka} \
        %{?_with_tmpfilesdir} \
        %{?_without_bd} \
        %{?_without_epoll} \
        %{?_without_fusermount} \
        %{?_without_georeplication} \
        %{?_with_firewalld} \
        %{?_without_ocf} \
        %{?_without_qemu_block} \
        %{?_without_rdma} \
        %{?_without_syslog} \
        %{?_without_systemtap} \
        %{?_without_tiering}

# fix hardening and remove rpath in shlibs
%if ( 0%{?fedora} && 0%{?fedora} > 17 ) || ( 0%{?rhel} && 0%{?rhel} > 6 )
sed -i 's| \\\$compiler_flags |&\\\$LDFLAGS |' libtool
%endif
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|' libtool

make %{?_smp_mflags}

# Build Glupy
pushd xlators/features/glupy/src
FLAGS="$RPM_OPT_FLAGS" python setup.py build
popd

%check
make check

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
# install the Glupy Python library in /usr/lib/python*/site-packages
pushd xlators/features/glupy/src
python setup.py install --skip-build --verbose --root %{buildroot}
popd
# Install include directory
mkdir -p %{buildroot}%{_includedir}/glusterfs
install -p -m 0644 libglusterfs/src/*.h \
    %{buildroot}%{_includedir}/glusterfs/
install -p -m 0644 contrib/uuid/*.h \
    %{buildroot}%{_includedir}/glusterfs/
# Following needed by hekafs multi-tenant translator
mkdir -p %{buildroot}%{_includedir}/glusterfs/rpc
install -p -m 0644 rpc/rpc-lib/src/*.h \
    %{buildroot}%{_includedir}/glusterfs/rpc/
install -p -m 0644 rpc/xdr/src/*.h \
    %{buildroot}%{_includedir}/glusterfs/rpc/
mkdir -p %{buildroot}%{_includedir}/glusterfs/server
install -p -m 0644 xlators/protocol/server/src/*.h \
    %{buildroot}%{_includedir}/glusterfs/server/
%if ( 0%{_for_fedora_koji_builds} )
install -D -p -m 0644 %{SOURCE1} \
    %{buildroot}%{_sysconfdir}/sysconfig/glusterd
install -D -p -m 0644 %{SOURCE2} \
    %{buildroot}%{_sysconfdir}/sysconfig/glusterfsd
%else
install -D -p -m 0644 extras/glusterd-sysconfig \
    %{buildroot}%{_sysconfdir}/sysconfig/glusterd
%endif

%if ( 0%{_for_fedora_koji_builds} )
%if ( 0%{?rhel} && 0%{?rhel} <= 5 )
install -D -p -m 0755 %{SOURCE6} \
    %{buildroot}%{_sysconfdir}/sysconfig/modules/glusterfs-fuse.modules
%endif
%endif

mkdir -p %{buildroot}%{_localstatedir}/log/glusterd
mkdir -p %{buildroot}%{_localstatedir}/log/glusterfs
mkdir -p %{buildroot}%{_localstatedir}/log/glusterfsd
mkdir -p %{buildroot}%{_localstatedir}/run/gluster
touch %{buildroot}%{python_sitelib}/gluster/__init__.py


# Remove unwanted files from all the shared libraries
find %{buildroot}%{_libdir} -name '*.a' -delete
find %{buildroot}%{_libdir} -name '*.la' -delete

# Remove installed docs, the ones we want are included by %%doc, in
# /usr/share/doc/glusterfs or /usr/share/doc/glusterfs-x.y.z depending
# on the distribution
%if ( 0%{?fedora} && 0%{?fedora} > 19 ) || ( 0%{?rhel} && 0%{?rhel} > 6 )
rm -rf %{buildroot}%{_pkgdocdir}/*
%else
rm -rf %{buildroot}%{_defaultdocdir}/%{name}
mkdir -p %{buildroot}%{_pkgdocdir}
%endif
head -50 ChangeLog > ChangeLog.head && mv ChangeLog.head ChangeLog
cat << EOM >> ChangeLog

More commit messages for this ChangeLog can be found at
https://forge.gluster.org/glusterfs-core/glusterfs/commits/v%{version}%{?prereltag}
EOM

# Remove benchmarking and other unpackaged files
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
rm -rf %{buildroot}/benchmarking
rm -f %{buildroot}/glusterfs-mode.el
rm -f %{buildroot}/glusterfs.vim
%else
# make install always puts these in %%{_defaultdocdir}/%%{name} so don't
# use %%{_pkgdocdir}; that will be wrong on later Fedora distributions
rm -rf %{buildroot}%{_defaultdocdir}/%{name}/benchmarking
rm -f %{buildroot}%{_defaultdocdir}/%{name}/glusterfs-mode.el
rm -f %{buildroot}%{_defaultdocdir}/%{name}/glusterfs.vim
%endif

# Create working directory
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd

# Update configuration file to /var/lib working directory
sed -i 's|option working-directory /etc/glusterd|option working-directory %{_sharedstatedir}/glusterd|g' \
    %{buildroot}%{_sysconfdir}/glusterfs/glusterd.vol

# Install glusterfsd .service or init.d file
%if ( 0%{_for_fedora_koji_builds} )
%_init_install %{glusterfsd_service} glusterfsd
%endif

install -D -p -m 0644 extras/glusterfs-logrotate \
    %{buildroot}%{_sysconfdir}/logrotate.d/glusterfs

%if ( 0%{!?_without_georeplication:1} )
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/geo-replication
touch %{buildroot}%{_sharedstatedir}/glusterd/geo-replication/gsyncd_template.conf
install -D -p -m 0644 extras/glusterfs-georep-logrotate \
    %{buildroot}%{_sysconfdir}/logrotate.d/glusterfs-georep
%endif

%if ( 0%{!?_without_syslog:1} )
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} > 6 )
install -D -p -m 0644 extras/gluster-rsyslog-7.2.conf \
    %{buildroot}%{_sysconfdir}/rsyslog.d/gluster.conf.example
%endif

%if ( 0%{?rhel} && 0%{?rhel} == 6 )
install -D -p -m 0644 extras/gluster-rsyslog-5.8.conf \
    %{buildroot}%{_sysconfdir}/rsyslog.d/gluster.conf.example
%endif

%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
install -D -p -m 0644 extras/logger.conf.example \
    %{buildroot}%{_sysconfdir}/glusterfs/logger.conf.example
%endif
%endif

touch %{buildroot}%{_sharedstatedir}/glusterd/glusterd.info
touch %{buildroot}%{_sharedstatedir}/glusterd/options
subdirs=("add-brick" "create" "copy-file" "delete" "gsync-create" "remove-brick" "reset" "set" "start" "stop")
for dir in ${subdirs[@]}
do
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/"$dir"/{pre,post}
done
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/glustershd
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/peers
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/vols
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/nfs/run
touch %{buildroot}%{_sharedstatedir}/glusterd/nfs/nfs-server.vol
touch %{buildroot}%{_sharedstatedir}/glusterd/nfs/run/nfs.pid

%{__install} -p -m 0744 extras/hook-scripts/start/post/*.sh   \
    %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/start/post
%{__install} -p -m 0744 extras/hook-scripts/stop/pre/*.sh   \
    %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/stop/pre
%{__install} -p -m 0744 extras/hook-scripts/set/post/*.sh   \
    %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/set/post
%{__install} -p -m 0744 extras/hook-scripts/add-brick/post/*.sh   \
    %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/add-brick/post
%{__install} -p -m 0744 extras/hook-scripts/add-brick/pre/*.sh   \
    %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/add-brick/pre
%{__install} -p -m 0744 extras/hook-scripts/reset/post/*.sh   \
    %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/reset/post
%{__install} -p -m 0744 extras/hook-scripts/S56glusterd-geo-rep-create-post.sh   \
    %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/gsync-create/post


find ./tests ./run-tests.sh -type f | cpio -pd %{buildroot}%{_prefix}/share/glusterfs

## Install bash completion for cli
install -p -m 0744 -D extras/command-completion/gluster.bash \
    %{buildroot}%{_sysconfdir}/bash_completion.d/gluster


%clean
rm -rf %{buildroot}

##-----------------------------------------------------------------------------
## All %post should be placed here and keep them sorted
##
%post
%if ( 0%{!?_without_syslog:1} )
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
%_init_restart rsyslog
%endif
%endif

%post api
/sbin/ldconfig

%post fuse
%if ( 0%{?rhel} == 5 )
modprobe fuse
%endif

%if ( 0%{?_build_server} )
%if ( 0%{!?_without_georeplication:1} )
%post geo-replication
#restart glusterd.
if [ $1 -ge 1 ]; then
    %_init_restart glusterd
fi
%endif
%endif

%post libs
/sbin/ldconfig

%if ( 0%{?_build_server} )
%post server
# Legacy server
%_init_enable glusterd
# fix bz#1110715
if [ -f %_init_glusterfsd ]; then
%_init_enable glusterfsd
fi
# ".cmd_log_history" is renamed to "cmd_history.log" in GlusterFS-3.7 .
# While upgrading glusterfs-server package form GlusterFS version <= 3.6 to
# GlusterFS version 3.7, ".cmd_log_history" should be renamed to
# "cmd_history.log" to retain cli command history contents.
if [ -f %{_localstatedir}/log/glusterfs/.cmd_log_history ]; then
    mv %{_localstatedir}/log/glusterfs/.cmd_log_history \
       %{_localstatedir}/log/glusterfs/cmd_history.log
fi

# Genuine Fedora (and EPEL) builds never put gluster files in /etc; if
# there are any files in /etc from a prior gluster.org install, move them
# to /var/lib. (N.B. Starting with 3.3.0 all gluster files are in /var/lib
# in gluster.org RPMs.) Be careful to copy them on the off chance that
# /etc and /var/lib are on separate file systems
if [ -d /etc/glusterd -a ! -h %{_sharedstatedir}/glusterd ]; then
    mkdir -p %{_sharedstatedir}/glusterd
    cp -a /etc/glusterd %{_sharedstatedir}/glusterd
    rm -rf /etc/glusterd
    ln -sf %{_sharedstatedir}/glusterd /etc/glusterd
fi

# Rename old volfiles in an RPM-standard way.  These aren't actually
# considered package config files, so %%config doesn't work for them.
if [ -d %{_sharedstatedir}/glusterd/vols ]; then
    for file in $(find %{_sharedstatedir}/glusterd/vols -name '*.vol'); do
        newfile=${file}.rpmsave
        echo "warning: ${file} saved as ${newfile}"
        cp ${file} ${newfile}
    done
fi

# add marker translator
# but first make certain that there are no old libs around to bite us
# BZ 834847
if [ -e /etc/ld.so.conf.d/glusterfs.conf ]; then
    rm -f /etc/ld.so.conf.d/glusterfs.conf
    /sbin/ldconfig
fi

%if (0%{?_with_firewalld:1})
#reload service files if firewalld running
if $(systemctl is-active firewalld 1>/dev/null 2>&1); then
  #firewalld-filesystem is not available for rhel7, so command used for reload.
  firewall-cmd  --reload
fi
%endif

pidof -c -o %PPID -x glusterd &> /dev/null
if [ $? -eq 0 ]; then
    kill -9 `pgrep -f gsyncd.py` &> /dev/null

    killall --wait glusterd &> /dev/null
    glusterd --xlator-option *.upgrade=on -N

    #Cleaning leftover glusterd socket file which is created by glusterd in
    #rpm_script_t context.
    rm -rf /var/run/glusterd.socket

    # glusterd _was_ running, we killed it, it exited after *.upgrade=on,
    # so start it again
    %_init_start glusterd
else
    glusterd --xlator-option *.upgrade=on -N

    #Cleaning leftover glusterd socket file which is created by glusterd in
    #rpm_script_t context.
    rm -rf /var/run/glusterd.socket
fi
%endif

##-----------------------------------------------------------------------------
## All %preun should be placed here and keep them sorted
##
%if ( 0%{?_build_server} )
%preun server
if [ $1 -eq 0 ]; then
    if [ -f %_init_glusterfsd ]; then
        %_init_stop glusterfsd
    fi
    %_init_stop glusterd
    if [ -f %_init_glusterfsd ]; then
        %_init_disable glusterfsd
    fi
    %_init_disable glusterd
fi
if [ $1 -ge 1 ]; then
    if [ -f %_init_glusterfsd ]; then
        %_init_restart glusterfsd
    fi
    %_init_restart glusterd
fi
%endif

##-----------------------------------------------------------------------------
## All %postun should be placed here and keep them sorted
##
%postun
/sbin/ldconfig
%if ( 0%{!?_without_syslog:1} )
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
%_init_restart rsyslog
%endif
%endif

%postun api
/sbin/ldconfig

%if ( 0%{?_build_server} )
%postun server
%if (0%{?_with_firewalld:1})
#reload service files if firewalld running
if $(systemctl is-active firewalld 1>/dev/null 2>&1); then
    firewall-cmd  --reload
fi
%endif
%endif


%postun libs
/sbin/ldconfig

##-----------------------------------------------------------------------------
## All files should be placed here and keep them grouped
##
%files
# exclude extra-xlators files
%if ( ! 0%{!?_without_extra_xlators:1} )
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/encryption/rot-13.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/mac-compat.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/prot_client.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/prot_dht.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/prot_server.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/quiesce.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/testing/features/template.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/testing/performance/symlink-cache.so
%exclude %{python_sitelib}/*
%endif
# exclude regression-tests files
%if ( ! 0%{!?_without_regression_tests:1} )
%exclude %{_prefix}/share/glusterfs/run-tests.sh
%exclude %{_prefix}/share/glusterfs/tests/*
%endif
%if ( ! 0%{?_build_server} )
# exclude ganesha files
%exclude %{_sysconfdir}/ganesha/*
%exclude %{_libexecdir}/ganesha/*
%exclude %{_prefix}/lib/ocf/*
# exclude incrementalapi
%exclude %{_libexecdir}/glusterfs/*
%exclude %{_sbindir}/gfind_missing_files
%exclude %{_libexecdir}/glusterfs/glusterfind
%exclude %{_bindir}/glusterfind
%exclude %{_libexecdir}/glusterfs/peer_add_secret_pub
# exclude server files
%exclude %{_sharedstatedir}/glusterd/*
%exclude %{_sysconfdir}/glusterfs
%exclude %{_sysconfdir}/glusterfs/glusterd.vol
%exclude %{_sysconfdir}/glusterfs/glusterfs-georep-logrotate
%exclude %{_sysconfdir}/glusterfs/glusterfs-logrotate
%exclude %{_sysconfdir}/glusterfs/gluster-rsyslog-5.8.conf
%exclude %{_sysconfdir}/glusterfs/gluster-rsyslog-7.2.conf
%exclude %{_sysconfdir}/glusterfs/group-virt.example
%exclude %{_sysconfdir}/glusterfs/logger.conf.example
%exclude %_init_glusterd
%exclude %{_sysconfdir}/sysconfig/glusterd
%exclude %{_bindir}/glusterfind
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/cluster/pump.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/arbiter.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/bit-rot.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/bitrot-stub.so
%if ( 0%{!?_without_tiering:1} )
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/changetimerecorder.so
%endif
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/index.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/locks.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/posix*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/snapview-server.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/marker.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/quota*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/trash.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/upcall.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mgmt*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/nfs*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/protocol/server*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/storage*
%if ( 0%{!?_without_tiering:1} )
%exclude %{_libdir}/libgfdb.so.*
%endif
%exclude %{_sbindir}/gcron.py
%exclude %{_sbindir}/glfsheal
%exclude %{_sbindir}/glusterd
%exclude %{_sbindir}/snap_scheduler.py
%exclude %{_datadir}/glusterfs/scripts/stop-all-gluster-processes.sh
#/usr/share/doc/glusterfs-server-3.7.0beta2/clear_xattrs.sh
%exclude %{_localstatedir}/run/gluster
%if 0%{?_tmpfilesdir:1}
%exclude %{_tmpfilesdir}/gluster.conf
%endif
%if ( 0%{?_with_firewalld:1} )
%exclude /usr/lib/firewalld/services/glusterfs.xml
%endif
%endif
%doc ChangeLog COPYING-GPLV2 COPYING-LGPLV3 INSTALL README.md THANKS
%if ( 0%{!?_without_syslog:1} )
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
%{_sysconfdir}/rsyslog.d/gluster.conf.example
%endif
%endif
%{_mandir}/man8/*gluster*.8*
%exclude %{_mandir}/man8/gluster.8*
%dir %{_localstatedir}/log/glusterfs
%if ( 0%{!?_without_rdma:1} )
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/rpc-transport/rdma*
%endif
%dir %{_datadir}/glusterfs/scripts
%{_datadir}/glusterfs/scripts/post-upgrade-script-for-quota.sh
%{_datadir}/glusterfs/scripts/pre-upgrade-script-for-quota.sh
# xlators that are needed on the client- and on the server-side
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/auth
%{_libdir}/glusterfs/%{version}%{?prereltag}/auth/addr.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/auth/login.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/rpc-transport
%{_libdir}/glusterfs/%{version}%{?prereltag}/rpc-transport/socket.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/debug
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/debug/error-gen.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/debug/io-stats.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/debug/trace.so
%if ( ! ( 0%{?rhel} && 0%{?rhel} < 6 ) )
# RHEL-5 based distributions have a too old openssl
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/encryption/crypt.so
%endif
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/access-control.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/barrier.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/cdc.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/changelog.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/gfid-access.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/read-only.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/shard.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/snapview-client.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/worm.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/meta.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/io-cache.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/io-threads.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/md-cache.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/open-behind.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/quick-read.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/read-ahead.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/readdir-ahead.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/stat-prefetch.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/write-behind.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/system/posix-acl.so


%files api
%exclude %{_libdir}/*.so
# libgfapi files
%{_libdir}/libgfapi.*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mount/api.so

%files api-devel
%{_libdir}/pkgconfig/glusterfs-api.pc
%{_libdir}/libgfapi.so
%{_includedir}/glusterfs/api/*

%files cli
%{_sbindir}/gluster
%{_mandir}/man8/gluster.8*
%{_sysconfdir}/bash_completion.d/gluster

%files devel
%{_includedir}/glusterfs
%exclude %{_includedir}/glusterfs/y.tab.h
%exclude %{_includedir}/glusterfs/api
%exclude %{_libdir}/libgfapi.so
%if ( ! 0%{?_build_server} )
%exclude %{_libdir}/libgfchangelog.so
%endif
%if ( 0%{!?_without_tiering:1} && ! 0%{?_build_server})
%exclude %{_libdir}/libgfdb.so
%endif
%{_libdir}/*.so
# Glupy Translator examples
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy/debug-trace.*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy/helloworld.*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy/negative.*
%if ( 0%{?_build_server} )
%{_libdir}/pkgconfig/libgfchangelog.pc
%else
%exclude %{_libdir}/pkgconfig/libgfchangelog.pc
%endif
%if ( 0%{!?_without_tiering:1} && 0%{?_build_server})
%{_libdir}/pkgconfig/libgfdb.pc
%else
%if ( 0%{?rhel} && 0%{?rhel} >= 6 )
%exclude %{_libdir}/pkgconfig/libgfdb.pc
%endif
%endif

%files client-xlators
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/cluster/*.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/cluster/pump.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/ganesha.so
%if ( 0%{!?_without_qemu_block:1} )
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/qemu-block.so
%endif
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/protocol/client.so

%if ( 0%{!?_without_extra_xlators:1} )
%files extra-xlators
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/encryption/rot-13.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/mac-compat.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/prot_client.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/prot_dht.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/prot_server.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/quiesce.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/testing/features/template.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/testing/performance/symlink-cache.so
# Glupy Python files
%{python_sitelib}/gluster/glupy/*
# Don't expect a .egg-info file on EL5
%if ( ! ( 0%{?rhel} && 0%{?rhel} < 6 ) )
%{python_sitelib}/glusterfs_glupy*.egg-info
%endif
%endif

%files fuse
# glusterfs is a symlink to glusterfsd, -server depends on -fuse.
%{_sbindir}/glusterfs
%{_sbindir}/glusterfsd
%config(noreplace) %{_sysconfdir}/logrotate.d/glusterfs
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mount/fuse.so
/sbin/mount.glusterfs
%if ( 0%{!?_without_fusermount:1} )
%{_bindir}/fusermount-glusterfs
%endif
%if ( 0%{_for_fedora_koji_builds} )
%if ( 0%{?rhel} && 0%{?rhel} <= 5 )
%{_sysconfdir}/sysconfig/modules/glusterfs-fuse.modules
%endif
%endif

%if ( 0%{?_build_server} )
%files ganesha
%{_sysconfdir}/ganesha/*
%attr(0755,-,-) %{_libexecdir}/ganesha/*
%attr(0755,-,-) %{_prefix}/lib/ocf/resource.d/heartbeat/*
%endif

%if ( 0%{?_build_server} )
%if ( 0%{!?_without_georeplication:1} )
%files geo-replication
%config(noreplace) %{_sysconfdir}/logrotate.d/glusterfs-georep
%{_libexecdir}/glusterfs/gsyncd
%{_libexecdir}/glusterfs/python/syncdaemon/*
%{_libexecdir}/glusterfs/gverify.sh
%{_libexecdir}/glusterfs/set_geo_rep_pem_keys.sh
%{_libexecdir}/glusterfs/peer_gsec_create
%{_libexecdir}/glusterfs/peer_mountbroker
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/geo-replication
%{_sharedstatedir}/glusterd/hooks/1/gsync-create/post/S56glusterd-geo-rep-create-post.sh
%{_datadir}/glusterfs/scripts/get-gfid.sh
%{_datadir}/glusterfs/scripts/slave-upgrade.sh
%{_datadir}/glusterfs/scripts/gsync-upgrade.sh
%{_datadir}/glusterfs/scripts/generate-gfid-file.sh
%{_datadir}/glusterfs/scripts/gsync-sync-gfid
%ghost %attr(0644,-,-) %{_sharedstatedir}/glusterd/geo-replication/gsyncd_template.conf
%endif
%{_libexecdir}/glusterfs/gfind_missing_files
%{_sbindir}/gfind_missing_files
%endif

%files libs
%{_libdir}/*.so.*
%exclude %{_libdir}/libgfapi.*
%if ( 0%{!?_without_tiering:1} )
# libgfdb is only needed server-side
%exclude %{_libdir}/libgfdb.*
%endif

%files -n python-gluster
# introducing glusterfs module in site packages.
# so that all other gluster submodules can reside in the same namespace.
%{python_sitelib}/gluster/__init__.*

%if ( 0%{!?_without_rdma:1} )
%files rdma
%{_libdir}/glusterfs/%{version}%{?prereltag}/rpc-transport/rdma*
%endif

%if ( 0%{?_build_server} )
%if ( 0%{!?_without_regression_tests:1} )
%files regression-tests
%{_prefix}/share/glusterfs/run-tests.sh
%{_prefix}/share/glusterfs/tests
%exclude %{_prefix}/share/glusterfs/tests/basic/rpm.t
%endif
%endif

%if ( 0%{?_build_server} )
%if ( 0%{!?_without_ocf:1} )
%files resource-agents
# /usr/lib is the standard for OCF, also on x86_64
%{_prefix}/lib/ocf/resource.d/glusterfs
%endif
%endif

%if ( 0%{?_build_server} )
%files server
%exclude %{_sharedstatedir}/glusterd/hooks/1/gsync-create/post/S56glusterd-geo-rep-create-post.sh
%doc extras/clear_xattrs.sh
%config(noreplace) %{_sysconfdir}/sysconfig/glusterd
%config(noreplace) %{_sysconfdir}/glusterfs
%dir %{_localstatedir}/run/gluster
%if 0%{?_tmpfilesdir:1}
%{_tmpfilesdir}/gluster.conf
%endif
%dir %{_sharedstatedir}/glusterd
%{_sharedstatedir}/glusterd/*
%config(noreplace) %{_sharedstatedir}/glusterd/groups/virt
# Legacy configs
%if ( 0%{_for_fedora_koji_builds} )
%config(noreplace) %{_sysconfdir}/sysconfig/glusterfsd
%endif
%config %{_sharedstatedir}/glusterd/hooks/1/add-brick/post/disabled-quota-root-xattr-heal.sh
%config %{_sharedstatedir}/glusterd/hooks/1/add-brick/pre/S28Quota-enable-root-xattr-heal.sh
%config %{_sharedstatedir}/glusterd/hooks/1/set/post/S30samba-set.sh
%config %{_sharedstatedir}/glusterd/hooks/1/set/post/S32gluster_enable_shared_storage.sh
%config %{_sharedstatedir}/glusterd/hooks/1/start/post/S29CTDBsetup.sh
%config %{_sharedstatedir}/glusterd/hooks/1/start/post/S30samba-start.sh
%config %{_sharedstatedir}/glusterd/hooks/1/start/post/S31ganesha-start.sh
%config %{_sharedstatedir}/glusterd/hooks/1/stop/pre/S30samba-stop.sh
%config %{_sharedstatedir}/glusterd/hooks/1/stop/pre/S29CTDB-teardown.sh
%config %{_sharedstatedir}/glusterd/hooks/1/reset/post/S31ganesha-reset.sh
# init files
%_init_glusterd
%if ( 0%{_for_fedora_koji_builds} )
%_init_glusterfsd
%endif
# binaries
%{_sbindir}/glusterd
%{_sbindir}/glfsheal
# {_sbindir}/glusterfsd is the actual binary, but glusterfs (client) is a
# symlink. The binary itself (and symlink) are part of the glusterfs-fuse
# package, because glusterfs-server depends on that anyway.
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/cluster/pump.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/arbiter.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/bit-rot.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/bitrot-stub.so
%if ( 0%{!?_without_tiering:1} )
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/changetimerecorder.so
%endif
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/index.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/locks.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/posix*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/snapview-server.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/marker.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/quota*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/trash.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/upcall.so
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mgmt*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/nfs*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/protocol/server*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/storage*
%if ( 0%{!?_without_tiering:1} )
%{_libdir}/libgfdb.so.*
%endif

#snap_scheduler
%{_sbindir}/snap_scheduler.py
%{_sbindir}/gcron.py

#hookscripts
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick/post
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick/pre
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/set
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/set/post
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/start
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/start/post
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/stop
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/stop/pre
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/delete
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/delete/post

%ghost %attr(0644,-,-) %config(noreplace) %{_sharedstatedir}/glusterd/glusterd.info
%ghost %attr(0600,-,-) %{_sharedstatedir}/glusterd/options
%ghost %attr(0600,-,-) %{_sharedstatedir}/glusterd/nfs/nfs-server.vol
%ghost %attr(0600,-,-) %{_sharedstatedir}/glusterd/nfs/run/nfs.pid

# Extra utility script
%{_datadir}/glusterfs/scripts/stop-all-gluster-processes.sh

# Incrementalapi
%{_libexecdir}/glusterfs/glusterfind
%{_bindir}/glusterfind
%{_libexecdir}/glusterfs/peer_add_secret_pub
%{_sharedstatedir}/glusterd/hooks/1/delete/post/S57glusterfind-delete-post.py

%if ( 0%{?_with_firewalld:1} )
/usr/lib/firewalld/services/glusterfs.xml
%endif
%endif


##-----------------------------------------------------------------------------
## All %pretrans should be placed here and keep them sorted
##
%if 0%{?_build_server}
%pretrans -p <lua>
if not posix.access("/bin/bash", "x") then
    -- initial installation, no shell, no running glusterfsd
    return 0
end

-- TODO: move this completely to a lua script
-- For now, we write a temporary bash script and execute that.

script = [[#!/bin/sh
pidof -c -o %PPID -x glusterfsd &>/dev/null

if [ $? -eq 0 ]; then
   pushd . > /dev/null 2>&1
   for volume in /var/lib/glusterd/vols/*; do cd $volume;
       vol_type=`grep '^type=' info | awk -F'=' '{print $2}'`
       volume_started=`grep '^status=' info | awk -F'=' '{print $2}'`
       if [ $vol_type -eq 0 ] && [ $volume_started -eq 1 ] ; then
          echo "ERROR: Distribute volumes detected. In-service rolling upgrade requires distribute volume(s) to be stopped."
          echo "ERROR: Please stop distribute volume(s) before proceeding... exiting!"
          exit 1;
       fi
   done

   popd > /dev/null 2>&1
   echo "WARNING: Updating glusterfs requires its processes to be killed. This action does NOT incur downtime."
   echo "WARNING: Ensure to wait for the upgraded server to finish healing before proceeding."
   echo "WARNING: Refer upgrade section of install guide for more details"
   echo "Please run # service glusterd stop; pkill glusterfs; pkill glusterfsd; pkill gsyncd.py;"
   exit 1;
fi
]]

-- rpm in RHEL5 does not have os.tmpname()
-- io.tmpfile() can not be resolved to a filename to pass to bash :-/
tmpname = "/tmp/glusterfs_pretrans_" .. os.date("%s")
tmpfile = io.open(tmpname, "w")
tmpfile:write(script)
tmpfile:close()
ok, how, val = os.execute("/bin/bash " .. tmpname)
os.remove(tmpname)
if not (ok == 0) then
   error("Detected running glusterfs processes", ok)
end



%pretrans api -p <lua>
if not posix.access("/bin/bash", "x") then
    -- initial installation, no shell, no running glusterfsd
    return 0
end

-- TODO: move this completely to a lua script
-- For now, we write a temporary bash script and execute that.

script = [[#!/bin/sh
pidof -c -o %PPID -x glusterfsd &>/dev/null

if [ $? -eq 0 ]; then
   pushd . > /dev/null 2>&1
   for volume in /var/lib/glusterd/vols/*; do cd $volume;
       vol_type=`grep '^type=' info | awk -F'=' '{print $2}'`
       volume_started=`grep '^status=' info | awk -F'=' '{print $2}'`
       if [ $vol_type -eq 0 ] && [ $volume_started -eq 1 ] ; then
          exit 1;
       fi
   done

   popd > /dev/null 2>&1
   exit 1;
fi
]]

-- rpm in RHEL5 does not have os.tmpname()
-- io.tmpfile() can not be resolved to a filename to pass to bash :-/
tmpname = "/tmp/glusterfs-api_pretrans_" .. os.date("%s")
tmpfile = io.open(tmpname, "w")
tmpfile:write(script)
tmpfile:close()
ok, how, val = os.execute("/bin/bash " .. tmpname)
os.remove(tmpname)
if not (ok == 0) then
   error("Detected running glusterfs processes", ok)
end



%pretrans api-devel -p <lua>
if not posix.access("/bin/bash", "x") then
    -- initial installation, no shell, no running glusterfsd
    return 0
end

-- TODO: move this completely to a lua script
-- For now, we write a temporary bash script and execute that.

script = [[#!/bin/sh
pidof -c -o %PPID -x glusterfsd &>/dev/null

if [ $? -eq 0 ]; then
   pushd . > /dev/null 2>&1
   for volume in /var/lib/glusterd/vols/*; do cd $volume;
       vol_type=`grep '^type=' info | awk -F'=' '{print $2}'`
       volume_started=`grep '^status=' info | awk -F'=' '{print $2}'`
       if [ $vol_type -eq 0 ] && [ $volume_started -eq 1 ] ; then
          exit 1;
       fi
   done

   popd > /dev/null 2>&1
   exit 1;
fi
]]

-- rpm in RHEL5 does not have os.tmpname()
-- io.tmpfile() can not be resolved to a filename to pass to bash :-/
tmpname = "/tmp/glusterfs-api-devel_pretrans_" .. os.date("%s")
tmpfile = io.open(tmpname, "w")
tmpfile:write(script)
tmpfile:close()
ok, how, val = os.execute("/bin/bash " .. tmpname)
os.remove(tmpname)
if not (ok == 0) then
   error("Detected running glusterfs processes", ok)
end



%pretrans cli -p <lua>
if not posix.access("/bin/bash", "x") then
    -- initial installation, no shell, no running glusterfsd
    return 0
end

-- TODO: move this completely to a lua script
-- For now, we write a temporary bash script and execute that.

script = [[#!/bin/sh
pidof -c -o %PPID -x glusterfsd &>/dev/null

if [ $? -eq 0 ]; then
   pushd . > /dev/null 2>&1
   for volume in /var/lib/glusterd/vols/*; do cd $volume;
       vol_type=`grep '^type=' info | awk -F'=' '{print $2}'`
       volume_started=`grep '^status=' info | awk -F'=' '{print $2}'`
       if [ $vol_type -eq 0 ] && [ $volume_started -eq 1 ] ; then
          exit 1;
       fi
   done

   popd > /dev/null 2>&1
   exit 1;
fi
]]

-- rpm in RHEL5 does not have os.tmpname()
-- io.tmpfile() can not be resolved to a filename to pass to bash :-/
tmpname = "/tmp/glusterfs-cli_pretrans_" .. os.date("%s")
tmpfile = io.open(tmpname, "w")
tmpfile:write(script)
tmpfile:close()
ok, how, val = os.execute("/bin/bash " .. tmpname)
os.remove(tmpname)
if not (ok == 0) then
   error("Detected running glusterfs processes", ok)
end



%pretrans client-xlators -p <lua>
if not posix.access("/bin/bash", "x") then
    -- initial installation, no shell, no running glusterfsd
    return 0
end

-- TODO: move this completely to a lua script
-- For now, we write a temporary bash script and execute that.

script = [[#!/bin/sh
pidof -c -o %PPID -x glusterfsd &>/dev/null

if [ $? -eq 0 ]; then
   pushd . > /dev/null 2>&1
   for volume in /var/lib/glusterd/vols/*; do cd $volume;
       vol_type=`grep '^type=' info | awk -F'=' '{print $2}'`
       volume_started=`grep '^status=' info | awk -F'=' '{print $2}'`
       if [ $vol_type -eq 0 ] && [ $volume_started -eq 1 ] ; then
          exit 1;
       fi
   done

   popd > /dev/null 2>&1
   exit 1;
fi
]]

-- rpm in RHEL5 does not have os.tmpname()
-- io.tmpfile() can not be resolved to a filename to pass to bash :-/
tmpname = "/tmp/glusterfs-client-xlators_pretrans_" .. os.date("%s")
tmpfile = io.open(tmpname, "w")
tmpfile:write(script)
tmpfile:close()
ok, how, val = os.execute("/bin/bash " .. tmpname)
os.remove(tmpname)
if not (ok == 0) then
   error("Detected running glusterfs processes", ok)
end



%pretrans devel -p <lua>
if not posix.access("/bin/bash", "x") then
    -- initial installation, no shell, no running glusterfsd
    return 0
end

-- TODO: move this completely to a lua script
-- For now, we write a temporary bash script and execute that.

script = [[#!/bin/sh
pidof -c -o %PPID -x glusterfsd &>/dev/null

if [ $? -eq 0 ]; then
   pushd . > /dev/null 2>&1
   for volume in /var/lib/glusterd/vols/*; do cd $volume;
       vol_type=`grep '^type=' info | awk -F'=' '{print $2}'`
       volume_started=`grep '^status=' info | awk -F'=' '{print $2}'`
       if [ $vol_type -eq 0 ] && [ $volume_started -eq 1 ] ; then
          exit 1;
       fi
   done

   popd > /dev/null 2>&1
   exit 1;
fi
]]

-- rpm in RHEL5 does not have os.tmpname()
-- io.tmpfile() can not be resolved to a filename to pass to bash :-/
tmpname = "/tmp/glusterfs-devel_pretrans_" .. os.date("%s")
tmpfile = io.open(tmpname, "w")
tmpfile:write(script)
tmpfile:close()
ok, how, val = os.execute("/bin/bash " .. tmpname)
os.remove(tmpname)
if not (ok == 0) then
   error("Detected running glusterfs processes", ok)
end



%pretrans fuse -p <lua>
if not posix.access("/bin/bash", "x") then
    -- initial installation, no shell, no running glusterfsd
    return 0
end

-- TODO: move this completely to a lua script
-- For now, we write a temporary bash script and execute that.

script = [[#!/bin/sh
pidof -c -o %PPID -x glusterfsd &>/dev/null

if [ $? -eq 0 ]; then
   pushd . > /dev/null 2>&1
   for volume in /var/lib/glusterd/vols/*; do cd $volume;
       vol_type=`grep '^type=' info | awk -F'=' '{print $2}'`
       volume_started=`grep '^status=' info | awk -F'=' '{print $2}'`
       if [ $vol_type -eq 0 ] && [ $volume_started -eq 1 ] ; then
          exit 1;
       fi
   done

   popd > /dev/null 2>&1
   exit 1;
fi
]]

-- rpm in RHEL5 does not have os.tmpname()
-- io.tmpfile() can not be resolved to a filename to pass to bash :-/
tmpname = "/tmp/glusterfs-fuse_pretrans_" .. os.date("%s")
tmpfile = io.open(tmpname, "w")
tmpfile:write(script)
tmpfile:close()
ok, how, val = os.execute("/bin/bash " .. tmpname)
os.remove(tmpname)
if not (ok == 0) then
   error("Detected running glusterfs processes", ok)
end



%pretrans ganesha -p <lua>
if not posix.access("/bin/bash", "x") then
    -- initial installation, no shell, no running glusterfsd
    return 0
end

-- TODO: move this completely to a lua script
-- For now, we write a temporary bash script and execute that.

script = [[#!/bin/sh
pidof -c -o %PPID -x glusterfsd &>/dev/null

if [ $? -eq 0 ]; then
   pushd . > /dev/null 2>&1
   for volume in /var/lib/glusterd/vols/*; do cd $volume;
       vol_type=`grep '^type=' info | awk -F'=' '{print $2}'`
       volume_started=`grep '^status=' info | awk -F'=' '{print $2}'`
       if [ $vol_type -eq 0 ] && [ $volume_started -eq 1 ] ; then
          exit 1;
       fi
   done

   popd > /dev/null 2>&1
   exit 1;
fi
]]

-- rpm in RHEL5 does not have os.tmpname()
-- io.tmpfile() can not be resolved to a filename to pass to bash :-/
tmpname = "/tmp/glusterfs-ganesha_pretrans_" .. os.date("%s")
tmpfile = io.open(tmpname, "w")
tmpfile:write(script)
tmpfile:close()
ok, how, val = os.execute("/bin/bash " .. tmpname)
os.remove(tmpname)
if not (ok == 0) then
   error("Detected running glusterfs processes", ok)
end



%if ( 0%{!?_without_georeplication:1} )
%pretrans geo-replication -p <lua>
if not posix.access("/bin/bash", "x") then
    -- initial installation, no shell, no running glusterfsd
    return 0
end

-- TODO: move this completely to a lua script
-- For now, we write a temporary bash script and execute that.

script = [[#!/bin/sh
pidof -c -o %PPID -x glusterfsd &>/dev/null

if [ $? -eq 0 ]; then
   pushd . > /dev/null 2>&1
   for volume in /var/lib/glusterd/vols/*; do cd $volume;
       vol_type=`grep '^type=' info | awk -F'=' '{print $2}'`
       volume_started=`grep '^status=' info | awk -F'=' '{print $2}'`
       if [ $vol_type -eq 0 ] && [ $volume_started -eq 1 ] ; then
          exit 1;
       fi
   done

   popd > /dev/null 2>&1
   exit 1;
fi
]]

-- rpm in RHEL5 does not have os.tmpname()
-- io.tmpfile() can not be resolved to a filename to pass to bash :-/
tmpname = "/tmp/glusterfs-geo-replication_pretrans_" .. os.date("%s")
tmpfile = io.open(tmpname, "w")
tmpfile:write(script)
tmpfile:close()
ok, how, val = os.execute("/bin/bash " .. tmpname)
os.remove(tmpname)
if not (ok == 0) then
   error("Detected running glusterfs processes", ok)
end
%endif



%pretrans libs -p <lua>
if not posix.access("/bin/bash", "x") then
    -- initial installation, no shell, no running glusterfsd
    return 0
end

-- TODO: move this completely to a lua script
-- For now, we write a temporary bash script and execute that.

script = [[#!/bin/sh
pidof -c -o %PPID -x glusterfsd &>/dev/null

if [ $? -eq 0 ]; then
   pushd . > /dev/null 2>&1
   for volume in /var/lib/glusterd/vols/*; do cd $volume;
       vol_type=`grep '^type=' info | awk -F'=' '{print $2}'`
       volume_started=`grep '^status=' info | awk -F'=' '{print $2}'`
       if [ $vol_type -eq 0 ] && [ $volume_started -eq 1 ] ; then
          exit 1;
       fi
   done

   popd > /dev/null 2>&1
   exit 1;
fi
]]

-- rpm in RHEL5 does not have os.tmpname()
-- io.tmpfile() can not be resolved to a filename to pass to bash :-/
tmpname = "/tmp/glusterfs-libs_pretrans_" .. os.date("%s")
tmpfile = io.open(tmpname, "w")
tmpfile:write(script)
tmpfile:close()
ok, how, val = os.execute("/bin/bash " .. tmpname)
os.remove(tmpname)
if not (ok == 0) then
   error("Detected running glusterfs processes", ok)
end



%pretrans -n python-gluster -p <lua>
if not posix.access("/bin/bash", "x") then
    -- initial installation, no shell, no running glusterfsd
    return 0
end

-- TODO: move this completely to a lua script
-- For now, we write a temporary bash script and execute that.

script = [[#!/bin/sh
pidof -c -o %PPID -x glusterfsd &>/dev/null

if [ $? -eq 0 ]; then
   pushd . > /dev/null 2>&1
   for volume in /var/lib/glusterd/vols/*; do cd $volume;
       vol_type=`grep '^type=' info | awk -F'=' '{print $2}'`
       volume_started=`grep '^status=' info | awk -F'=' '{print $2}'`
       if [ $vol_type -eq 0 ] && [ $volume_started -eq 1 ] ; then
          exit 1;
       fi
   done

   popd > /dev/null 2>&1
   exit 1;
fi
]]

-- rpm in RHEL5 does not have os.tmpname()
-- io.tmpfile() can not be resolved to a filename to pass to bash :-/
tmpname = "/tmp/python-gluster_pretrans_" .. os.date("%s")
tmpfile = io.open(tmpname, "w")
tmpfile:write(script)
tmpfile:close()
ok, how, val = os.execute("/bin/bash " .. tmpname)
os.remove(tmpname)
if not (ok == 0) then
   error("Detected running glusterfs processes", ok)
end



%if ( 0%{!?_without_rdma:1} )
%pretrans rdma -p <lua>
if not posix.access("/bin/bash", "x") then
    -- initial installation, no shell, no running glusterfsd
    return 0
end

-- TODO: move this completely to a lua script
-- For now, we write a temporary bash script and execute that.

script = [[#!/bin/sh
pidof -c -o %PPID -x glusterfsd &>/dev/null

if [ $? -eq 0 ]; then
   pushd . > /dev/null 2>&1
   for volume in /var/lib/glusterd/vols/*; do cd $volume;
       vol_type=`grep '^type=' info | awk -F'=' '{print $2}'`
       volume_started=`grep '^status=' info | awk -F'=' '{print $2}'`
       if [ $vol_type -eq 0 ] && [ $volume_started -eq 1 ] ; then
          exit 1;
       fi
   done

   popd > /dev/null 2>&1
   exit 1;
fi
]]

-- rpm in RHEL5 does not have os.tmpname()
-- io.tmpfile() can not be resolved to a filename to pass to bash :-/
tmpname = "/tmp/glusterfs-rdma_pretrans_" .. os.date("%s")
tmpfile = io.open(tmpname, "w")
tmpfile:write(script)
tmpfile:close()
ok, how, val = os.execute("/bin/bash " .. tmpname)
os.remove(tmpname)
if not (ok == 0) then
   error("Detected running glusterfs processes", ok)
end
%endif



%if ( 0%{!?_without_ocf:1} )
%pretrans resource-agents -p <lua>
if not posix.access("/bin/bash", "x") then
    -- initial installation, no shell, no running glusterfsd
    return 0
end

-- TODO: move this completely to a lua script
-- For now, we write a temporary bash script and execute that.

script = [[#!/bin/sh
pidof -c -o %PPID -x glusterfsd &>/dev/null

if [ $? -eq 0 ]; then
   pushd . > /dev/null 2>&1
   for volume in /var/lib/glusterd/vols/*; do cd $volume;
       vol_type=`grep '^type=' info | awk -F'=' '{print $2}'`
       volume_started=`grep '^status=' info | awk -F'=' '{print $2}'`
       if [ $vol_type -eq 0 ] && [ $volume_started -eq 1 ] ; then
          exit 1;
       fi
   done

   popd > /dev/null 2>&1
   exit 1;
fi
]]

-- rpm in RHEL5 does not have os.tmpname()
-- io.tmpfile() can not be resolved to a filename to pass to bash :-/
tmpname = "/tmp/glusterfs-resource-agents_pretrans_" .. os.date("%s")
tmpfile = io.open(tmpname, "w")
tmpfile:write(script)
tmpfile:close()
ok, how, val = os.execute("/bin/bash " .. tmpname)
os.remove(tmpname)
if not (ok == 0) then
   error("Detected running glusterfs processes", ok)
end
%endif



%pretrans server -p <lua>
if not posix.access("/bin/bash", "x") then
    -- initial installation, no shell, no running glusterfsd
    return 0
end

-- TODO: move this completely to a lua script
-- For now, we write a temporary bash script and execute that.

script = [[#!/bin/sh
pidof -c -o %PPID -x glusterfsd &>/dev/null

if [ $? -eq 0 ]; then
   pushd . > /dev/null 2>&1
   for volume in /var/lib/glusterd/vols/*; do cd $volume;
       vol_type=`grep '^type=' info | awk -F'=' '{print $2}'`
       volume_started=`grep '^status=' info | awk -F'=' '{print $2}'`
       if [ $vol_type -eq 0 ] && [ $volume_started -eq 1 ] ; then
          exit 1;
       fi
   done

   popd > /dev/null 2>&1
   exit 1;
fi
]]

-- rpm in RHEL5 does not have os.tmpname()
-- io.tmpfile() can not be resolved to a filename to pass to bash :-/
tmpname = "/tmp/glusterfs-server_pretrans_" .. os.date("%s")
tmpfile = io.open(tmpname, "w")
tmpfile:write(script)
tmpfile:close()
ok, how, val = os.execute("/bin/bash " .. tmpname)
os.remove(tmpname)
if not (ok == 0) then
   error("Detected running glusterfs processes", ok)
end
%endif


%changelog
* Thu May 26 2016 Scientific Linux Auto Patch Process <SCIENTIFIC-LINUX-DEVEL@LISTSERV.FNAL.GOV>
- Added Source: enable-server-packages.patch
-->  Enable building the glusterfs-server package
- Added Source: glusterfs.S56copy.patch
-->  Copied S56glusterd-geo-rep-create-post.sh to /var/lib/glusterd/hooks/1/gsync-create/post/
- Added Source: glusterfs.ini
-->  Config file for automated patch script

* Sun Feb 07 2016 Milind Changire <mchangir@redhat.com> - 3.7.5-19
- fixes bugs bz#1303894 bz#1302901 bz#1305172 bz#1304684

* Thu Jan 28 2016 Milind Changire <mchangir@redhat.com> - 3.7.5-18
- fixes bugs bz#1299724 bz#1300246 bz#1300682

* Thu Jan 21 2016 Milind Changire <mchangir@redhat.com> - 3.7.5-17
- fixes bugs bz#1299799 bz#1285226 bz#1283961 bz#1219794 bz#1294774

* Thu Jan 14 2016 Milind Changire <mchangir@redhat.com> - 3.7.5-16
- fixes bugs bz#1297300 bz#1296134 bz#1296048 bz#1297004

* Fri Jan 08 2016 Milind Changire <mchangir@redhat.com> - 3.7.5-15
- fixes bugs bz#1285226 bz#1285167 bz#1291969 bz#1277944 bz#1288509 
  bz#1293380 bz#1278798 bz#1294816 bz#1285797 bz#1288490 bz#1272409 bz#1219794

* Tue Jan 05 2016 Milind Changire <mchangir@redhat.com> - 3.7.5-14
- fixes bugs bz#1294487 bz#1293903 bz#1294594 bz#1291386 bz#1294073 
  bz#1281946 bz#1282729 bz#1285797 bz#1272409 bz#1294478

* Wed Dec 23 2015 Milind Changire <mchangir@redhat.com> - 3.7.5-13
- fixes bugs bz#1293240 bz#1275751 bz#1276273 bz#1285783 bz#1286218 
  bz#1289228 bz#1282729 bz#1291152 bz#1219794 bz#1293228 bz#1293237 bz#1292762 
  bz#1274334 bz#1291195 bz#1292751 bz#1285797 bz#1291560 bz#1291566 bz#1293286 
  bz#1286028

* Thu Dec 17 2015 Milind Changire <mchangir@redhat.com> - 3.7.5-12
- fixes bugs bz#1285226 bz#1283940 bz#1291052 bz#1275751 bz#1288003 
  bz#1283035 bz#1285238 bz#1290401 bz#1262680 bz#1289893 bz#1289423 bz#1276227

* Thu Dec 10 2015 Milind Changire <mchangir@redhat.com> - 3.7.5-11
- fixes bugs bz#1287532 bz#1288988 bz#1275751 bz#1289071 bz#1284834 
  bz#1287980 bz#1284387 bz#1287997

* Tue Dec 08 2015 Milind Changire <mchangir@redhat.com> - 3.7.5-10
- fixes bugs bz#1283608 bz#1278798 bz#1288921 bz#1285998 bz#1278389 bz#1275633

* Thu Dec 03 2015 Milind Changire <mchangir@redhat.com> - 3.7.5-9
- bz#1275971 bz#1285295 bz#1286346 bz#1257343 bz#1286605 bz#1275912 bz#1286604 bz#1264800 bz#1272008 bz#1283563 bz#1250241 bz#1278254 bz#1286927 bz#1247515 bz#1286654 bz#1286637

* Tue Dec 01 2015 Milind Changire <mchangir@redhat.com> - 3.7.5-8
- bz#1285783 bz#1285166 bz#1286058 bz#1236020 bz#1276245 bz#1281304 bz#1285958

* Tue Nov 24 2015 Milind Changire <mchangir@redhat.com> - 3.7.5-7
- fixes bugs bz#1280410 bz#1276248 bz#1269885 bz#1224226 bz#1277088 
  bz#1277028 bz#1279350 bz#1278408 bz#1277562 bz#1283410 bz#1277126 bz#1278279 
  bz#1246007 bz#1275521 bz#1282701 bz#1224928 bz#1283050 bz#1275525 bz#1275998 
  bz#990558 bz#1278754 bz#1224064 bz#1228079 bz#1283566 bz#1271732 bz#1224880 
  bz#1278390 bz#1272929

* Tue Nov 10 2015 Milind Changire <mchangir@redhat.com> - 3.7.5-6
- fixes bugs bz#1276248 bz#1278399 bz#1265074 bz#1276246 bz#1278723 
  bz#1277359 bz#1276587 bz#1276234 bz#1272452 bz#1276542 bz#1277126 bz#1257209 
  bz#1276541 bz#1265200 bz#1276678 bz#1277043 bz#1275925 bz#1249975 bz#1261248 
  bz#1271999 bz#1264804 bz#1277316 bz#1269557 bz#1278389 bz#1275919 bz#1241436

* Thu Oct 29 2015 Bala.FA <barumuga@redhat.com> - 3.7.5-5
- fixes bugs bz#1237059 bz#1273706

* Thu Oct 29 2015 Bala.FA <barumuga@redhat.com> - 3.7.5-4
- fixes bugs bz#1200815 bz#1273703 bz#1227029 bz#1232641 bz#1262627 
  bz#1274411 bz#1236052 bz#1267185 bz#1233486 bz#1269753 bz#1211839 bz#1275158 
  bz#1272407 bz#1272341 bz#1273711 bz#1272409 bz#1248895 bz#1267194 bz#1273249 
  bz#1273260 bz#1275906 bz#1230114 bz#1274595 bz#1275155 bz#1271999 bz#1266878 
  bz#1274334 bz#1275515 bz#1265571 bz#1243797 bz#1272403 bz#1275907

* Thu Oct 15 2015 Bala.FA <barumuga@redhat.com> - 3.7.5-3
- fixes bugs bz#1236153 bz#1236503 bz#1237022 bz#1269203 bz#1271752

* Thu Oct 15 2015 Bala.FA <barumuga@redhat.com> - 3.7.5-2
- fixes bugs bz#1228643 bz#1271178 bz#1271184 bz#1271648 bz#1271659 bz#1271705
  bz#1271724 bz#1271725 bz#1271727 bz#1271729 bz#1271732 bz#1271733 bz#1271750
  bz#1271752 bz#1271757

* Wed Oct 14 2015 Bala.FA <barumuga@redhat.com> - 3.7.5-1
- rebase to upstream v3.7.5
