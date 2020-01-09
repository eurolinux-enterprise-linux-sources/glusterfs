%global _hardened_build 1

%global _for_fedora_koji_builds 0

# uncomment and add '%' to use the prereltag for pre-releases
# %%global prereltag qa3

##-----------------------------------------------------------------------------
## All argument definitions should be placed here and keep them sorted
##

# if you wish to compile an rpm with cmocka unit testing...
# rpmbuild -ta glusterfs-3.7.9.tar.gz --with cmocka
%{?_with_cmocka:%global _with_cmocka --enable-cmocka}

# if you wish to compile an rpm without rdma support, compile like this...
# rpmbuild -ta glusterfs-3.7.9.tar.gz --without rdma
%{?_without_rdma:%global _without_rdma --disable-ibverbs}

# No RDMA Support on s390(x)
%ifarch s390 s390x
%global _without_rdma --disable-ibverbs
%endif

# if you wish to compile an rpm without epoll...
# rpmbuild -ta glusterfs-3.7.9.tar.gz --without epoll
%{?_without_epoll:%global _without_epoll --disable-epoll}

# if you wish to compile an rpm without fusermount...
# rpmbuild -ta glusterfs-3.7.9.tar.gz --without fusermount
%{?_without_fusermount:%global _without_fusermount --disable-fusermount}

# if you wish to compile an rpm without geo-replication support, compile like this...
# rpmbuild -ta glusterfs-3.7.9.tar.gz --without georeplication
%{?_without_georeplication:%global _without_georeplication --disable-georeplication}

# Disable geo-replication on EL5, as its default Python is too old
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
%global _without_georeplication --disable-georeplication
%endif

# if you wish to compile an rpm without the OCF resource agents...
# rpmbuild -ta glusterfs-3.7.9.tar.gz --without ocf
%{?_without_ocf:%global _without_ocf --without-ocf}

# if you wish to build rpms without syslog logging, compile like this
# rpmbuild -ta glusterfs-3.7.9.tar.gz --without syslog
%{?_without_syslog:%global _without_syslog --disable-syslog}

# disable syslog forcefully as rhel <= 6 doesn't have rsyslog or rsyslog-mmcount
# Fedora deprecated syslog, see
#  https://fedoraproject.org/wiki/Changes/NoDefaultSyslog
# (And what about RHEL7?)
%if ( 0%{?fedora} && 0%{?fedora} >= 20 ) || ( 0%{?rhel} && 0%{?rhel} <= 6 )
%global _without_syslog --disable-syslog
%endif

# if you wish to compile an rpm without the BD map support...
# rpmbuild -ta glusterfs-3.7.9.tar.gz --without bd
%{?_without_bd:%global _without_bd --disable-bd-xlator}

%if ( 0%{?rhel} && 0%{?rhel} < 6 || 0%{?sles_version} )
%define _without_bd --disable-bd-xlator
%endif

# if you wish to compile an rpm without the qemu-block support...
# rpmbuild -ta glusterfs-3.7.9.tar.gz --without qemu-block
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
# rpmbuild -ta glusterfs-3.7.9.tar.gz --without server

%global _build_server 1
%if "%{?_without_server}"
%global _build_server 0
%endif

%global _without_extra_xlators 1
%global _without_regression_tests 1

%global _build_server 1
##-----------------------------------------------------------------------------
## All %%global definitions should be placed here and keep them sorted
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
## All package definitions should be placed here in alphabetical order
##
Summary:          Distributed File System
%if ( 0%{_for_fedora_koji_builds} )
Name:             glusterfs
Version:          3.5.0
Release:          0.1%{?prereltag:.%{prereltag}}%{?dist}
Vendor:           Fedora Project
%else
Name:             glusterfs
Version:          3.7.9
Release:          12%{?dist}
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
Source0:          glusterfs-3.7.9.tar.gz
Source9:	enable-server-packages.patch
Source10:	glusterfs.ini
%endif

BuildRoot:        %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

%if ( 0%{?rhel} && 0%{?rhel} <= 5 )
BuildRequires:    python-simplejson
%endif
%if ( 0%{?_with_systemd:1} )
BuildRequires:    systemd-units
%endif

Requires:         %{name}-libs%{?_isa} = %{version}-%{release}
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

