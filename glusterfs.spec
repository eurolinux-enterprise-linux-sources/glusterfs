%global _hardened_build 1

%global _for_fedora_koji_builds 0

# uncomment and add '%' to use the prereltag for pre-releases
# %%global prereltag qa3

##-----------------------------------------------------------------------------
## All argument definitions should be placed here and keep them sorted
##

# if you wish to compile an rpm with debugging...
# rpmbuild -ta glusterfs-3.12.2.tar.gz --with debug
%{?_with_debug:%global _with_debug --enable-debug}

# if you wish to compile an rpm to run all processes under valgrind...
# rpmbuild -ta glusterfs-3.12.2.tar.gz --with valgrind
%{?_with_valgrind:%global _with_valgrind --enable-valgrind}

# if you wish to compile an rpm with cmocka unit testing...
# rpmbuild -ta glusterfs-3.12.2.tar.gz --with cmocka
%{?_with_cmocka:%global _with_cmocka --enable-cmocka}

# if you wish to compile an rpm without rdma support, compile like this...
# rpmbuild -ta glusterfs-3.12.2.tar.gz --without rdma
%{?_without_rdma:%global _without_rdma --disable-ibverbs}

# No RDMA Support on s390(x)
%ifarch s390 s390x armv7hl
%global _without_rdma --disable-ibverbs
%endif

# if you wish to compile an rpm without epoll...
# rpmbuild -ta glusterfs-3.12.2.tar.gz --without epoll
%{?_without_epoll:%global _without_epoll --disable-epoll}

# if you wish to compile an rpm without fusermount...
# rpmbuild -ta glusterfs-3.12.2.tar.gz --without fusermount
%{?_without_fusermount:%global _without_fusermount --disable-fusermount}

# if you wish to compile an rpm without geo-replication support, compile like this...
# rpmbuild -ta glusterfs-3.12.2.tar.gz --without georeplication
%{?_without_georeplication:%global _without_georeplication --disable-georeplication}

# Disable geo-replication on EL5, as its default Python is too old
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
%global _without_georeplication --disable-georeplication
%endif

# if you wish to compile an rpm without the OCF resource agents...
# rpmbuild -ta glusterfs-3.12.2.tar.gz --without ocf
%{?_without_ocf:%global _without_ocf --without-ocf}

# if you wish to build rpms without syslog logging, compile like this
# rpmbuild -ta glusterfs-3.12.2.tar.gz --without syslog
%{?_without_syslog:%global _without_syslog --disable-syslog}

# disable syslog forcefully as rhel <= 6 doesn't have rsyslog or rsyslog-mmcount
# Fedora deprecated syslog, see
#  https://fedoraproject.org/wiki/Changes/NoDefaultSyslog
# (And what about RHEL7?)
%if ( 0%{?fedora} && 0%{?fedora} >= 20 ) || ( 0%{?rhel} && 0%{?rhel} <= 6 )
%global _without_syslog --disable-syslog
%endif

# if you wish to compile an rpm without the BD map support...
# rpmbuild -ta glusterfs-3.12.2.tar.gz --without bd
%{?_without_bd:%global _without_bd --disable-bd-xlator}

%if ( 0%{?rhel} && 0%{?rhel} < 6 || 0%{?sles_version} )
%global _without_bd --disable-bd-xlator
%endif

# Disable data-tiering on EL5, sqlite is too old
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
%global _without_tiering --disable-tiering
%endif

# if you wish not to build server rpms, compile like this.
# rpmbuild -ta glusterfs-3.12.2.tar.gz --without server

%global _build_server 1
%if "%{?_without_server}"
%global _build_server 0
%endif

%if ( "%{?dist}" == ".el6rhs" ) || ( "%{?dist}" == ".el7rhs" ) || ( "%{?dist}" == ".el7rhgs" )
%global _build_server 1
%else
%global _build_server 0
#%%global _without_georeplication --disable-georeplication
%endif
%global _build_server 1

%global _without_extra_xlators 1
%global _without_regression_tests 1

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
%global _with_tmpfilesdir --with-tmpfilesdir=%{_tmpfilesdir}
%else
%global _with_tmpfilesdir --without-tmpfilesdir
%endif

# Eventing
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
%global _without_events --disable-events
%endif