# Patch0001: 0001-build-Updating-rfc.sh-to-point-to-rhgs-3.1.3-branch.patch
Patch0002: 0002-glusterd-fix-op-versions-for-RHS-backwards-compatabi.patch
Patch0003: 0003-glusterd-disabling-enable-shared-storage-option-shou.patch
Patch0004: 0004-tier-ctr-sql-Dafault-values-for-sql-cache-and-wal-si.patch
Patch0005: 0005-glusterd-probing-a-new-node-which-is-part-of-another.patch
Patch0006: 0006-libglusterfs-pass-buffer-size-to-gf_store_read_and_t.patch
Patch0007: 0007-extra-enable-shared-storage-key-should-create-shared.patch
Patch0008: 0008-posix-fix-posix_fgetxattr-to-return-the-correct-erro.patch
Patch0009: 0009-libgfapi-glfd-close-is-not-correctly-handled-for-asy.patch
Patch0010: 0010-rpc-set-bind-insecure-to-off-by-default.patch
Patch0011: 0011-glusterd-spec-fixing-autogen-issue.patch
Patch0012: 0012-event-epoll-Use-pollers-to-check-if-event_pool_dispa.patch
Patch0013: 0013-cluster-dht-rebalance-rebalance-failure-handling.patch
Patch0014: 0014-libglusterfs-glusterd-Fix-compilation-errors.patch
Patch0015: 0015-build-remove-ghost-directory-entries.patch
Patch0016: 0016-build-add-RHGS-specific-changes.patch
Patch0017: 0017-secalert-remove-setuid-bit-for-fusermount-glusterfs.patch
Patch0018: 0018-build-packaging-corrections-for-RHEL-5.patch
Patch0019: 0019-build-introduce-security-hardening-flags-in-gluster.patch
Patch0020: 0020-spec-fix-add-pre-transaction-scripts-for-geo-rep-and.patch
Patch0021: 0021-rpm-glusterfs-devel-for-client-builds-should-not-dep.patch
Patch0022: 0022-build-add-pretrans-check.patch
Patch0023: 0023-build-exclude-libgfdb.pc-conditionally.patch
Patch0024: 0024-build-exclude-glusterfs.xml-on-rhel-7-client-build.patch
Patch0025: 0025-glusterd-fix-info-file-checksum-mismatch-during-upgr.patch
Patch0026: 0026-build-spec-file-conflict-resolution.patch
Patch0027: 0027-uss-gluster-generate-gfid-for-snapshot-files-from-sn.patch
Patch0028: 0028-snapshot-Use-svc-manager-during-glusterd-restart.patch
Patch0029: 0029-snapshot-cli-Keep-the-dict-keys-uniform.patch
Patch0030: 0030-glusterd-Fix-connected-clients-check-during-volume-s.patch
Patch0031: 0031-glusterd-upon-re-peer-probe-glusterd-should-not-retu.patch
Patch0032: 0032-dht-update-attr-information-in-refresh-layout-to-avo.patch
Patch0033: 0033-dht-report-constant-directory-size.patch
Patch0034: 0034-posix-Filter-gsyncd-stime-xattr.patch
Patch0035: 0035-build-fixing-dependency-issue-for-glusterfs-ganesha-.patch
Patch0036: 0036-libglusterfs-open-cmd_history-log-file-with-O_APPEND.patch
Patch0037: 0037-glusterd-Add-a-new-event-to-handle-multi-net-probes.patch
Patch0038: 0038-cluster-ec-Provide-an-option-to-enable-disable-eager.patch
Patch0039: 0039-glfs-heal-Use-encrypted-connection-in-shd.patch
Patch0040: 0040-afr-Add-throttled-background-client-side-heals.patch
Patch0041: 0041-tests-shard-fallocate-tests-refactor.patch
Patch0042: 0042-features-shard-Implement-discard-fop.patch
Patch0043: 0043-debug-trace-Print-acm-times-as-integers.patch
Patch0044: 0044-glusterd-afr-Enable-auto-heal-when-replica-count-inc.patch
Patch0045: 0045-afr-Enable-auto-heal-when-replica-count-increases.patch
Patch0046: 0046-tier-dht-Attach-tier-fix-layout-to-run-in-background.patch
Patch0047: 0047-glusterd-build-realpath-post-recreate-of-brick-mount.patch
Patch0048: 0048-glusterd-fill-real_path-variable-in-brickinfo-during.patch
Patch0049: 0049-dht-lock-on-subvols-to-prevent-lookup-vs-rmdir-race.patch
Patch0050: 0050-Tier-displaying-status-only-one-the-nodes-running-ti.patch
Patch0051: 0051-storage-posix-send-proper-iatt-attributes-for-the-ro.patch
Patch0052: 0052-marker-set-inode-ctx-before-lookup-unwind.patch
Patch0053: 0053-server-send-lookup-on-root-inode-when-itable-is-crea.patch
Patch0054: 0054-marker-build_ancestry-in-marker.patch
Patch0055: 0055-posix_acl-skip-acl_permits-for-special-clients.patch
Patch0056: 0056-marker-do-mq_reduce_parent_size_txn-in-FG-for-unlink.patch
Patch0057: 0057-marker-optimize-mq_update_dirty_inode_task.patch
Patch0058: 0058-afr-add-mtime-based-split-brain-resolution-to-CLI.patch
Patch0059: 0059-md-cache-Cache-gluster-swift-metadata.patch
Patch0060: 0060-dht-lock-on-subvols-to-prevent-rename-and-lookup-sel.patch
Patch0061: 0061-glusterd-DEBUG-log-should-not-come-after-resetting-c.patch
Patch0062: 0062-gfapi-Fix-the-crashes-caused-by-global_xlator-and-TH.patch
Patch0063: 0063-features-changelog-Don-t-modify-pargfid-in-resolve_p.patch
Patch0064: 0064-tools-glusterfind-Handling-Unicode-file-names.patch
Patch0065: 0065-cluster-afr-Don-t-delete-gfid-req-from-lookup-reques.patch
Patch0066: 0066-cluster-ec-Do-not-ref-dictionary-in-lookup.patch
Patch0067: 0067-packaging-gluster-ganesha-requires-pacemaker-etc.-on.patch
Patch0068: 0068-ganesha-Include-a-script-to-generate-epoch-value.patch
Patch0069: 0069-cluster-afr-Choose-local-child-as-source-if-possible.patch
Patch0070: 0070-features-index-Get-gfid-type-in-readdir.patch
Patch0071: 0071-cluster-afr-Fix-witness-counting-code-in-src-sink-de.patch
Patch0072: 0072-syncop-Add-parallel-dir-scan-functionality.patch
Patch0073: 0073-cluster-afr-Fix-partial-heals-in-3-way-replication.patch
Patch0074: 0074-cluster-afr-Don-t-lookup-forget-inodes.patch
Patch0075: 0075-cluster-afr-Use-parallel-dir-scan-functionality.patch
Patch0076: 0076-features-shard-Make-o-direct-writes-work-with-shardi.patch
Patch0077: 0077-Revert-features-shard-Make-o-direct-writes-work-with.patch
Patch0078: 0078-op-version-Bump-up-op-version-to-3.7.12.patch
Patch0079: 0079-features-shard-Make-o-direct-writes-work-with-shardi.patch
Patch0080: 0080-glusterd-populate-brickinfo-real_path-conditionally.patch
Patch0081: 0081-NFS-new-option-nfs.rdirplus-added.patch
Patch0082: 0082-posix_acl-create-inode-ctx-for-posix_acl_get.patch
Patch0083: 0083-mount-fuse-report-ESTALE-as-ENOENT.patch
Patch0084: 0084-cluster-afr-Fix-spurious-entries-in-heal-info.patch
Patch0085: 0085-dht-add-nuke-functionality-for-efficient-server-side.patch
Patch0086: 0086-cluster-distribute-detect-stale-layouts-in-entry-fop.patch
Patch0087: 0087-geo-rep-Fix-hostname-mismatch-between-volinfo-and-ge.patch
Patch0088: 0088-extras-Add-namespace-for-options-in-group-virt.examp.patch
Patch0089: 0089-quota-setting-read-only-option-in-xdata-to-instruct-.patch
Patch0090: 0090-glusterd-fix-validation-of-lower-op-version-check-in.patch
Patch0091: 0091-clone-snapshot-Save-restored_from_snap-for-clones.patch
Patch0092: 0092-snapshot-quota-Copy-quota.cksum-during-snapshot-oper.patch
Patch0093: 0093-cluster-afr-Fix-inode-leak-in-data-self-heal.patch
Patch0094: 0094-afr-replica-pair-going-offline-does-not-require-CHIL.patch
Patch0095: 0095-afr-propagate-child-up-event-after-timeout.patch
Patch0096: 0096-dht-rebalance-Handle-GF_DEFRAG_STOP.patch
Patch0097: 0097-common-ha-continuous-grace_mon-log-messages-in-var-l.patch
Patch0098: 0098-gfapi-set-need_lookup-flag-on-response-list.patch
Patch0099: 0099-gfapi-fill-iatt-in-readdirp_cbk-if-entry-inode-is-nu.patch
Patch0100: 0100-geo-rep-Fix-checkpoint-issue-in-scheduler.patch
Patch0101: 0101-tier-dht-check-for-rebalance-completion-for-EIO-erro.patch
Patch0102: 0102-inode-Always-fetch-first-entry-from-the-inode-lists-.patch
Patch0103: 0103-Tier-tier-command-fails-message-when-any-node-is-dow.patch
Patch0104: 0104-geo-rep-Fix-gluster-binary-invocation-while-running-.patch
Patch0105: 0105-glusterd-persist-brickinfo-real_path.patch
Patch0106: 0106-tier-migrator-Fetch-the-next-query-file-for-the-next.patch
Patch0107: 0107-protocol-server-Do-not-log-ENOENT-ESTALE-in-fd-based.patch
Patch0108: 0108-libglusterfs-Add-debug-and-trace-logs-for-stack-trac.patch
Patch0109: 0109-cluster-dht-Handle-rmdir-failure-correctly.patch
Patch0110: 0110-features-bitrot-Introduce-scrubber-monitor-thread.patch
Patch0111: 0111-glusterd-bitrot-Fix-bit-rot-scrub-status.patch
Patch0112: 0112-packaging-postun-libs-ldconfig-relative-path-1-used-.patch
Patch0113: 0113-cli-bitrot-Unmask-scrub-statistics.patch
Patch0114: 0114-glusterd-fix-max-pmap-alloc-to-GF_PORT_MAX.patch
Patch0115: 0115-glusterd-try-to-connect-on-GF_PMAP_PORT_FOREIGN-aswe.patch
Patch0116: 0116-cluster-afr-Fix-read-child-selection-in-entry-create.patch
Patch0117: 0117-cluster-afr-Don-t-let-NFS-cache-stat-after-writes.patch
Patch0118: 0118-performance-write-behind-guaranteed-retry-after-a-sh.patch
Patch0119: 0119-runner-extract-and-return-actual-exit-status-of-chil.patch
Patch0120: 0120-rpc-fix-gf_process_reserved_ports.patch
Patch0121: 0121-heal-Fix-incorrect-heal-info-output.patch
Patch0122: 0122-socket-Reap-own-threads.patch
Patch0123: 0123-rpc-assign-port-only-if-it-is-unreserved.patch
Patch0124: 0124-glusterd-add-defence-mechanism-to-avoid-brick-port-c.patch
Patch0125: 0125-rpc-define-client-port-range.patch
Patch0126: 0126-dht-afr-client-posix-Fail-mkdir-without-gfid-req.patch
Patch0127: 0127-gfapi-upcall-Ignore-handle-create-failures.patch
Patch0128: 0128-glusterd-remove-brick-commit-should-not-succeed-when.patch
Patch0129: 0129-packaging-additional-dirs-and-files-in-var-lib-glust.patch
Patch0130: 0130-cluster-afr-Do-heals-with-shd-pid.patch
Patch0131: 0131-Tier-glusterd-Resetting-the-tier-status-value-to-not.patch
Patch0132: 0132-NFS-Ganesha-Parse-the-Export_Id-correctly-for-unexpo.patch
Patch0133: 0133-glusterd-ganesha-copy-ganesha-export-configuration-f.patch
Patch0134: 0134-tier-detach-During-detach-check-if-background-fixlay.patch
Patch0135: 0135-dht-remember-locked-subvol-and-send-unlock-to-the-sa.patch
Patch0136: 0136-gfapi-Fix-a-deadlock-caused-by-graph-switch-while-ai.patch
Patch0137: 0137-heal-Have-fixed-number-of-fields-in-heal-info-output.patch
Patch0138: 0138-heal-xml-xml-implementation-of-heal-info-and-splitbr.patch
Patch0139: 0139-packaging-additional-dirs-and-files-in-var-lib-glust.patch
Patch0140: 0140-build-dependency-error-during-upgrade.patch
Patch0141: 0141-packaging-additional-dirs-and-files-in-var-lib-glust.patch
Patch0142: 0142-readdir-ahead-Prefetch-xattrs-needed-by-md-cache.patch
Patch0143: 0143-packaging-additional-dirs-and-files-in-var-lib-glust.patch
Patch0144: 0144-packaging-postun-libs-ldconfig-relative-path-1-used-.patch
Patch0145: 0145-glusterd-geo-rep-slave-volume-uuid-to-identify-a-geo.patch
Patch0146: 0146-Revert-features-shard-Make-o-direct-writes-work-with.patch
Patch0147: 0147-gfapi-clear-loc.gfid-when-retrying-after-ESTALE.patch
Patch0148: 0148-cluster-afr-Handle-non-zero-source-in-heal-info-deci.patch
Patch0149: 0149-cluster-tier-return-1-to-cli-on-detach-commit-when-d.patch
Patch0150: 0150-cluster-afr-Do-post-op-in-case-of-symmetric-errors.patch
Patch0151: 0151-cluster-dht-Perform-NULL-check-on-xdata-before-dict_.patch
Patch0152: 0152-socket-Fix-incorrect-handling-of-partial-reads.patch
Patch0153: 0153-common-ha-floating-IP-VIP-doesn-t-fail-over-when-gan.patch
Patch0154: 0154-features-marker-Fix-dict_get-errors-when-key-is-NULL.patch
Patch0155: 0155-ganesha-scripts-Fixing-refresh-config-in-ganesha-ha..patch
Patch0156: 0156-tier-detach-Clear-tier-fix-layout-complete-xattr-aft.patch
Patch0157: 0157-cluster-distribute-use-a-linked-inode-in-directory-h.patch
Patch0158: 0158-cluster-distribute-heal-layout-in-discover-codepath-.patch
Patch0159: 0159-dht-rename-takes-lock-on-parent-directory-if-destina.patch
Patch0160: 0160-cluster-afr-If-possible-give-errno-received-from-low.patch
Patch0161: 0161-cluster-afr-Refresh-inode-for-inode-write-fops-in-ne.patch
Patch0162: 0162-cluster-afr-Do-not-inode_link-in-afr.patch
Patch0163: 0163-glusterd-copy-real_path-from-older-brickinfo-during-.patch
Patch0164: 0164-features-shard-Get-hard-link-count-in-unlink-rename-.patch
Patch0165: 0165-tier-cli-printing-a-warning-instead-of-skipping-the-.patch
Patch0166: 0166-glusterfsd-fix-to-return-actual-exit-status-on-mount.patch
Patch0167: 0167-extras-stop-all-include-glusterfs-process-as-well.patch
Patch0168: 0168-common-ha-stonith-enabled-option-set-error-in-new-pa.patch
Patch0169: 0169-gfapi-upcall-Use-GF_CALLOC-while-allocating-variable.patch
Patch0170: 0170-common-ha-log-flooded-with-Could-not-map-name-xxxx-t.patch
Patch0171: 0171-common-ha-post-fail-back-ganesha.nfsds-are-not-put-i.patch
Patch0172: 0172-glusterd-Fix-signature-of-glusterd_volinfo_copy_bric.patch
Patch0173: 0173-cluster-ec-Fix-issues-with-eager-locking.patch
Patch0174: 0174-dht-selfheal-should-wind-mkdir-call-to-subvols-with-.patch
Patch0175: 0175-cluster-afr-Unwind-xdata_rsp-even-in-case-of-failure.patch
Patch0176: 0176-Revert-gfapi-upcall-Use-GF_CALLOC-while-allocating-v.patch
Patch0177: 0177-geo-rep-Handle-Worker-kill-gracefully-if-worker-alre.patch
Patch0178: 0178-geo-rep-update-peers-section-in-gsyncd-conf.patch
Patch0179: 0179-glusterd-snapshot-Fix-snapshot-creation-with-geo-rep.patch
Patch0180: 0180-geo-rep-Fix-volume-stop-with-geo-rep-session.patch
Patch0181: 0181-glusterd-geo-rep-upgrade-path-when-slave-vol-uuid-in.patch
Patch0182: 0182-glusterd-snapshot-remove-quota-related-options-from-.patch
Patch0183: 0183-common-ha-race-timing-issue-setting-up-cluster.patch
Patch0184: 0184-cluster-ec-Restrict-the-launch-of-replace-brick-heal.patch
Patch0185: 0185-storage-posix-Print-offset-size-and-gfid-too-when-re.patch
Patch0186: 0186-protocol-client-Filter-o-direct-in-readv-writev.patch
Patch0187: 0187-libglusterfs-Even-anonymous-fds-must-have-fd-flags-s.patch
Patch0188: 0188-posix-shard-Use-page-aligned-buffer-for-o-direct-rea.patch
Patch0189: 0189-features-shard-Don-t-modify-readv-size.patch
Patch0190: 0190-core-shard-Make-shards-inherit-main-file-s-O_DIRECT-.patch
Patch0191: 0191-nfs-store-sattr-properly-in-nfs3_setattr-call.patch
Patch0192: 0192-glusterd-geo-rep-Avoid-started-status-check-if-same-.patch
Patch0193: 0193-libglusterfs-Negate-all-but-O_DIRECT-flag-if-present.patch
Patch0194: 0194-glusterd-fail-volume-delete-if-one-of-the-node-is-do.patch
Patch0195: 0195-cluster-ec-Pass-xdata-to-dht-in-case-of-error.patch
Patch0196: 0196-glusterd-Fix-gsyncd-upgrade-issue.patch
Patch0197: 0197-gfapi-update-count-when-glfs_buf_copy-is-used.patch
Patch0198: 0198-gfapi-check-the-value-iovec-in-glfs_io_async_cbk-onl.patch

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
Requires:         %{name}%{?_isa} = %{version}-%{release}
Requires:         %{name}-client-xlators%{?_isa} = %{version}-%{release}

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
Requires:         %{name}%{?_isa} = %{version}-%{release}
Requires:         %{name}-devel%{?_isa} = %{version}-%{release}
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
Requires:         %{name}-libs%{?_isa} = %{version}-%{release}

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
Requires:         %{name}%{?_isa} = %{version}-%{release}
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

Requires:         %{name}%{?_isa} = %{version}-%{release}
Requires:         %{name}-client-xlators%{?_isa} = %{version}-%{release}

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

Requires:         %{name}-server%{?_isa} = %{version}-%{release}
Requires:         nfs-ganesha-gluster, pcs, dbus
%if ( 0%{?rhel} && 0%{?rhel} == 6 )
Requires:         cman, pacemaker, corosync
%endif

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
Requires:         %{name}%{?_isa} = %{version}-%{release}
Requires:         %{name}-server%{?_isa} = %{version}-%{release}
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
Requires:         %{name}%{?_isa} = %{version}-%{release}

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
Requires:         %{name}%{?_isa} = %{version}-%{release}
Requires:         %{name}-fuse%{?_isa} = %{version}-%{release}
Requires:         %{name}-server%{?_isa} = %{version}-%{release}
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
Requires:         %{name}-server%{?_isa} = %{version}-%{release}
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
Requires:         %{name}%{?_isa} = %{version}-%{release}
Requires:         %{name}-cli%{?_isa} = %{version}-%{release}
Requires:         %{name}-libs%{?_isa} = %{version}-%{release}
# some daemons (like quota) use a fuse-mount, glusterfsd is part of -fuse
Requires:         %{name}-fuse%{?_isa} = %{version}-%{release}
# self-heal daemon, rebalance, nfs-server etc. are actually clients
Requires:         %{name}-api%{?_isa} = %{version}-%{release}
Requires:         %{name}-client-xlators%{?_isa} = %{version}-%{release}
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