# From https://fedoraproject.org/wiki/Packaging:Python#Macros
%if ( 0%{?rhel} && 0%{?rhel} <= 6 )
%{!?python2_sitelib: %global python2_sitelib %(python2 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(python2 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%global _rundir %{_localstatedir}/run
%endif

%if ( 0%{?_with_systemd:1} )
%global _init_enable()  /bin/systemctl enable %1.service ;
%global _init_disable() /bin/systemctl disable %1.service ;
%global _init_restart() /bin/systemctl try-restart %1.service ;
%global _init_start()   /bin/systemctl start %1.service ;
%global _init_stop()    /bin/systemctl stop %1.service ;
%global _init_install() install -D -p -m 0644 %1 %{buildroot}%{_unitdir}/%2.service ;
# can't seem to make a generic macro that works
%global _init_glusterd   %{_unitdir}/glusterd.service
%global _init_glusterfsd %{_unitdir}/glusterfsd.service
%global _init_glustereventsd %{_unitdir}/glustereventsd.service
%global _init_glusterfssharedstorage %{_unitdir}/glusterfssharedstorage.service
%else
%global _init_enable()  /sbin/chkconfig --add %1 ;
%global _init_disable() /sbin/chkconfig --del %1 ;
%global _init_restart() /sbin/service %1 condrestart &>/dev/null ;
%global _init_start()   /sbin/service %1 start &>/dev/null ;
%global _init_stop()    /sbin/service %1 stop &>/dev/null ;
%global _init_install() install -D -p -m 0755 %1 %{buildroot}%{_sysconfdir}/init.d/%2 ;
# can't seem to make a generic macro that works
%global _init_glusterd   %{_sysconfdir}/init.d/glusterd
%global _init_glusterfsd %{_sysconfdir}/init.d/glusterfsd
%global _init_glustereventsd %{_sysconfdir}/init.d/glustereventsd
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
%global _sharedstatedir /var/lib
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
Version:          3.8.0
Release:          0.1%{?prereltag:.%{prereltag}}%{?dist}
%else
Name:             glusterfs
Version:          3.12.2
Release:          18%{?dist}
%endif
License:          GPLv2 or LGPLv3+
Group:            System Environment/Base
URL:              http://gluster.readthedocs.io/en/latest/
%if ( 0%{_for_fedora_koji_builds} )
Source0:          http://bits.gluster.org/pub/gluster/glusterfs/src/glusterfs-%{version}%{?prereltag}.tar.gz
Source1:          glusterd.sysconfig
Source2:          glusterfsd.sysconfig
Source6:          rhel5-load-fuse-modules
Source7:          glusterfsd.service
Source8:          glusterfsd.init
%else
Source0:          glusterfs-3.12.2.tar.gz
%endif

BuildRoot:        %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

Requires(pre):    shadow-utils
%if ( 0%{?rhel} && 0%{?rhel} <= 5 )
BuildRequires:    python-simplejson
%endif
%if ( 0%{?_with_systemd:1} )
BuildRequires:    systemd
%endif

Requires:         %{name}-libs%{?_isa} = %{version}-%{release}
%if ( 0%{?_with_systemd:1} )
%{?systemd_requires}
%endif
BuildRequires:    git
BuildRequires:    bison flex
BuildRequires:    gcc make libtool
BuildRequires:    ncurses-devel readline-devel
BuildRequires:    libxml2-devel openssl-devel
BuildRequires:    libaio-devel libacl-devel
BuildRequires:    python2-devel
%if ( 0%{?fedora} && 0%{?fedora} < 26 ) || ( 0%{?rhel} )
BuildRequires:    python-ctypes
%endif
BuildRequires:    userspace-rcu-devel >= 0.7
%if ( 0%{?rhel} && 0%{?rhel} <= 6 )
BuildRequires:    automake
%endif
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
%if ( 0%{!?_without_bd:1} )
BuildRequires:    lvm2-devel
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

# Patch0001: 0001-Update-rfc.sh-to-rhgs-3.4.0.patch
Patch0002: 0002-glusterd-fix-op-versions-for-RHS-backwards-compatabi.patch
Patch0003: 0003-tier-ctr-sql-Dafault-values-for-sql-cache-and-wal-si.patch
Patch0004: 0004-rpc-set-bind-insecure-to-off-by-default.patch
Patch0005: 0005-glusterd-spec-fixing-autogen-issue.patch
Patch0006: 0006-libglusterfs-glusterd-Fix-compilation-errors.patch
Patch0007: 0007-build-remove-ghost-directory-entries.patch
Patch0008: 0008-build-add-RHGS-specific-changes.patch
Patch0009: 0009-secalert-remove-setuid-bit-for-fusermount-glusterfs.patch
Patch0010: 0010-build-packaging-corrections-for-RHEL-5.patch
Patch0011: 0011-build-introduce-security-hardening-flags-in-gluster.patch
Patch0012: 0012-spec-fix-add-pre-transaction-scripts-for-geo-rep-and.patch
Patch0013: 0013-rpm-glusterfs-devel-for-client-builds-should-not-dep.patch
Patch0014: 0014-build-add-pretrans-check.patch
Patch0015: 0015-build-exclude-libgfdb.pc-conditionally.patch
Patch0016: 0016-build-exclude-glusterfs.xml-on-rhel-7-client-build.patch
Patch0017: 0017-glusterd-fix-info-file-checksum-mismatch-during-upgr.patch
Patch0018: 0018-build-spec-file-conflict-resolution.patch
Patch0019: 0019-build-dependency-error-during-upgrade.patch
Patch0020: 0020-eventsapi-Fix-eventtypes.h-header-generation-with-Py.patch
Patch0021: 0021-syscall-remove-preadv-and-pwritev-sys-wrappers.patch
Patch0022: 0022-build-ignore-sbindir-conf.py-for-RHEL-5.patch
Patch0023: 0023-build-randomize-temp-file-names-in-pretrans-scriptle.patch
Patch0024: 0024-glusterd-gNFS-On-post-upgrade-to-3.2-disable-gNFS-fo.patch
Patch0025: 0025-build-Add-dependency-on-netstat-for-glusterfs-ganesh.patch
Patch0026: 0026-glusterd-gNFS-explicitly-set-nfs.disable-to-off-afte.patch
Patch0027: 0027-glusterd-spawn-nfs-daemon-in-op-version-bump-if-nfs..patch
Patch0028: 0028-glusterd-parallel-readdir-Change-the-op-version-of-p.patch
Patch0029: 0029-build-exclude-glusterfssharedstorage.service-and-mou.patch
Patch0030: 0030-build-make-gf_attach-available-in-glusterfs-server.patch
Patch0031: 0031-glusterd-Revert-op-version-for-cluster.max-brick-per.patch
Patch0032: 0032-cli-Add-message-for-user-before-modifying-brick-mult.patch
Patch0033: 0033-build-launch-glusterd-upgrade-after-all-new-bits-are.patch
Patch0034: 0034-build-remove-pretrans-script-for-python-gluster.patch
Patch0035: 0035-glusterd-regenerate-volfiles-on-op-version-bump-up.patch
Patch0036: 0036-mount-fuse-Fix-parsing-of-vol_id-for-snapshot-volume.patch
Patch0037: 0037-protocol-auth-use-the-proper-validation-method.patch
Patch0038: 0038-protocol-server-fix-the-comparision-logic-in-case-of.patch
Patch0039: 0039-protocol-client-handle-the-subdir-handshake-properly.patch
Patch0040: 0040-glusterd-delete-source-brick-only-once-in-reset-bric.patch
Patch0041: 0041-glusterd-persist-brickinfo-s-port-change-into-gluste.patch
Patch0042: 0042-glusterd-restart-the-brick-if-qorum-status-is-NOT_AP.patch
Patch0043: 0043-glusterd-clean-up-portmap-on-brick-disconnect.patch
Patch0044: 0044-glusterd-fix-brick-restart-parallelism.patch
Patch0045: 0045-glusterd-introduce-max-port-range.patch
Patch0046: 0046-Revert-build-conditionally-build-legacy-gNFS-server-.patch
Patch0047: 0047-Revert-glusterd-skip-nfs-svc-reconfigure-if-nfs-xlat.patch
Patch0048: 0048-glusterd-introduce-timer-in-mgmt_v3_lock.patch
Patch0049: 0049-Revert-packaging-ganesha-remove-glusterfs-ganesha-su.patch
Patch0050: 0050-Revert-glusterd-storhaug-remove-ganesha.patch
Patch0051: 0051-Revert-storhaug-HA-first-step-remove-resource-agents.patch
Patch0052: 0052-common-ha-fixes-for-Debian-based-systems.patch
Patch0053: 0053-ganesha-scripts-Remove-export-entries-from-ganesha.c.patch
Patch0054: 0054-glusterd-ganesha-During-volume-delete-remove-the-gan.patch
Patch0055: 0055-glusterd-ganesha-throw-proper-error-for-gluster-nfs-.patch
Patch0056: 0056-ganesha-scripts-Stop-ganesha-process-on-all-nodes-if.patch
Patch0057: 0057-ganesha-allow-refresh-config-and-volume-export-unexp.patch
Patch0058: 0058-glusterd-ganesha-perform-removal-of-ganesha.conf-on-.patch
Patch0059: 0059-glusterd-ganesha-update-cache-invalidation-properly-.patch
Patch0060: 0060-glusterd-ganesha-return-proper-value-in-pre_setup.patch
Patch0061: 0061-ganesha-scripts-remove-dependency-over-export-config.patch
Patch0062: 0062-glusterd-ganesha-add-proper-NULL-check-in-manage_exp.patch
Patch0063: 0063-ganesha-minor-improvments-for-commit-e91cdf4-17081.patch
Patch0064: 0064-common-ha-surviving-ganesha.nfsd-not-put-in-grace-on.patch
Patch0065: 0065-common-ha-enable-and-disable-selinux-ganesha_use_fus.patch
Patch0066: 0066-packaging-glusterfs-ganesha-update-sometimes-fails-s.patch
Patch0067: 0067-packaging-own-files-in-var-run-gluster-shared_storag.patch
Patch0068: 0068-common-ha-enable-and-disable-selinux-gluster_use_exe.patch
Patch0069: 0069-ganesha-ha-don-t-set-SELinux-booleans-if-SELinux-is-.patch
Patch0070: 0070-build-remove-ganesha-dependency-on-selinux-policy.patch
Patch0071: 0071-common-ha-enable-pacemaker-at-end-of-setup.patch
Patch0072: 0072-common-ha-Fix-an-incorrect-syntax-during-setup.patch
Patch0073: 0073-Fix-build-issues-related-to-nfs-ganesha-package.patch
Patch0074: 0074-build-make-var-run-available-on-RHEL-6.patch
Patch0075: 0075-cli-gluster-help-changes.patch
Patch0076: 0076-cluster-ec-Handle-parallel-get_size_version.patch
Patch0077: 0077-cluster-ec-add-functions-for-stripe-alignment.patch
Patch0078: 0078-cluster-afr-Honor-default-timeout-of-5min-for-analyz.patch
Patch0079: 0079-cluster-ec-Allow-parallel-writes-in-EC-if-possible.patch
Patch0080: 0080-heal-New-feature-heal-info-summary-to-list-the-statu.patch
Patch0081: 0081-cluster-dht-Don-t-set-ACLs-on-linkto-file.patch
Patch0082: 0082-cluster-afr-Print-heal-info-summary-output-in-stream.patch
Patch0083: 0083-cluster-afr-Print-heal-info-split-brain-output-in-st.patch
Patch0084: 0084-cluster-afr-Fix-for-arbiter-becoming-source.patch
Patch0085: 0085-snapshot-Issue-with-other-processes-accessing-the-mo.patch
Patch0086: 0086-snapshot-lvm-cleanup-during-snapshot-remove.patch
Patch0087: 0087-glusterd-Validate-changelog-on-geo-rep-volume.patch
Patch0088: 0088-cluster-ec-Implement-DISCARD-FOP-for-EC.patch
Patch0089: 0089-geo-rep-Filter-out-volume-mark-xattr.patch
Patch0090: 0090-Quota-Adding-man-page-for-quota.patch
Patch0091: 0091-extras-scripts-to-control-CPU-MEMORY-for-any-gluster.patch
Patch0092: 0092-posix-Needs-to-reserve-disk-space-to-prevent-the-bri.patch
Patch0093: 0093-posix-Ignore-disk-space-reserve-check-for-internal-F.patch
Patch0094: 0094-cluster-afr-Fail-open-on-split-brain.patch
Patch0095: 0095-extras-hooks-Fix-errors-reported-via-shellcheck-util.patch
Patch0096: 0096-extras-hooks-Honour-all-input-arguments-to-scripts.patch
Patch0097: 0097-extras-hooks-Fix-getopt-usage.patch
Patch0098: 0098-snapshot-snapshot-creation-failed-after-brick-reset-.patch
Patch0099: 0099-Tier-Stop-tierd-for-detach-start.patch
Patch0100: 0100-cluster-ec-Improve-heal-info-command-to-handle-obvio.patch
Patch0101: 0101-cluster-ec-Prevent-self-heal-to-work-after-PARENT_DO.patch
Patch0102: 0102-libglusterfs-fix-the-call_stack_set_group-function.patch
Patch0103: 0103-features-locks-Fix-memory-leaks.patch
Patch0104: 0104-cluster-dht-fix-crash-when-deleting-directories.patch
Patch0105: 0105-glusterd-Fix-glusterd-mem-leaks.patch
Patch0106: 0106-glusterd-Free-up-svc-conn-on-volume-delete.patch
Patch0107: 0107-feature-bitrot-remove-internal-xattrs-from-lookup-cb.patch
Patch0108: 0108-mount-fuse-use-fstat-in-getattr-implementation-if-an.patch
Patch0109: 0109-mount-fuse-never-fail-open-dir-with-ENOENT.patch
Patch0110: 0110-Revert-mount-fuse-report-ESTALE-as-ENOENT.patch
Patch0111: 0111-cluster-dht-don-t-overfill-the-buffer-in-readdir-p.patch
Patch0112: 0112-write-behind-Allow-trickling-writes-to-be-configurab.patch
Patch0113: 0113-gfapi-set-lkowner-in-glfd.patch
Patch0114: 0114-eventsapi-Add-JWT-signing-support.patch
Patch0115: 0115-eventsapi-JWT-signing-without-external-dependency.patch
Patch0116: 0116-eventsapi-HTTPS-support-for-Webhooks.patch
Patch0117: 0117-geo-rep-Log-message-improvements.patch
Patch0118: 0118-snapshot-after-brick-reset-replace-snapshot-creation.patch
Patch0119: 0119-geo-rep-Fix-data-sync-issue-during-hardlink-rename.patch
Patch0120: 0120-glusterd-connect-to-an-existing-brick-process-when-q.patch
Patch0121: 0121-cluster-ec-OpenFD-heal-implementation-for-EC.patch
Patch0122: 0122-tests-Use-dev-urandom-instead-of-dev-random-for-dd.patch
Patch0123: 0123-quota-fixes-issue-in-quota.conf-when-setting-large-n.patch
Patch0124: 0124-build-remove-ExclusiveArch-from-spec-file.patch
Patch0125: 0125-cluster-afr-Fixing-the-flaws-in-arbiter-becoming-sou.patch
Patch0126: 0126-spec-unpackaged-files-found-for-RHEL-7-client-build.patch
Patch0127: 0127-spec-unpackaged-files-found-for-RHEL-7-client-build.patch
Patch0128: 0128-build-remove-pretrans-script-for-ganesha.patch
Patch0129: 0129-posix-delete-stale-gfid-handles-in-nameless-lookup.patch
Patch0130: 0130-md-cache-avoid-checking-the-xattr-value-buffer-with-.patch
Patch0131: 0131-readdir-ahead-Add-parallel-readdir-option-in-readdir.patch
Patch0132: 0132-posix-In-getxattr-honor-the-wildcard.patch
Patch0133: 0133-upcall-Allow-md-cache-to-specify-invalidations-on-xa.patch
Patch0134: 0134-cli-Fixed-a-use_after_free.patch
Patch0135: 0135-cli-commands-are-missing-in-man-page.patch
Patch0136: 0136-glusterd-Nullify-pmap-entry-for-bricks-belonging-to-.patch
Patch0137: 0137-bitrot-improved-cli-report-after-bitrot-operatoin.patch
Patch0138: 0138-glusterd-enable-brick-multiplexing-by-default.patch
Patch0139: 0139-libglusterfs-Reset-errno-before-call.patch
Patch0140: 0140-md-cache-Add-additional-samba-and-macOS-specific-EAs.patch
Patch0141: 0141-rpc-Showing-some-unusual-timer-error-logs-during-bri.patch
Patch0142: 0142-cluster-dht-Add-migration-checks-to-dht_-f-xattrop.patch
Patch0143: 0143-glusterd-store-handle-the-case-of-fsid-being-set-to-.patch
Patch0144: 0144-cluster-dht-Unlink-linkto-files-as-root.patch
Patch0145: 0145-glusterd-optimize-glusterd-import-volumes-code-path.patch
Patch0146: 0146-cluster-dht-Cleanup-on-fallocate-failure.patch
Patch0147: 0147-glusterd-import-volumes-in-separate-synctask.patch
Patch0148: 0148-glusterd-tier-is_tier_enabled-inserted-causing-check.patch
Patch0149: 0149-cluster-ec-EC-DISCARD-doesn-t-punch-hole-properly.patch
Patch0150: 0150-dht-Fill-first_up_subvol-before-use-in-dht_opendir.patch
Patch0151: 0151-geo-rep-Improve-geo-rep-pre-validation-logs.patch
Patch0152: 0152-glusterfind-Speed-up-gfid-lookup-100x-by-using-an-SQ.patch
Patch0153: 0153-afr-add-quorum-checks-in-post-op.patch
Patch0154: 0154-afr-capture-the-correct-errno-in-post-op-quorum-chec.patch
Patch0155: 0155-afr-don-t-treat-all-cases-all-bricks-being-blamed-as.patch
Patch0156: 0156-performance-write-behind-fix-bug-while-handling-shor.patch
Patch0157: 0157-cluster-afr-remove-unnecessary-child_up-initializati.patch
Patch0158: 0158-cluster-ec-create-eager-lock-option-for-non-regular-.patch
Patch0159: 0159-extras-hooks-Fix-S10selinux-label-brick.sh-hook-scri.patch
Patch0160: 0160-common-ha-enable-and-disable-selinux-ganesha_use_fus.patch
Patch0161: 0161-cluster-dht-Fixed-a-typo.patch
Patch0162: 0162-cluster-dht-Handle-single-dht-child-in-dht_lookup.patch
Patch0163: 0163-glusterd-compare-uuid-instead-of-hostname-while-find.patch
Patch0164: 0164-geo-rep-Remove-lazy-umount-and-use-mount-namespaces.patch
Patch0165: 0165-cluster-dht-Ignore-ENODATA-from-getxattr-for-posix-a.patch
Patch0166: 0166-rpcsvc-scale-rpcsvc_request_handler-threads.patch
Patch0167: 0167-glusterd-ganesha-change-voltype-for-ganesha.enable-i.patch
Patch0168: 0168-features-shard-Pass-the-correct-block-num-to-store-i.patch
Patch0169: 0169-features-shard-Leverage-block_num-info-in-inode-ctx-.patch
Patch0170: 0170-features-shard-Fix-shard-inode-refcount-when-it-s-pa.patch
Patch0171: 0171-features-shard-Upon-FSYNC-from-upper-layers-wind-fsy.patch
Patch0172: 0172-glusterd-add-profile_enabled-flag-in-get-state.patch
Patch0173: 0173-packaging-adding-missed-part-from-5eed664-while-back.patch
Patch0174: 0174-hooks-add-a-script-to-stat-the-subdirs-in-add-brick.patch
Patch0175: 0175-rpc-make-actor-search-parallel.patch
Patch0176: 0176-glusterd-volume-get-fixes-for-client-io-threads-quor.patch
Patch0177: 0177-hooks-fix-workdir-in-S13create-subdir-mounts.sh.patch
Patch0178: 0178-cluster-ec-Do-lock-conflict-check-correctly-for-wait.patch
Patch0179: 0179-packaging-adding-missed-part-from-5eed664-while-back.patch
Patch0180: 0180-packaging-adding-missed-part-from-5eed664-while-back.patch
Patch0181: 0181-glusterd-get-state-memory-leak-fix.patch
Patch0182: 0182-glusterd-Fix-coverity-issues-in-glusterd-handler.c.patch
Patch0183: 0183-cluster-afr-Fix-dict-leak-in-pre-op.patch
Patch0184: 0184-cli-glusterfsd-remove-copyright-information.patch
Patch0185: 0185-rpcsvc-correct-event-thread-scaling.patch
Patch0186: 0186-cli-Remove-upstream-doc-reference.patch
Patch0187: 0187-features-shard-Do-list_del_init-while-list-memory-is.patch
Patch0188: 0188-georep-Pause-Resume-of-geo-replication-with-wrong-us.patch
Patch0189: 0189-fuse-enable-proper-fgetattr-like-semantics.patch
Patch0190: 0190-cluster-afr-Adding-option-to-take-full-file-lock.patch
Patch0191: 0191-cluster-afr-Make-afr_fsync-a-transaction.patch
Patch0192: 0192-cluster-afr-Remove-compound-fops-usage-in-afr.patch
Patch0193: 0193-cluster-afr-Remove-unused-code-paths.patch
Patch0194: 0194-cluster-afr-Make-AFR-eager-locking-similar-to-EC.patch
Patch0195: 0195-storage-posix-Add-active-fd-count-option-in-gluster.patch
Patch0196: 0196-cluster-afr-Switch-to-active-fd-count-for-open-fd-ch.patch
Patch0197: 0197-glusterd-ganesha-create-remove-export-file-only-from.patch
Patch0198: 0198-cluster-ec-Change-default-read-policy-to-gfid-hash.patch
Patch0199: 0199-cluster-ec-avoid-delays-in-self-heal.patch
Patch0200: 0200-quick-read-Discard-cache-for-fallocate-zerofill-and-.patch
Patch0201: 0201-posix-After-set-storage.reserve-limit-df-does-not-sh.patch
Patch0202: 0202-glusterd-TLS-verification-fails-while-using-intermed.patch
Patch0203: 0203-mgmt-glusterd-Adding-validation-for-setting-quorum-c.patch
Patch0204: 0204-glusterd-memory-leak-in-mgmt_v3-lock-functionality.patch
Patch0205: 0205-cluster-dht-User-xattrs-are-not-healed-after-brick-s.patch
Patch0206: 0206-glusterd-honour-localtime-logging-for-all-the-daemon.patch
Patch0207: 0207-glusterd-fix-txn_opinfo-memory-leak.patch
Patch0208: 0208-cluster-dht-enable-lookup-optimize-by-default.patch
Patch0209: 0209-cluster-dht-Update-layout-in-inode-only-on-success.patch
Patch0210: 0210-cluster-ec-send-list-node-uuids-request-to-all-subvo.patch
Patch0211: 0211-common-ha-scripts-pass-the-list-of-servers-properly-.patch
Patch0212: 0212-readdir-ahead-Cleanup-the-xattr-request-code.patch
Patch0213: 0213-glusterd-mark-port_registered-to-true-for-all-runnin.patch
Patch0214: 0214-cluster-dht-Serialize-mds-update-code-path-with-look.patch
Patch0215: 0215-cluster-dht-ENOSPC-will-not-fail-rebalance.patch
Patch0216: 0216-cluster-dht-Wind-open-to-all-subvols.patch
Patch0217: 0217-cluster-dht-Handle-file-migrations-when-brick-down.patch
Patch0218: 0218-posix-reserve-option-behavior-is-not-correct-while-u.patch
Patch0219: 0219-Quota-heal-directory-on-newly-added-bricks-when-quot.patch
Patch0220: 0220-glusterd-turn-off-selinux-feature-in-downstream.patch
Patch0221: 0221-cluster-dht-Skipped-files-are-not-treated-as-errors.patch
Patch0222: 0222-hooks-remove-selinux-hooks.patch
Patch0223: 0223-glusterd-Make-localtime-logging-option-invisible-in-.patch
Patch0224: 0224-protocol-server-Backport-patch-to-reduce-duplicate-c.patch
Patch0225: 0225-glusterfsd-Memleak-in-glusterfsd-process-while-brick.patch
Patch0226: 0226-gluster-Sometimes-Brick-process-is-crashed-at-the-ti.patch
Patch0227: 0227-afr-add-quorum-checks-in-pre-op.patch
Patch0228: 0228-afr-fixes-to-afr-eager-locking.patch
Patch0229: 0229-fuse-do-fd_resolve-in-fuse_getattr-if-fd-is-received.patch
Patch0230: 0230-glusterd-volume-inode-fd-status-broken-with-brick-mu.patch
Patch0231: 0231-fuse-retire-statvfs-tweak.patch
Patch0232: 0232-eventsapi-Handle-Unicode-string-during-signing.patch
Patch0233: 0233-libglusterfs-fix-comparison-of-a-NULL-dict-with-a-no.patch
Patch0234: 0234-ec-Use-tiebreaker_inodelk-where-necessary.patch
Patch0235: 0235-cluster-syncop-Implement-tiebreaker-inodelk-entrylk.patch
Patch0236: 0236-cluster-syncop-Address-comments-in-3ad68df725ac32f83.patch
Patch0237: 0237-cluster-dht-Fix-dht_rename-lock-order.patch
Patch0238: 0238-quota-Build-is-failed-due-to-access-rpc-refcount-in-.patch
Patch0239: 0239-geo-rep-Fix-syncing-of-symlink.patch
Patch0240: 0240-shared-storage-Prevent-mounting-shared-storage-from-.patch
Patch0241: 0241-server-auth-add-option-for-strict-authentication.patch
Patch0242: 0242-feature-changelog-remove-unused-variable.patch
Patch0243: 0243-timer-Fix-possible-race-during-cleanup.patch
Patch0244: 0244-common-ha-All-statd-related-files-need-to-be-owned-b.patch
Patch0245: 0245-build-make-RHGS-version-available-for-server.patch
Patch0246: 0246-glusterd-Fix-for-memory-leak-in-get-state-detail.patch
Patch0247: 0247-protocol-server-unwind-as-per-op-version.patch
Patch0248: 0248-performance-md-cache-purge-cache-on-ENOENT-ESTALE-er.patch
Patch0249: 0249-cluster-dht-unwind-if-dht_selfheal_dir_mkdir-returns.patch
Patch0250: 0250-cluster-dht-act-as-passthrough-for-renames-on-single.patch
Patch0251: 0251-dht-gf_defrag_settle_hash-should-ignore-ENOENT-and-E.patch
Patch0252: 0252-glusterd-ganesha-Skip-non-ganesha-nodes-properly-for.patch
Patch0253: 0253-geo-rep-Fix-upgrade-issue.patch
Patch0254: 0254-posix-Avoid-changelog-retries-for-geo-rep.patch
Patch0255: 0255-glusterd-update-listen-backlog-value-to-1024.patch
Patch0256: 0256-rpc-set-listen-backlog-to-high-value.patch
Patch0257: 0257-rpc-rearm-listener-socket-early.patch
Patch0258: 0258-cluster-dht-log-error-only-if-layout-healing-is-requ.patch
Patch0259: 0259-Quota-Turn-on-ssl-for-crawler-clients-if-needed.patch
Patch0260: 0260-dht-Avoid-dict-log-flooding-for-internal-MDS-xattr.patch
Patch0261: 0261-libglusterfs-syncop-Add-syncop_entrylk.patch
Patch0262: 0262-cluster-dht-store-the-reaction-on-failures-per-lock.patch
Patch0263: 0263-server-resolver-don-t-trust-inode-table-for-RESOLVE_.patch
Patch0264: 0264-cluster-dht-fixes-to-parallel-renames-to-same-destin.patch
Patch0265: 0265-Glusterfsd-brick-crash-during-get-state.patch
Patch0266: 0266-glusterd-geo-rep-Fix-glusterd-crash.patch
Patch0267: 0267-geo-rep-scheduler-Fix-crash.patch
Patch0268: 0268-dht-Excessive-dict-is-null-logs-in-dht_discover_comp.patch
Patch0269: 0269-extras-Disable-choose-local-in-groups-virt-and-glust.patch
Patch0270: 0270-glusterfs-Resolve-brick-crashes-at-the-time-of-inode.patch
Patch0271: 0271-cli-Fix-for-gluster-volume-info-xml.patch
Patch0272: 0272-readdir-ahead-Fix-an-issue-with-parallel-readdir-and.patch
Patch0273: 0273-rpcsvc-Turn-off-ownthreads-for-Glusterfs-program.patch
Patch0274: 0274-client-protocol-fix-the-log-level-for-removexattr_cb.patch
Patch0275: 0275-afr-fix-bug-1363721.t-failure.patch
Patch0276: 0276-tests-check-volume-status-for-shd-being-up.patch
Patch0277: 0277-Revert-rpcsvc-Turn-off-ownthreads-for-Glusterfs-prog.patch
Patch0278: 0278-Revert-rpcsvc-correct-event-thread-scaling.patch
Patch0279: 0279-Revert-rpc-make-actor-search-parallel.patch
Patch0280: 0280-Revert-rpcsvc-scale-rpcsvc_request_handler-threads.patch
Patch0281: 0281-Revert-program-GF-DUMP-Shield-ping-processing-from-t.patch
Patch0282: 0282-cluster-dht-Remove-EIO-from-dht_inode_missing.patch
Patch0283: 0283-cluster-ec-Fix-pre-op-xattrop-management.patch
Patch0284: 0284-glusterd-glusterd-is-releasing-the-locks-before-time.patch
Patch0285: 0285-gluster-Allow-only-read-only-CLI-commands-via-remote.patch
Patch0286: 0286-glusterd-memory-leak-in-geo-rep-status.patch
Patch0287: 0287-Revert-performance-write-behind-fix-flush-stuck-by-f.patch
Patch0288: 0288-feature-locks-Unwind-response-based-on-clinet-versio.patch
Patch0289: 0289-changelog-fix-br-state-check.t-failure-for-brick_mux.patch
Patch0290: 0290-performance-open-behind-open-pending-fds-before-perm.patch
Patch0291: 0291-Core-The-lock-contention-on-gf_client_dump_inodes_to.patch
Patch0292: 0292-geo-rep-Fix-rename-of-directory-in-hybrid-crawl.patch
Patch0293: 0293-rpcsvc-correct-event-thread-scaling.patch
Patch0294: 0294-features-shard-Fix-missing-unlock-in-shard_fsync_sha.patch
Patch0295: 0295-dht-Excessive-dict-is-null-logs-in-dht_revalidate_cb.patch
Patch0296: 0296-cluster-dht-Increase-failure-count-for-lookup-failur.patch
Patch0297: 0297-dht-Delete-MDS-internal-xattr-from-dict-in-dht_getxa.patch
Patch0298: 0298-glusterd-Fix-for-shd-not-coming-up.patch
Patch0299: 0299-afr-heal-gfids-when-file-is-not-present-on-all-brick.patch
Patch0300: 0300-protocol-client-Don-t-send-fops-till-SETVOLUME-is-co.patch
Patch0301: 0301-storage-posix-Fix-posix_symlinks_match.patch
Patch0302: 0302-storage-posix-Handle-ENOSPC-correctly-in-zero_fill.patch
Patch0303: 0303-block-profile-enable-cluster.eager-lock-in-block-pro.patch
Patch0304: 0304-cluster-dht-Fix-rename-journal-in-changelog.patch
Patch0305: 0305-geo-rep-Fix-geo-rep-for-older-versions-of-unshare.patch
Patch0306: 0306-glusterfsd-Do-not-process-GLUSTERD_BRICK_XLATOR_OP-i.patch
Patch0307: 0307-glusterd-Introduce-daemon-log-level-cluster-wide-opt.patch
Patch0308: 0308-glusterd-Fix-glusterd-crash.patch
Patch0309: 0309-extras-group-add-database-workload-profile.patch
Patch0310: 0310-cluster-afr-Make-sure-lk-owner-is-assigned-at-the-ti.patch
Patch0311: 0311-glusterd-show-brick-online-after-port-registration.patch
Patch0312: 0312-glusterd-show-brick-online-after-port-registration-e.patch
Patch0313: 0313-dht-Inconsistent-permission-for-directories-after-br.patch
Patch0314: 0314-cluster-afr-Prevent-execution-of-code-after-call_cou.patch
Patch0315: 0315-changelog-fix-br-state-check.t-crash-for-brick_mux.patch
Patch0316: 0316-snapshot-remove-stale-entry.patch
Patch0317: 0317-geo-rep-scheduler-Fix-EBUSY-trace-back.patch
Patch0318: 0318-Quota-Fix-crawling-of-files.patch
Patch0319: 0319-glusterd-_is_prefix-should-handle-0-length-paths.patch
Patch0320: 0320-glusterd-log-improvements-on-brick-creation-validati.patch
Patch0321: 0321-geo-rep-Fix-symlink-rename-syncing-issue.patch
Patch0322: 0322-geo-rep-Cleanup-stale-unprocessed-xsync-changelogs.patch
Patch0323: 0323-cluster-afr-Mark-dirty-for-entry-transactions-for-qu.patch
Patch0324: 0324-dht-delete-tier-related-internal-xattr-in-dht_getxat.patch
Patch0325: 0325-core-dereference-check-on-the-variables-in-glusterfs.patch
Patch0326: 0326-glusterd-memory-leak-in-get-state.patch
Patch0327: 0327-afr-switch-lk_owner-only-when-pre-op-succeeds.patch
Patch0328: 0328-geo-rep-Fix-issues-with-gfid-conflict-handling.patch
Patch0329: 0329-cluster-dht-Set-loc-gfid-before-healing-attr.patch
Patch0330: 0330-posix-check-before-removing-stale-symlink.patch
Patch0331: 0331-rpc-free-registered-callback-programs.patch
Patch0332: 0332-rpc-rpc_clnt_connection_cleanup-is-crashed-due-to-do.patch
Patch0333: 0333-glusterd-Add-multiple-checks-before-attach-start-a-b.patch
Patch0334: 0334-glusterd-Bricks-of-a-normal-volumes-should-not-attac.patch
Patch0335: 0335-cluster-ec-set-others.eager-lock-option-off-by-defau.patch
Patch0336: 0336-dict-handle-negative-key-value-length-while-unserial.patch
Patch0337: 0337-glusterfs-Brick-process-is-crash-at-the-time-of-call.patch
Patch0338: 0338-posix-prevent-crash-when-SEEK_DATA-HOLE-is-not-suppo.patch
Patch0339: 0339-posix-remove-not-supported-get-set-content.patch
Patch0340: 0340-protocol-don-t-use-alloca.patch
Patch0341: 0341-Revert-glusterd-enable-brick-multiplexing-by-default.patch
Patch0342: 0342-glusterd-more-stricter-checks-of-if-brick-is-running.patch
Patch0343: 0343-core-Update-condition-in-get_xlator_by_name_or_type.patch
Patch0344: 0344-glusterd-Compare-volume_id-before-start-attach-a-bri.patch
Patch0345: 0345-io-stats-allow-only-relative-path-for-dumping-io-sta.patch
Patch0346: 0346-gfapi-Handle-the-path-glfs_resolve_at.patch
Patch0347: 0347-posix-fix-unused-variable-warning.patch
Patch0348: 0348-posix-disable-block-and-character-files.patch
Patch0349: 0349-posix-don-t-allow-.-path-in-name.patch
Patch0350: 0350-cluster-dht-fix-inode-ref-management-in-dht_heal_pat.patch
Patch0351: 0351-cluster-dht-Fixed-rebalanced-files.patch
Patch0352: 0352-snapshot-Fail-snapshot-creation-if-an-empty-descript.patch
Patch0353: 0353-snapshot-handshake-store-description-after-strdup.patch
Patch0354: 0354-snapshot-Fix-wrong-dictionary-key-in-snapshot-cleanu.patch
Patch0355: 0355-server-protocol-resolve-memory-leak.patch
Patch0356: 0356-io-stats-sanitize-the-dump-path-further.patch
Patch0357: 0357-snapshot-fix-snapshot-status-failure-due-to-symlink-.patch
Patch0358: 0358-glusterd-glusterd_brick_start-shouldn-t-try-to-bring.patch
Patch0359: 0359-storage-posix-Increment-trusted.pgfid-in-posix_mknod.patch
Patch0360: 0360-geo-rep-Make-automatic-gfid-conflict-resolution-opti.patch
Patch0361: 0361-ctr-skip-ctr-xlator-init-if-ctr-is-not-enabled.patch
Patch0362: 0362-glusterd-glusterd_brick_start-shouldn-t-cleanup-pidf.patch

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
Requires:         python2-gluster = %{version}-%{release}
Requires:         python2
%if ( 0%{?fedora} && 0%{?fedora} < 26 ) || ( 0%{?rhel} )
BuildRequires:    python-ctypes
%endif

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
Requires:         psmisc

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
Requires:         nfs-ganesha-gluster >= 2.4.1
Requires:         pcs, dbus
%if ( 0%{?rhel} && 0%{?rhel} == 6 )
Requires:         cman, pacemaker, corosync
%endif
%if ( ( 0%{?fedora} && 0%{?fedora} > 25 ) || ( 0%{?rhel} && 0%{?rhel} > 6 ) )
%if ( 0%{?rhel} )
Requires: selinux-policy >= 3.13.1-160
Requires(post):   policycoreutils-python
Requires(postun): policycoreutils-python
%else
Requires(post):   policycoreutils-python-utils
Requires(postun): policycoreutils-python-utils
%endif
%endif

%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} > 5 )
# we need portblock resource-agent in 3.9.5 and later.
Requires:         resource-agents >= 3.9.5
Requires:         net-tools
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
Requires:         python2
Requires:         python-prettytable
%if ( 0%{?fedora} && 0%{?fedora} < 26 ) || ( 0%{?rhel} )
BuildRequires:    python-ctypes
%endif
Requires:         python2-gluster = %{version}-%{release}
Requires:         rsync
Requires:         util-linux

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

%global _python_gluster_description \
GlusterFS is a distributed file-system capable of scaling to several\
petabytes. It aggregates various storage bricks over Infiniband RDMA\
or TCP/IP interconnect into one large parallel network file\
system. GlusterFS is one of the most sophisticated file systems in\
terms of features and extensibility.  It borrows a powerful concept\
called Translators from GNU Hurd kernel. Much of the code in GlusterFS\
is in user space and easily manageable.\
\
This package contains the python modules of GlusterFS and own gluster\
namespace.

%description -n python-gluster %{_python_gluster_description}

%package -n python2-gluster
Summary:          GlusterFS python library
Group:            Development/Tools
%{?python_provide:%python_provide python2-gluster}
Requires:         python2
Provides:         python-gluster = %{version}-%{release}
Obsoletes:        python-gluster < 3.10

%description -n python2-gluster %{_python_gluster_description}

%if ( 0%{!?_without_rdma:1} )
%package rdma
Summary:          GlusterFS rdma support for ib-verbs
Group:            Applications/File
%if ( 0%{?fedora} && 0%{?fedora} > 26 )
BuildRequires:    rdma-core-devel
%else
BuildRequires:    libibverbs-devel
BuildRequires:    librdmacm-devel >= 1.0.15
%endif
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
Requires:         python2 attr dbench file git libacl-devel net-tools
Requires:         nfs-utils xfsprogs yajl psmisc bc

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
Requires:         %{name}-server = %{version}-%{release}
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
# lvm2 for snapshot, and nfs-utils and rpcbind/portmap for gnfs server
Requires:         lvm2
Requires:         nfs-utils
%if ( 0%{?_with_systemd:1} )
%{?systemd_requires}
%else
Requires(post):   /sbin/chkconfig
Requires(preun):  /sbin/service
Requires(preun):  /sbin/chkconfig
Requires(postun): /sbin/service
%endif
%if (0%{?_with_firewalld:1})
# we install firewalld rules, so we need to have the directory owned
%if ( 0%{!?rhel} )
# not on RHEL because firewalld-filesystem appeared in 7.3
# when EL7 rpm gets weak dependencies we can add a Suggests:
Requires:         firewalld-filesystem
%endif
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
%if (0%{?_with_valgrind:1})
Requires:         valgrind
%endif

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

%if ( 0%{?_build_server} )
%if ( 0%{!?_without_events:1} )
%package events
Summary:          GlusterFS Events
Group:            Applications/File
Requires:         %{name}-server%{?_isa} = %{version}-%{release}
Requires:         python2 python-prettytable
Requires:         python2-gluster = %{version}-%{release}
%if ( 0%{?rhel} )
Requires:         python-requests
%else
Requires:         python2-requests
%endif
%if ( 0%{?rhel} && 0%{?rhel} < 7 )
Requires:         python-argparse
%endif
%if ( 0%{?_with_systemd:1} )
%{?systemd_requires}
%endif

%description events
GlusterFS Events

%endif
%endif

%prep
%setup -q -n %{name}-%{version}%{?prereltag}

# sanitization scriptlet for patches with file renames
ls %{_topdir}/SOURCES/*.patch | sort | \
while read p
do
    # if the destination file exists, its most probably stale
    # so we must remove it
    rename_to=( $(grep -i 'rename to' $p | cut -f 3 -d ' ') )
    if [ ${#rename_to[*]} -gt 0 ]; then
        for f in ${rename_to[*]}
        do
            if [ -f $f ]; then
                rm -f $f
            elif [ -d $f ]; then
                rm -rf $f
            fi
        done
    fi

    SOURCE_FILES=( $(egrep '^\-\-\- a/' $p | cut -f 2- -d '/') )
    DEST_FILES=( $(egrep '^\+\+\+ b/' $p | cut -f 2- -d '/') )
    EXCLUDE_DOCS=()
    for idx in ${!SOURCE_FILES[@]}; do
        # skip the doc 
        source_file=${SOURCE_FILES[$idx]}
        dest_file=${DEST_FILES[$idx]}
        if [[ "$dest_file" =~ ^doc/.+ ]]; then
            if [ "$source_file" != "dev/null" ] && [ ! -f "$dest_file" ]; then
                # if patch is being applied to a doc file and if the doc file
                # hasn't been added so far then we need to exclude it
                EXCLUDE_DOCS=( ${EXCLUDE_DOCS[*]} "$dest_file" )
            fi
        fi
    done
    EXCLUDE_DOCS_OPT=""
    for doc in ${EXCLUDE_DOCS}; do
        EXCLUDE_DOCS_OPT="--exclude=$doc $EXCLUDE_DOCS_OPT"
    done
    # apply the patch with 'git apply'
    git apply -p1 --exclude=rfc.sh \
                  --exclude=.gitignore \
                  --exclude=.testignore \
                  --exclude=MAINTAINERS \
                  --exclude=extras/checkpatch.pl \
                  --exclude=build-aux/checkpatch.pl \
                  --exclude='tests/*' \
                  ${EXCLUDE_DOCS_OPT} \
                  $p
done


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

./autogen.sh && %configure \
        %{?_with_cmocka} \
        %{?_with_debug} \
        %{?_with_valgrind} \
        %{?_with_tmpfilesdir} \
        %{?_without_bd} \
        %{?_without_epoll} \
        %{?_without_fusermount} \
        %{?_without_georeplication} \
        %{?_with_firewalld} \
        %{?_without_ocf} \
        %{?_without_rdma} \
        %{?_without_syslog} \
        %{?_without_tiering} \
        %{?_without_events}

# fix hardening and remove rpath in shlibs
%if ( 0%{?fedora} && 0%{?fedora} > 17 ) || ( 0%{?rhel} && 0%{?rhel} > 6 )
sed -i 's| \\\$compiler_flags |&\\\$LDFLAGS |' libtool
%endif
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|' libtool

make %{?_smp_mflags}

%check
make check

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
# Install include directory
install -p -m 0644 contrib/uuid/*.h \
    %{buildroot}%{_includedir}/glusterfs/
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
mkdir -p %{buildroot}%{_rundir}/gluster

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

# ganesha ghosts
%if ( 0%{?_build_server} )
mkdir -p %{buildroot}%{_sysconfdir}/ganesha
touch %{buildroot}%{_sysconfdir}/ganesha/ganesha-ha.conf
mkdir -p %{buildroot}%{_localstatedir}/run/gluster/shared_storage/nfs-ganesha/exports
touch %{buildroot}%{_localstatedir}/run/gluster/shared_storage/nfs-ganesha/ganesha.conf
touch %{buildroot}%{_localstatedir}/run/gluster/shared_storage/nfs-ganesha/ganesha-ha.conf
%endif

%if ( 0%{!?_without_georeplication:1} )
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/geo-replication
touch %{buildroot}%{_sharedstatedir}/glusterd/geo-replication/gsyncd_template.conf
install -D -p -m 0644 extras/glusterfs-georep-logrotate \
    %{buildroot}%{_sysconfdir}/logrotate.d/glusterfs-georep
%endif

touch %{buildroot}%{_sharedstatedir}/glusterd/glusterd.info
touch %{buildroot}%{_sharedstatedir}/glusterd/options
subdirs=(add-brick create copy-file delete gsync-create remove-brick reset set start stop)
for dir in ${subdirs[@]}; do
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

%if ( 0%{?_build_server} )
echo "RHGS 3.4.0" > %{buildroot}%{_datadir}/glusterfs/release
%endif

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

%if ( 0%{?_build_server} )
%if ( 0%{!?_without_events:1} )
%post events
%_init_restart glustereventsd
%endif
%endif

%if ( 0%{?rhel} == 5 )
%post fuse
modprobe fuse
exit 0
%endif

%if ( 0%{?_build_server} )
%if ( 0%{?fedora} && 0%{?fedora} > 25 || ( 0%{?rhel} && 0%{?rhel} > 6 ) )
%post ganesha
semanage boolean -m ganesha_use_fusefs --on
exit 0
%endif
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
%if ( 0%{_for_fedora_koji_builds} )
%_init_enable glusterfsd
%endif
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
    %firewalld_reload
%endif

%endif

##-----------------------------------------------------------------------------
## All %%pre should be placed here and keep them sorted
##
%pre
getent group gluster > /dev/null || groupadd -r gluster
getent passwd gluster > /dev/null || useradd -r -g gluster -d %{_rundir}/gluster -s /sbin/nologin -c "GlusterFS daemons" gluster
exit 0


##-----------------------------------------------------------------------------
## All %%preun should be placed here and keep them sorted
##
%if ( 0%{?_build_server} )
%if ( 0%{!?_without_events:1} )
%preun events
if [ $1 -eq 0 ]; then
    if [ -f %_init_glustereventsd ]; then
        %_init_stop glustereventsd
        %_init_disable glustereventsd
    fi
fi
exit 0
%endif

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
## All %%postun should be placed here and keep them sorted
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
%if ( 0%{?fedora} && 0%{?fedora} > 25  || ( 0%{?rhel} && 0%{?rhel} > 6 ) )
%postun ganesha
semanage boolean -m ganesha_use_fusefs --off
exit 0
%endif
%endif

%postun libs
/sbin/ldconfig

%if ( 0%{?_build_server} )
%postun server
/sbin/ldconfig
%if (0%{?_with_firewalld:1})
    %firewalld_reload
%endif
exit 0
%endif

##-----------------------------------------------------------------------------
## All %%trigger should be placed here and keep them sorted
##
%if ( 0%{?_build_server} )
%if ( 0%{?fedora} && 0%{?fedora} > 25  || ( 0%{?rhel} && 0%{?rhel} > 6 ) )
%trigger ganesha -- selinux-policy-targeted
semanage boolean -m ganesha_use_fusefs --on
exit 0
%endif
%endif

##-----------------------------------------------------------------------------
## All %%triggerun should be placed here and keep them sorted
##
%if ( 0%{?_build_server} )
%if ( 0%{?fedora} && 0%{?fedora} > 25 || ( 0%{?rhel} && 0%{?rhel} > 6 ) )
%triggerun ganesha -- selinux-policy-targeted
semanage boolean -m ganesha_use_fusefs --off
exit 0
%endif
%endif

##-----------------------------------------------------------------------------
## All %%files should be placed here and keep them grouped
##
%files
# exclude extra-xlators files
%if ( ! 0%{!?_without_extra_xlators:1} )
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/encryption/rot-13.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/quiesce.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/selinux.so
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
%exclude %{_prefix}/lib/ocf/*
%exclude %{_libexecdir}/ganesha/*
%exclude %{_prefix}/lib/ocf/resource.d/heartbeat/*
%exclude %{_sysconfdir}/ganesha/ganesha-ha.conf.sample

# exclude incrementalapi
%exclude %{_libexecdir}/glusterfs/*
%exclude %{_sbindir}/gfind_missing_files
%exclude %{_libexecdir}/glusterfs/glusterfind
%exclude %{_bindir}/glusterfind
%exclude %{_libexecdir}/glusterfs/peer_add_secret_pub
# exclude eventsapi files
%exclude %{_sysconfdir}/glusterfs/eventsconfig.json
%exclude %{_sharedstatedir}/glusterd/events
%exclude %{_libexecdir}/glusterfs/events
%exclude %{_libexecdir}/glusterfs/peer_eventsapi.py*
%exclude %{_sbindir}/glustereventsd
%exclude %{_sbindir}/gluster-eventsapi
%exclude %{_datadir}/glusterfs/scripts/eventsdash.py*
%if ( 0%{?_with_systemd:1} )
%exclude %{_unitdir}/glustereventsd.service
%exclude %_init_glusterfssharedstorage
%else
%exclude %{_sysconfdir}/init.d/glustereventsd
%endif
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
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/arbiter.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/bit-rot.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/bitrot-stub.so
%if ( 0%{!?_without_tiering:1} )
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/changetimerecorder.so
%endif
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/index.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/leases.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/locks.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/posix*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/snapview-server.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/marker.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/quota*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/trash.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/upcall.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mgmt*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/nfs*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/decompounder.so
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/protocol/server*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/storage*
%if ( 0%{!?_without_tiering:1} )
%exclude %{_libdir}/libgfdb.so.*
%endif
%exclude %{_sbindir}/gcron.py
%exclude %{_sbindir}/glfsheal
%exclude %{_sbindir}/glusterd
%exclude %{_sbindir}/gf_attach
%exclude %{_sbindir}/snap_scheduler.py
%exclude %{_datadir}/glusterfs/scripts/stop-all-gluster-processes.sh
%if ( 0%{?_with_systemd:1} )
%exclude %{_libexecdir}/glusterfs/mount-shared-storage.sh
%endif
%exclude %{_sbindir}/conf.py*
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
%dir %{_datadir}/glusterfs
%dir %{_datadir}/glusterfs/scripts
     %{_datadir}/glusterfs/scripts/post-upgrade-script-for-quota.sh
     %{_datadir}/glusterfs/scripts/pre-upgrade-script-for-quota.sh
# xlators that are needed on the client- and on the server-side
%dir %{_libdir}/glusterfs
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/auth
     %{_libdir}/glusterfs/%{version}%{?prereltag}/auth/addr.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/auth/login.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/rpc-transport
     %{_libdir}/glusterfs/%{version}%{?prereltag}/rpc-transport/socket.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/debug
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/debug/error-gen.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/debug/io-stats.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/debug/sink.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/debug/trace.so
%if ( ! ( 0%{?rhel} && 0%{?rhel} < 6 ) )
# RHEL-5 based distributions have a too old openssl
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/encryption
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/encryption/crypt.so
%endif
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features
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
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/io-cache.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/io-threads.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/md-cache.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/open-behind.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/quick-read.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/read-ahead.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/readdir-ahead.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/stat-prefetch.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/write-behind.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/nl-cache.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/system
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/system/posix-acl.so
%dir %attr(0775,gluster,gluster) %{_rundir}/gluster
%if 0%{?_tmpfilesdir:1}
%{_tmpfilesdir}/gluster.conf
%endif
%if ( ! 0%{?_build_server} )
%exclude %{_libdir}/pkgconfig/libgfchangelog.pc
%exclude %{_libdir}/pkgconfig/libgfdb.pc
%exclude %{_sbindir}/gluster-setgfid2path
%exclude %{_mandir}/man8/gluster-setgfid2path.8*
%if ( 0%{?_with_systemd:1} )
%exclude %{_datadir}/glusterfs/scripts/control-cpu-load.sh
%exclude %{_datadir}/glusterfs/scripts/control-mem.sh
%endif
%endif

%files api
%exclude %{_libdir}/*.so
# libgfapi files
%{_libdir}/libgfapi.*
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mount
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mount/api.so

%files api-devel
%{_libdir}/pkgconfig/glusterfs-api.pc
%{_libdir}/libgfapi.so
%dir %{_includedir}/glusterfs
%dir %{_includedir}/glusterfs/api
     %{_includedir}/glusterfs/api/*

%files cli
%{_sbindir}/gluster
%{_mandir}/man8/gluster.8*
%{_sysconfdir}/bash_completion.d/gluster

%files devel
%dir %{_includedir}/glusterfs
     %{_includedir}/glusterfs/*
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
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy/debug-trace.*
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy/helloworld.*
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy/negative.*
%if ( 0%{?_build_server} )
%{_libdir}/pkgconfig/libgfchangelog.pc
%else
%exclude %{_libdir}/pkgconfig/libgfchangelog.pc
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
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/cluster
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/cluster/*.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/protocol
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/protocol/client.so

%if ( 0%{!?_without_extra_xlators:1} )
%files extra-xlators
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/encryption
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/encryption/rot-13.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/quiesce.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/testing
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/testing/features
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/testing/features/template.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/testing/performance
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/testing/performance/symlink-cache.so
# Glupy Python files
%dir %{python2_sitelib}/gluster
%dir %{python2_sitelib}/gluster/glupy
     %{python2_sitelib}/gluster/glupy/*
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
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mount
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
%dir %{_libexecdir}/ganesha
%{_libexecdir}/ganesha/*
%{_prefix}/lib/ocf/resource.d/heartbeat/*
%{_sharedstatedir}/glusterd/hooks/1/start/post/S31ganesha-start.sh
%{_sysconfdir}/ganesha/ganesha-ha.conf.sample
%ghost      %attr(0644,-,-) %config(noreplace) %{_sysconfdir}/ganesha/ganesha-ha.conf
%ghost %dir %attr(0755,-,-) %{_localstatedir}/run/gluster/shared_storage/nfs-ganesha
%ghost %dir %attr(0755,-,-) %{_localstatedir}/run/gluster/shared_storage/nfs-ganesha/exports
%ghost      %attr(0644,-,-) %config(noreplace) %{_localstatedir}/run/gluster/shared_storage/nfs-ganesha/ganesha.conf
%ghost      %attr(0644,-,-) %config(noreplace) %{_localstatedir}/run/gluster/shared_storage/nfs-ganesha/ganesha-ha.conf
%endif

%if ( 0%{?_build_server} )
%if ( 0%{!?_without_georeplication:1} )
%files geo-replication
%config(noreplace) %{_sysconfdir}/logrotate.d/glusterfs-georep

%{_sbindir}/gfind_missing_files
%{_sbindir}/gluster-mountbroker
%dir %{_libexecdir}/glusterfs
%dir %{_libexecdir}/glusterfs/python
%dir %{_libexecdir}/glusterfs/python/syncdaemon
     %{_libexecdir}/glusterfs/gsyncd
     %{_libexecdir}/glusterfs/python/syncdaemon/*
     %{_libexecdir}/glusterfs/gverify.sh
     %{_libexecdir}/glusterfs/set_geo_rep_pem_keys.sh
     %{_libexecdir}/glusterfs/peer_gsec_create
     %{_libexecdir}/glusterfs/peer_mountbroker
     %{_libexecdir}/glusterfs/peer_mountbroker.py*
     %{_libexecdir}/glusterfs/gfind_missing_files
     %{_libexecdir}/glusterfs/peer_georep-sshkey.py*
%{_sbindir}/gluster-georep-sshkey

       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/geo-replication
%ghost      %attr(0644,-,-) %{_sharedstatedir}/glusterd/geo-replication/gsyncd_template.conf
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/gsync-create
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/gsync-create/post
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/gsync-create/post/S56glusterd-geo-rep-create-post.sh
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/gsync-create/pre

%dir %{_datadir}/glusterfs
%dir %{_datadir}/glusterfs/scripts
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

%files -n python2-gluster
# introducing glusterfs module in site packages.
# so that all other gluster submodules can reside in the same namespace.
%dir %{python2_sitelib}/gluster
     %{python2_sitelib}/gluster/__init__.*
     %{python2_sitelib}/gluster/cliutils

%if ( 0%{!?_without_rdma:1} )
%files rdma
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/rpc-transport
     %{_libdir}/glusterfs/%{version}%{?prereltag}/rpc-transport/rdma*
%endif

%if ( 0%{?_build_server} )
%if ( 0%{!?_without_regression_tests:1} )
%files regression-tests
%dir %{_datadir}/glusterfs
     %{_datadir}/glusterfs/run-tests.sh
     %{_datadir}/glusterfs/tests
%exclude %{_datadir}/glusterfs/tests/vagrant
%exclude %{_datadir}/share/glusterfs/tests/basic/rpm.t
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
# sysconf
%config(noreplace) %{_sysconfdir}/glusterfs
%exclude %{_sysconfdir}/glusterfs/eventsconfig.json
%config(noreplace) %{_sysconfdir}/sysconfig/glusterd
%if ( 0%{_for_fedora_koji_builds} )
%config(noreplace) %{_sysconfdir}/sysconfig/glusterfsd
%endif

# init files
%_init_glusterd
%if ( 0%{_for_fedora_koji_builds} )
%_init_glusterfsd
%endif
%if ( 0%{?_with_systemd:1} )
%_init_glusterfssharedstorage
%endif

# binaries
%{_sbindir}/glusterd
%{_sbindir}/glfsheal
%{_sbindir}/gf_attach
%{_sbindir}/gluster-setgfid2path
# {_sbindir}/glusterfsd is the actual binary, but glusterfs (client) is a
# symlink. The binary itself (and symlink) are part of the glusterfs-fuse
# package, because glusterfs-server depends on that anyway.

# Manpages
%{_mandir}/man8/gluster-setgfid2path.8*

# xlators
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/arbiter.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/bit-rot.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/bitrot-stub.so
%if ( 0%{!?_without_tiering:1} )
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/changetimerecorder.so
     %{_libdir}/libgfdb.so.*
%endif
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/index.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/locks.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/posix*
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/snapview-server.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/marker.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/quota*
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/selinux.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/trash.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/upcall.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/leases.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/nfs*
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mgmt
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mgmt/glusterd.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/protocol
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/protocol/server.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/storage
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/storage/bd.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/storage/posix.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/decompounder.so

# snap_scheduler
%{_sbindir}/snap_scheduler.py
%{_sbindir}/gcron.py
%{_sbindir}/conf.py

# /var/lib/glusterd, e.g. hookscripts, etc.
%ghost      %attr(0644,-,-) %config(noreplace) %{_sharedstatedir}/glusterd/glusterd.info
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/bitd
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/groups
            %attr(0644,-,-) %{_sharedstatedir}/glusterd/groups/virt
            %attr(0644,-,-) %{_sharedstatedir}/glusterd/groups/metadata-cache
            %attr(0644,-,-) %{_sharedstatedir}/glusterd/groups/gluster-block
            %attr(0644,-,-) %{_sharedstatedir}/glusterd/groups/db-workload
            %attr(0644,-,-) %{_sharedstatedir}/glusterd/groups/nl-cache
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/glusterfind
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/glusterfind/.keys
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/glustershd
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick/post
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick/post/disabled-quota-root-xattr-heal.sh
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick/post/S13create-subdir-mounts.sh
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick/pre
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick/pre/S28Quota-enable-root-xattr-heal.sh
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/create
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/create/post
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/create/pre
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/copy-file
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/copy-file/post
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/copy-file/pre
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/delete
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/delete/post
                            %{_sharedstatedir}/glusterd/hooks/1/delete/post/S57glusterfind-delete-post
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/delete/pre
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
%dir %{_libexecdir}/glusterfs
     %{_datadir}/glusterfs/release
%dir %{_datadir}/glusterfs/scripts
     %{_datadir}/glusterfs/scripts/stop-all-gluster-processes.sh
%if ( 0%{?_with_systemd:1} )
     %{_libexecdir}/glusterfs/mount-shared-storage.sh
     %{_datadir}/glusterfs/scripts/control-cpu-load.sh
     %{_datadir}/glusterfs/scripts/control-mem.sh
%endif

# Incrementalapi
     %{_libexecdir}/glusterfs/glusterfind
%{_bindir}/glusterfind
     %{_libexecdir}/glusterfs/peer_add_secret_pub

%if ( 0%{?_with_firewalld:1} )
%{_prefix}/lib/firewalld/services/glusterfs.xml
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

-- Since we run pretrans scripts only for RPMs built for a server build,
-- we can now use os.tmpname() since it is available on RHEL6 and later
-- platforms which are server platforms.
tmpname = os.tmpname()
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

-- Since we run pretrans scripts only for RPMs built for a server build,
-- we can now use os.tmpname() since it is available on RHEL6 and later
-- platforms which are server platforms.
tmpname = os.tmpname()
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

-- Since we run pretrans scripts only for RPMs built for a server build,
-- we can now use os.tmpname() since it is available on RHEL6 and later
-- platforms which are server platforms.
tmpname = os.tmpname()
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

-- Since we run pretrans scripts only for RPMs built for a server build,
-- we can now use os.tmpname() since it is available on RHEL6 and later
-- platforms which are server platforms.
tmpname = os.tmpname()
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

-- Since we run pretrans scripts only for RPMs built for a server build,
-- we can now use os.tmpname() since it is available on RHEL6 and later
-- platforms which are server platforms.
tmpname = os.tmpname()
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

-- Since we run pretrans scripts only for RPMs built for a server build,
-- we can now use os.tmpname() since it is available on RHEL6 and later
-- platforms which are server platforms.
tmpname = os.tmpname()
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

-- Since we run pretrans scripts only for RPMs built for a server build,
-- we can now use os.tmpname() since it is available on RHEL6 and later
-- platforms which are server platforms.
tmpname = os.tmpname()
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

-- Since we run pretrans scripts only for RPMs built for a server build,
-- we can now use os.tmpname() since it is available on RHEL6 and later
-- platforms which are server platforms.
tmpname = os.tmpname()
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

-- Since we run pretrans scripts only for RPMs built for a server build,
-- we can now use os.tmpname() since it is available on RHEL6 and later
-- platforms which are server platforms.
tmpname = os.tmpname()
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

-- Since we run pretrans scripts only for RPMs built for a server build,
-- we can now use os.tmpname() since it is available on RHEL6 and later
-- platforms which are server platforms.
tmpname = os.tmpname()
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

-- Since we run pretrans scripts only for RPMs built for a server build,
-- we can now use os.tmpname() since it is available on RHEL6 and later
-- platforms which are server platforms.
tmpname = os.tmpname()
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

-- Since we run pretrans scripts only for RPMs built for a server build,
-- we can now use os.tmpname() since it is available on RHEL6 and later
-- platforms which are server platforms.
tmpname = os.tmpname()
tmpfile = io.open(tmpname, "w")
tmpfile:write(script)
tmpfile:close()
ok, how, val = os.execute("/bin/bash " .. tmpname)
os.remove(tmpname)
if not (ok == 0) then
   error("Detected running glusterfs processes", ok)
end

%posttrans server
pidof -c -o %PPID -x glusterd &> /dev/null
if [ $? -eq 0 ]; then
    kill -9 `pgrep -f gsyncd.py` &> /dev/null

    killall --wait -SIGTERM glusterd &> /dev/null

    if [ "$?" != "0" ]; then
        echo "killall failed while killing glusterd"
    fi

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

# Events
%if ( 0%{?_build_server} )
%if ( 0%{!?_without_events:1} )
%files events
%config(noreplace) %{_sysconfdir}/glusterfs/eventsconfig.json
%dir %{_sharedstatedir}/glusterd
%dir %{_sharedstatedir}/glusterd/events
%dir %{_libexecdir}/glusterfs
     %{_libexecdir}/glusterfs/events
     %{_libexecdir}/glusterfs/peer_eventsapi.py*
%{_sbindir}/glustereventsd
%{_sbindir}/gluster-eventsapi
%{_datadir}/glusterfs/scripts/eventsdash.py*
%if ( 0%{?_with_systemd:1} )
%{_unitdir}/glustereventsd.service
%else
%{_sysconfdir}/init.d/glustereventsd
%endif
%endif
%endif

%changelog
* Mon Aug 27 2018 Milind Changire <mchangir@redhat.com> - 3.12.2-18
- fixes bugs bz#1524336 bz#1622029 bz#1622452

* Thu Aug 23 2018 Milind Changire <mchangir@redhat.com> - 3.12.2-17
- fixes bugs bz#1615578 bz#1619416 bz#1619538 bz#1620469 bz#1620765

* Tue Aug 14 2018 Milind Changire <mchangir@redhat.com> - 3.12.2-16
- fixes bugs bz#1569657 bz#1608352 bz#1609163 bz#1609724 bz#1610825 
  bz#1611151 bz#1612098 bz#1615338 bz#1615440

* Fri Jul 27 2018 Milind Changire <mchangir@redhat.com> - 3.12.2-15
- fixes bugs bz#1589279 bz#1598384 bz#1599362 bz#1599998 bz#1600790 
  bz#1601331 bz#1603103

* Wed Jul 18 2018 Milind Changire <mchangir@redhat.com> - 3.12.2-14
- fixes bugs bz#1547903 bz#1566336 bz#1568896 bz#1578716 bz#1581047 
  bz#1581231 bz#1582066 bz#1593865 bz#1597506 bz#1597511 bz#1597654 bz#1597768 
  bz#1598105 bz#1598356 bz#1599037 bz#1599823 bz#1600057 bz#1601314

* Thu Jun 28 2018 Milind Changire <mchangir@redhat.com> - 3.12.2-13
- fixes bugs bz#1493085 bz#1518710 bz#1554255 bz#1558948 bz#1558989 
  bz#1559452 bz#1567001 bz#1569312 bz#1569951 bz#1575539 bz#1575557 bz#1577051 
  bz#1580120 bz#1581184 bz#1581553 bz#1581647 bz#1582119 bz#1582129 bz#1582417 
  bz#1583047 bz#1588408 bz#1592666 bz#1594658

* Thu May 24 2018 Milind Changire <mchangir@redhat.com> - 3.12.2-12
- fixes bugs bz#1558989 bz#1580344 bz#1581057 bz#1581219

* Thu May 17 2018 Milind Changire <mchangir@redhat.com> - 3.12.2-11
- fixes bugs bz#1558989 bz#1575555 bz#1578647

* Tue May 15 2018 Milind Changire <mchangir@redhat.com> - 3.12.2-10
- fixes bugs bz#1488120 bz#1565577 bz#1568297 bz#1570586 bz#1572043 
  bz#1572075 bz#1575840 bz#1575877

* Wed May 09 2018 Milind Changire <mchangir@redhat.com> - 3.12.2-9
- fixes bugs bz#1546717 bz#1557551 bz#1558948 bz#1561999 bz#1563804 
  bz#1565015 bz#1565119 bz#1565399 bz#1565577 bz#1567100 bz#1567899 bz#1568374 
  bz#1568969 bz#1569490 bz#1570514 bz#1570541 bz#1570582 bz#1571645 bz#1572087 
  bz#1572585 bz#1575895

* Fri Apr 20 2018 Milind Changire <mchangir@redhat.com> - 3.12.2-8
- fixes bugs bz#1466129 bz#1475779 bz#1523216 bz#1535281 bz#1546941 
  bz#1550315 bz#1550991 bz#1553677 bz#1554291 bz#1559452 bz#1560955 bz#1562744 
  bz#1563692 bz#1565962 bz#1567110 bz#1569457

* Wed Apr 04 2018 Milind Changire <mchangir@redhat.com> - 3.12.2-7
- fixes bugs bz#958062 bz#1186664 bz#1226874 bz#1446046 bz#1529451 bz#1550315 
  bz#1557365 bz#1559884 bz#1561733

* Mon Mar 26 2018 Milind Changire <mchangir@redhat.com> - 3.12.2-6
- fixes bugs bz#1491785 bz#1518710 bz#1523599 bz#1528733 bz#1550474 
  bz#1550982 bz#1551186 bz#1552360 bz#1552414 bz#1552425 bz#1554255 bz#1554905 
  bz#1555261 bz#1556895 bz#1557297 bz#1559084 bz#1559788

* Wed Mar 07 2018 Milind Changire <mchangir@redhat.com> - 3.12.2-5
- fixes bugs bz#1378371 bz#1384983 bz#1472445 bz#1493085 bz#1508999 
  bz#1516638 bz#1518260 bz#1529072 bz#1530519 bz#1537357 bz#1540908 bz#1541122 
  bz#1541932 bz#1543068 bz#1544382 bz#1544852 bz#1545570 bz#1546075 bz#1546945 
  bz#1546960 bz#1547012 bz#1549497

* Mon Feb 12 2018 Milind Changire <mchangir@redhat.com> - 3.12.2-4
- fixes bugs bz#1446125 bz#1467536 bz#1530146 bz#1540600 bz#1540664 
  bz#1540961 bz#1541830 bz#1543296

* Mon Feb 05 2018 Milind Changire <mchangir@redhat.com> - 3.12.2-3
- fixes bugs bz#1446125 bz#1463592 bz#1516249 bz#1517463 bz#1527309 
  bz#1530325 bz#1531041 bz#1539699 bz#1540011

* Wed Jan 17 2018 Milind Changire <mchangir@redhat.com> - 3.12.2-2
- fixes bugs bz#1264911 bz#1277924 bz#1286820 bz#1360331 bz#1401969 
  bz#1410719 bz#1419438 bz#1426042 bz#1444820 bz#1459101 bz#1464150 bz#1464350 
  bz#1466122 bz#1466129 bz#1467903 bz#1468972 bz#1476876 bz#1484446 bz#1492591 
  bz#1498391 bz#1498730 bz#1499865 bz#1500704 bz#1501345 bz#1505570 bz#1507361 
  bz#1507394 bz#1509102 bz#1509191 bz#1509810 bz#1509833 bz#1511766 bz#1512470 
  bz#1512496 bz#1512963 bz#1515051 bz#1519076 bz#1519740 bz#1534253 bz#1534530

* Wed Nov 15 2017 Milind Changire <mchangir@redhat.com> - 3.12.2-1
- rebase to upstream glusterfs at v3.12.2
- fixes bugs bz#1442983 bz#1474745 bz#1503244 bz#1505363 bz#1509102