%build
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
CFLAGS=-DUSE_INSECURE_OPENSSL
export CFLAGS
%endif
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
CFLAGS="$CFLAGS $RPM_OPT_FLAGS"
LDFLAGS="$RPM_LD_FLAGS -Wl,-z,relro,-z,now"
%endif
export CFLAGS
export LDFLAGS
%endif

# fix for patch 0104
if [ -f extras/geo-rep/schedule_georep.py ]; then
    mv extras/geo-rep/schedule_georep.py extras/geo-rep/schedule_georep.py.in
fi

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

touch %{buildroot}%{_sharedstatedir}/glusterd/glusterd.info
touch %{buildroot}%{_sharedstatedir}/glusterd/options
subdirs=(add-brick create copy-file delete gsync-create remove-brick reset set start stop)
for dir in ${subdirs[@]}
do
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/"$dir"/{pre,post}
done
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/glustershd
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/peers
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/vols
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/nfs/run
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/bitd
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/quotad
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/scrub
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/snaps
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/ss_brick
touch %{buildroot}%{_sharedstatedir}/glusterd/nfs/nfs-server.vol
touch %{buildroot}%{_sharedstatedir}/glusterd/nfs/run/nfs.pid

find ./tests ./run-tests.sh -type f | cpio -pd %{buildroot}%{_prefix}/share/glusterfs

## Install bash completion for cli
install -p -m 0744 -D extras/command-completion/gluster.bash \
    %{buildroot}%{_sysconfdir}/bash_completion.d/gluster

%clean
rm -rf %{buildroot}

##-----------------------------------------------------------------------------
## All %%post should be placed here and keep them sorted
##
%post
/sbin/ldconfig
%if ( 0%{!?_without_syslog:1} )
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
%_init_restart rsyslog
%endif
%endif
exit 0

%post api
/sbin/ldconfig

%if ( 0%{?rhel} == 5 )
%post fuse
modprobe fuse
exit 0
%endif

%if ( 0%{?_build_server} )
%if ( 0%{!?_without_georeplication:1} )
%post geo-replication
if [ $1 -ge 1 ]; then
    %_init_restart glusterd
fi
exit 0
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
  firewall-cmd  --reload 1>/dev/null 2>&1
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
## All %%preun should be placed here and keep them sorted
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
## All %%postun should be placed here and keep them sorted as best we can
## making sure to "close" each one to avoid
##   ldconfig: relative path `1' used to build cache
## errors
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
/sbin/ldconfig
%if (0%{?_with_firewalld:1})
#reload service files if firewalld running
if $(systemctl is-active firewalld 1>/dev/null 2>&1); then
    firewall-cmd  --reload
fi
exit 0
%endif
exit 0
%endif

%postun libs
/sbin/ldconfig

##-----------------------------------------------------------------------------
## All %%files should be placed here and keep them grouped
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
%dir %{_localstatedir}/run/gluster
%if 0%{?_tmpfilesdir:1}
%{_tmpfilesdir}/gluster.conf
%endif

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
%{_libdir}/*.so
# Glupy Translator examples
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy/debug-trace.*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy/helloworld.*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy/negative.*
%if ( 0%{?_build_server} )
%{_libdir}/pkgconfig/libgfchangelog.pc
%else
%exclude %{_libdir}/pkgconfig/libgfchangelog.pc
%exclude %{_libdir}/libgfchangelog.so
%endif
%if ( 0%{!?_without_tiering:1} && ! 0%{?_build_server})
%exclude %{_libdir}/libgfdb.so
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
%{_libexecdir}/ganesha/*
%{_prefix}/lib/ocf/resource.d/heartbeat/*
%{_sharedstatedir}/glusterd/hooks/1/start/post/S31ganesha-start.sh
%{_sharedstatedir}/glusterd/hooks/1/reset/post/S31ganesha-reset.sh
%endif

%if ( 0%{?_build_server} )
%if ( 0%{!?_without_georeplication:1} )
%files geo-replication
%config(noreplace) %{_sysconfdir}/logrotate.d/glusterfs-georep

%{_sbindir}/gfind_missing_files
%{_libexecdir}/glusterfs/gsyncd
%{_libexecdir}/glusterfs/python/syncdaemon/*
%{_libexecdir}/glusterfs/gverify.sh
%{_libexecdir}/glusterfs/set_geo_rep_pem_keys.sh
%{_libexecdir}/glusterfs/peer_gsec_create
%{_libexecdir}/glusterfs/peer_mountbroker
%{_libexecdir}/glusterfs/gfind_missing_files

       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/geo-replication
%ghost      %attr(0644,-,-) %{_sharedstatedir}/glusterd/geo-replication/gsyncd_template.conf
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/gsync-create
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/gsync-create/post
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/gsync-create/post/S56glusterd-geo-rep-create-post.sh
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/gsync-create/pre

%{_datadir}/glusterfs/scripts/get-gfid.sh
%{_datadir}/glusterfs/scripts/slave-upgrade.sh
%{_datadir}/glusterfs/scripts/gsync-upgrade.sh
%{_datadir}/glusterfs/scripts/generate-gfid-file.sh
%{_datadir}/glusterfs/scripts/gsync-sync-gfid
%{_datadir}/glusterfs/scripts/schedule_georep.py*
%endif
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
%doc extras/clear_xattrs.sh
# sysconf
%config(noreplace) %{_sysconfdir}/glusterfs
%config(noreplace) %{_sysconfdir}/sysconfig/glusterd

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

# /var/lib/glusterd, e.g. hookscripts, etc.
%ghost      %attr(0644,-,-) %config(noreplace) %{_sharedstatedir}/glusterd/glusterd.info
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/bitd
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/groups
            %attr(0644,-,-) %{_sharedstatedir}/glusterd/groups/virt
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/glusterfind
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/glusterfind/.keys
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/glustershd
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick/post
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick/post/disabled-quota-root-xattr-heal.sh
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick/pre/S28Quota-enable-root-xattr-heal.sh
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick/pre
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/create
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/create/post
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/create/pre
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/copy-file
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/copy-file/post
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/copy-file/pre
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/delete
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/delete/post
                            %{_sharedstatedir}/glusterd/hooks/1/delete/post/S57glusterfind-delete-post.py
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/delete/pre
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/remove-brick
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/remove-brick/post
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/remove-brick/pre
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/reset
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/reset/post
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/reset/pre
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/set
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/set/post
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/set/post/S30samba-set.sh
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/set/post/S32gluster_enable_shared_storage.sh
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/set/pre
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/start
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/start/post
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/start/post/S29CTDBsetup.sh
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/start/post/S30samba-start.sh
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/start/pre
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/stop
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/stop/post
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/stop/pre
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/stop/pre/S30samba-stop.sh
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/stop/pre/S29CTDB-teardown.sh
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/nfs
%ghost      %attr(0600,-,-) %{_sharedstatedir}/glusterd/nfs/nfs-server.vol
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/nfs/run
%ghost      %attr(0600,-,-) %{_sharedstatedir}/glusterd/nfs/run/nfs.pid
%ghost      %attr(0600,-,-) %{_sharedstatedir}/glusterd/options
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/peers
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/quotad
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/scrub
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/snaps
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/ss_brick
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/vols

# Extra utility script
%{_datadir}/glusterfs/scripts/stop-all-gluster-processes.sh

# Incrementalapi
%{_libexecdir}/glusterfs/glusterfind
%{_bindir}/glusterfind
%{_libexecdir}/glusterfs/peer_add_secret_pub

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
* Wed Mar 22 2017 Scientific Linux Auto Patch Process <SCIENTIFIC-LINUX-DEVEL@LISTSERV.FNAL.GOV>
- Added Source: enable-server-packages.patch
-->  Enable building the glusterfs-server package
- Added Source: glusterfs.ini
-->  Config file for automated patch script

* Wed Aug 24 2016 Milind Changire <mchangir@redhat.com> - 3.7.9-12
- fixes bugs bz#1369390

* Wed Jul 27 2016 Milind Changire <mchangir@redhat.com> - 3.7.9-11
- fixes bugs bz#1353470

* Fri Jun 10 2016 Milind Changire <mchangir@redhat.com> - 3.7.9-10
- fixes bugs bz#1343549 bz#1344278 bz#1344625

* Tue Jun 07 2016 Milind Changire <mchangir@redhat.com> - 3.7.9-9
- fixes bugs bz#1336753 bz#1339136 bz#1342426 bz#1342938

* Sat Jun 04 2016 Milind Changire <mchangir@redhat.com> - 3.7.9-8
- fixes bugs bz#1341034 bz#1341316 bz#1341567 bz#1341820 bz#1342261

* Tue May 31 2016 Milind Changire <mchangir@redhat.com> - 3.7.9-7
- fixes bugs bz#1286582 bz#1330997 bz#1334092 bz#1337384 bz#1337649 
  bz#1339090 bz#1339163 bz#1339208 bz#1340085 bz#1340383

* Mon May 23 2016 Milind Changire <mchangir@redhat.com> - 3.7.9-6
- fixes bugs bz#1118762 bz#1322695 bz#1330044 bz#1331280 bz#1333643 
  bz#1335357 bz#1336332

* Tue May 17 2016 Milind Changire <mchangir@redhat.com> - 3.7.9-5
- fixes bugs bz#1261838 bz#1324820 bz#1325760 bz#1328194 bz#1331260 
  bz#1332949 bz#1333668 bz#1334234 bz#1334668 bz#1334985 bz#1335082 bz#1335114 
  bz#1335364 bz#1335437 bz#1335505 bz#1335826

* Tue May 10 2016 Milind Changire <mchangir@redhat.com> - 3.7.9-4
- fixes bugs bz#1097555 bz#1322306 bz#1327195 bz#1324820 bz#1306194 
  bz#1298724 bz#1299737 bz#1330385 bz#1258875 bz#1283957 bz#1311362 bz#1321550 
  bz#1332199 bz#1329514 bz#1224180 bz#1313370 bz#1328194 bz#1323424 bz#1332957 
  bz#1294755 bz#1328411 bz#1327751 bz#1332077 bz#1328721 bz#1330365

* Sat Apr 30 2016 Milind Changire <mchangir@redhat.com> - 3.7.9-3
- fixes bugs bz#1325975 bz#1311839 bz#1321556 bz#1286911 bz#1323042 
  bz#1298724 bz#1327165 bz#1101702 bz#1326498 bz#1326663 bz#1328397 bz#1330881 
  bz#1331376 bz#1330901 bz#1326248 bz#1324338 bz#1115367 bz#1308837 bz#1322695 
  bz#1322247 bz#1329895 bz#1327552 bz#1118770

* Tue Apr 19 2016 Milind Changire <mchangir@redhat.com> - 3.7.9-2
- fixes bugs bz#1321509 bz#1322765 bz#1314724 bz#1242358 bz#1317790 
  bz#1314391 bz#1318428 bz#1298724 bz#1318170 bz#1283957 bz#1302355 bz#1318427 
  bz#1325750 bz#1309437 bz#1317940 bz#1302688 bz#1320412 bz#1289439 bz#1294062 
  bz#1300875 bz#1305456 bz#1115367 bz#1118770 bz#1314373 bz#1314421 bz#1294790 
  bz#1317908 bz#1323119 bz#1248998 bz#1231150 bz#1311686 bz#1321544 bz#1298955 
  bz#1292034 bz#1319406 bz#1303591 bz#1279628

* Wed Mar 23 2016 Milind Changire <mchangir@redhat.com> - 3.7.9-1
- rebase to upstream v3.7.9
- fixes bugs bz#1319658 bz#1319670 bz#1319688 bz#1319695 bz#1319603 
  bz#1273706 bz#1319625 bz#1319619 bz#1319646 bz#1283035 bz#1319710 bz#1319698 
  bz#1319634 bz#1319592 bz#1319638

