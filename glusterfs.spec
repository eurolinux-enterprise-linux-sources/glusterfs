# if you make changes, the it is advised to increment this number, and provide
# a descriptive suffix to identify who owns or what the change represents
# e.g. release_version 2.MSW
%global release 2%{?dist}
%global _sharedstatedir /var/lib

%global version 3.4.0.40rhs


# if you wish to build the server rpms, compile like this...
# rpmbuild -ta glusterfs-3.4.0.30rhs.tar.gz --with server
%if "%{?_with_server}"
%define _build_server 1
%else
%if "%{dist}" == ".el6rhs"
%define _build_server 1
%else
%define _build_server 0
%endif
%endif

%global _hardened_build 1

%global _for_fedora_koji_builds 0

# uncomment and add '%' to use the prereltag for pre-releases
# global prereltag beta2

# if you wish to compile an rpm without rdma support, compile like this...
# rpmbuild -ta glusterfs-3.4.0.30rhs.tar.gz --without rdma
%{?_without_rdma:%global _without_rdma --disable-ibverbs}

# No RDMA Support on s390(x)
%ifarch s390 s390x
%global _without_rdma --disable-ibverbs
%endif

# if you wish to compile an rpm without epoll...
# rpmbuild -ta glusterfs-3.4.0.30rhs.tar.gz --without epoll
%{?_without_epoll:%global _without_epoll --disable-epoll}

# if you wish to compile an rpm without fusermount...
# rpmbuild -ta glusterfs-3.4.0.30rhs.tar.gz --without fusermount
%{?_without_fusermount:%global _without_fusermount --disable-fusermount}

%global _can_georeplicate 1

# if you wish to compile an rpm without geo-replication support, compile like this...
# rpmbuild -ta glusterfs-3.4.0.30rhs.tar.gz --without georeplication
%{?_without_georeplication:%global _without_georeplication --disable-geo-replication}

# if you wish to compile an rpm without the OCF resource agents...
# rpmbuild -ta glusterfs-3.4.0.30rhs.tar.gz --without ocf
%{?_without_ocf:%global _without_ocf --without-ocf}

# disable ocf as it is not required for rhs
%global _without_ocf --without-ocf

# if you wish to compile an rpm without the BD map support...
# rpmbuild -ta glusterfs-3.4.0.30rhs.tar.gz --without bd
%{?_without_bd:%global _without_bd --disable-bd-xlator}

%if ( 0%{?rhel} && 0%{?rhel} < 6 )
%define _without_bd true
%endif

# if you wish to build rpms without syslog logging, compile like this
# rpmbuild -ta glusterfs-3.4.0.30rhstar.gz --without syslog
%{?_without_syslog:%global _without_syslog --disable-syslog}

# disable syslog if dist is not for RHS and rhel <= 6.  These
# platoforms don't have either rsyslog-mmjsonparse or rsyslog-mmcount
%if ( 0%{?rhel} && 0%{?rhel} <= 6 && "%{dist}" != ".el6rhs" )
%global _without_syslog --disable-syslog
%endif

# disable syslog forcefully as rhel < 6 doesn't have rsyslog
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
%global _without_syslog --disable-syslog
%endif

%if ( 0%{?fedora} && 0%{?fedora} > 16 ) || ( 0%{?rhel} && 0%{?rhel} > 6 )
%global           _with_systemd true
%endif

Summary:          Cluster File System
%if ( 0%{_for_fedora_koji_builds} )
Name:             glusterfs
Version:          3.4.0
Release:          0.5%{?prereltag:.%{prereltag}}%{?dist}
Vendor:           Fedora Project
%else
Name:             glusterfs
Version:          %{version}
Release:          %{release}
Vendor:           Red Hat, Inc.
Packager:         gluster-users@gluster.org
ExclusiveArch:    x86_64 aarch64
%endif
License:          GPLv2 or LGPLv3+
Group:            System Environment/Base
URL:              http://www.gluster.org/docs/index.php/GlusterFS
Source0:          glusterfs-%{version}.tar.gz

BuildRoot:        %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

%if ( 0%{?_with_systemd:1} )
%if ( 0%{_for_fedora_koji_builds} )
%global glusterfsd_service %{S:%{SOURCE11}}
%endif
BuildRequires:    systemd-units
Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
%define _init_enable()  /bin/systemctl enable %1.service ;
%define _init_disable() /bin/systemctl disable %1.service ;
%define _init_restart() /bin/systemctl try-restart %1.service ;
%define _init_stop()    /bin/systemctl stop %1.service ;
%define _init_install() %{__install} -D -p -m 0644 %1 %{buildroot}%{_unitdir}/%2.service ;
# can't seem to make a generic macro that works
%define _init_glusterd   %{_unitdir}/glusterd.service
%define _init_glusterfsd %{_unitdir}/glusterfsd.service
%else
%if ( 0%{_for_fedora_koji_builds} )
%global glusterfsd_service %{S:%{SOURCE13}}
%endif
Requires(post):   /sbin/chkconfig
Requires(preun):  /sbin/service
Requires(preun):  /sbin/chkconfig
Requires(postun): /sbin/service
%define _init_enable()  /sbin/chkconfig --add %1 ;
%define _init_disable() /sbin/chkconfig --del %1 ;
%define _init_restart() /sbin/service %1 condrestart &>/dev/null ;
%define _init_stop()    /sbin/service %1 stop &>/dev/null ;
%define _init_install() %{__install} -D -p -m 0755 %1 %{buildroot}%{_sysconfdir}/init.d/%2 ;
# can't seem to make a generic macro that works
%define _init_glusterd   %{_sysconfdir}/init.d/glusterd
%define _init_glusterfsd %{_sysconfdir}/init.d/glusterfsd
%endif

BuildRequires:    bison flex
BuildRequires:    gcc make automake libtool
BuildRequires:    ncurses-devel readline-devel
BuildRequires:    libxml2-devel openssl-devel
BuildRequires:    libaio-devel
BuildRequires:    systemtap-sdt-devel
BuildRequires:    python-devel
BuildRequires:    python-ctypes
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
%if ( 0%{!?_without_bd:1} )
BuildRequires:    lvm2-devel
%endif
%endif
%if ( 0%{?rhel} && 0%{?rhel} <= 5 )
BuildRequires:    python-simplejson
%endif
Requires: openssl
Requires:         %{name}-libs = %{version}-%{release}

Obsoletes:        hekafs <= 0.7
Obsoletes:        %{name}-libs <= 2.0.0
Obsoletes:        %{name}-common < %{version}-%{release}
Obsoletes:        %{name}-core < %{version}-%{release}
Provides:         %{name}-common = %{version}-%{release}
Provides:         %{name}-core = %{version}-%{release}

# We do not want to generate useless provides and requires for xlator .so files
# Filter all generated:
#
# TODO: RHEL5 does not have a convenient solution
%if ( 0%{?rhel} == 6 )
    # filter_setup exists in RHEL6 only
    %filter_provides_in %{_libdir}/glusterfs/%{version}/
    %global __filter_from_req %{?__filter_from_req} | %{__grep} -v -P '^(?!lib).*\.so.*$'
    %filter_setup
%else
    # modern rpm and current Fedora do not generate requires when the
    # provides are filtered
    %global __provides_exclude_from ^%{_libdir}/glusterfs/%{version}/.*$
%endif

%description
GlusterFS is a clustered file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package includes the glusterfs binary, the glusterfsd daemon and the
gluster command line, libglusterfs and glusterfs translator modules common to
both GlusterFS server and client framework.

%package libs
Summary:          GlusterFS common libraries
Group:            Applications/File
%if ( 0%{!?_without_syslog:1} )
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} > 6 )
Requires:         rsyslog-mmjsonparse
%endif
%if ( 0%{?rhel} && 0%{?rhel} == 6 )
# rsyslog-mmcount should be installed manually before enabling new logging framework
#Requires:         rsyslog-mmcount
%endif
%endif

%description libs
GlusterFS is a clustered file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the base GlusterFS libraries

%if ( 0%{!?_without_rdma:1} )
%package rdma
Summary:          GlusterFS rdma support for ib-verbs
Group:            Applications/File
BuildRequires:    libibverbs-devel
BuildRequires:    librdmacm-devel
Requires:         %{name} = %{version}-%{release}

%description rdma
GlusterFS is a clustered file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides support to ib-verbs library.
%endif

%if 0%{?_build_server}
%if 0%{?_can_georeplicate}
%if ( 0%{!?_without_georeplication:1} )
%package geo-replication
Summary:          GlusterFS Geo-replication
Group:            Applications/File
Requires:         %{name} = %{version}-%{release}
# Strict dependency for `ls extras/geo-rep/*` scripts
Requires:         attr
Requires:         openssh-clients

%description geo-replication
GlusterFS is a clustered file-system capable of scaling to several
peta-bytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file system in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in userspace and easily manageable.

This package provides support to geo-replication.
%endif
%endif
%endif

%package fuse
Summary:          Fuse client
Group:            Applications/File
BuildRequires:    fuse-devel
#%if ( 0%{!?_without_fusermount:1} )
#Requires:         /usr/bin/fusermount
#%endif

Requires:         %{name} = %{version}-%{release}

Obsoletes:        %{name}-client < %{version}-%{release}
Provides:         %{name}-client = %{version}-%{release}

%description fuse
GlusterFS is a clustered file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides support to FUSE based clients.

%if 0%{?_build_server}
%package server
Summary:          Clustered file-system server
License:          GPLv3+
Group:            System Environment/Daemons
Requires:         %{name} = %{version}-%{release}
Requires:         %{name}-libs = %{version}-%{release}
Requires:         %{name}-fuse = %{version}-%{release}
Requires:         %{name}-geo-replication = %{version}-%{release}
Requires:         openssl
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
Requires:         rpcbind
%else
Requires:         portmap
%endif

%description server
GlusterFS is a clustered file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the glusterfs server daemon.
%endif

%package api
Summary:          Clustered file-system api library
License:          GPLv2 or LGPLv3+
Group:            System Environment/Daemons
Requires:         %{name}-libs = %{version}-%{release}

%description api
GlusterFS is a clustered file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the glusterfs libgfapi library

%if 0%{?_build_server}
%if ( 0%{!?_without_ocf:1} )
%package resource-agents
Summary:          OCF Resource Agents for GlusterFS
License:          GPLv3+
%if ( ! ( 0%{?rhel} && 0%{?rhel} < 6 ) )
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
Requires:         glusterfs-server
# depending on the distribution, we need pacemaker or resource-agents
Requires:         %{_prefix}/lib/ocf/resource.d

%description resource-agents
GlusterFS is a clustered file-system capable of scaling to several
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

%package devel
Summary:          Development Libraries
License:          GPLv2 or LGPLv3+
Group:            Development/Libraries
Requires:         %{name}-libs = %{version}-%{release}

%description devel
GlusterFS is a clustered file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the development libraries.


%package api-devel
Summary:          Development Libraries
License:          GPLv2 or LGPLv3+
Group:            Development/Libraries
Requires:         %{name}-api = %{version}-%{release}

%description api-devel
GlusterFS is a clustered file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the api include files.

%prep
%setup -q -n %{name}-%{version}%{?prereltag}

%build
./autogen.sh
%configure %{?_without_rdma} %{?_without_epoll} %{?_without_fusermount} %{?_without_georeplication} %{?_without_ocf} %{?_without_bd} %{?_without_syslog}

# fix hardening and remove rpath in shlibs
%if ( 0%{?fedora} && 0%{?fedora} > 17 ) || ( 0%{?rhel} && 0%{?rhel} > 6 )
%{__sed} -i 's| \\\$compiler_flags |&\\\$LDFLAGS |' libtool
%endif
%{__sed} -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|' libtool
%{__sed} -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|' libtool

%{__make} %{?_smp_mflags}

%install
%{__rm} -rf %{buildroot}
%{__make} install DESTDIR=%{buildroot}
# Install include directory
%{__mkdir_p} %{buildroot}%{_includedir}/glusterfs
%{__install} -p -m 0644 libglusterfs/src/*.h \
    %{buildroot}%{_includedir}/glusterfs/
%{__install} -p -m 0644 contrib/uuid/*.h \
    %{buildroot}%{_includedir}/glusterfs/
# Following needed by hekafs multi-tenant translator
%{__mkdir_p} %{buildroot}%{_includedir}/glusterfs/rpc
%{__install} -p -m 0644 rpc/rpc-lib/src/*.h \
    %{buildroot}%{_includedir}/glusterfs/rpc/
%{__install} -p -m 0644 rpc/xdr/src/*.h \
    %{buildroot}%{_includedir}/glusterfs/rpc/
%{__mkdir_p} %{buildroot}%{_includedir}/glusterfs/server
%{__install} -p -m 0644 xlators/protocol/server/src/*.h \
    %{buildroot}%{_includedir}/glusterfs/server/
%if ( 0%{_for_fedora_koji_builds} )
%{__install} -D -p -m 0644 %{SOURCE1} \
    %{buildroot}%{_sysconfdir}/sysconfig/glusterd
%{__install} -D -p -m 0644 %{SOURCE2} \
    %{buildroot}%{_sysconfdir}/sysconfig/glusterfsd
%else
%{__install} -D -p -m 0644 extras/glusterd-sysconfig \
    %{buildroot}%{_sysconfdir}/sysconfig/glusterd
%endif

%if ( 0%{_for_fedora_koji_builds} )
%if ( 0%{?rhel} && 0%{?rhel} <= 5 )
%{__install} -D -p -m 0755 %{SOURCE6} \
    %{buildroot}%{_sysconfdir}/sysconfig/modules/glusterfs-fuse.modules
%endif
%endif

%{__mkdir_p} %{buildroot}%{_localstatedir}/log/glusterd
%{__mkdir_p} %{buildroot}%{_localstatedir}/log/glusterfs
%{__mkdir_p} %{buildroot}%{_localstatedir}/log/glusterfsd
%{__mkdir_p} %{buildroot}%{_localstatedir}/run/gluster

# Remove unwanted files from all the shared libraries
find %{buildroot}%{_libdir} -name '*.a' -delete
find %{buildroot}%{_libdir} -name '*.la' -delete

# Remove installed docs, they're included by %%doc
%{__rm} -rf %{buildroot}%{_datadir}/doc/glusterfs/

# Remove benchmarking and other unpackaged files
%{__rm} -rf %{buildroot}/benchmarking
%{__rm} -f %{buildroot}/glusterfs-mode.el
%{__rm} -f %{buildroot}/glusterfs.vim

# Create working directory
%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd

# Update configuration file to /var/lib working directory
sed -i 's|option working-directory /etc/glusterd|option working-directory %{_sharedstatedir}/glusterd|g' \
    %{buildroot}%{_sysconfdir}/glusterfs/glusterd.vol

%if 0%{?_build_server}
# Install glusterfsd .service or init.d file
%if ( 0%{?_with_systemd:1} )
%if ( 0%{_for_fedora_koji_builds} )
%_init_install %{glusterfsd_service} glusterfsd
%endif
%endif

%if ( 0%{_for_fedora_koji_builds} )
# Client logrotate entry
%{__install} -D -p -m 0644 %{SOURCE3} \
    %{buildroot}%{_sysconfdir}/logrotate.d/glusterfs-fuse

# Server logrotate entry
%{__install} -D -p -m 0644 %{SOURCE4} \
    %{buildroot}%{_sysconfdir}/logrotate.d/glusterd
# Legacy server logrotate entry
%{__install} -D -p -m 0644 %{SOURCE5} \
    %{buildroot}%{_sysconfdir}/logrotate.d/glusterfsd
%else
%{__install} -D -p -m 0644 extras/glusterfs-logrotate \
    %{buildroot}%{_sysconfdir}/logrotate.d/glusterfs
#geo replication logrotate file.
%{__install} -D -p -m 0644 extras/glusterfs-georep-logrotate \
    %{buildroot}%{_sysconfdir}/logrotate.d/glusterfs-georep
%endif

%if ( 0%{!?_without_georeplication:1} )
# geo-rep ghosts
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/geo-replication
#touch %{buildroot}%{_sharedstatedir}/glusterd/geo-replication/gsyncd_template.conf
%endif

# Following needed by the hooks interface
subdirs=("add-brick" "create" "delete" "remove-brick" "set" "start" "stop" "gsync-create")
for dir in ${subdirs[@]}
do
%{__mkdir_p} %{buildroot}%{_datadir}/glusterfs/hook-scripts/"$dir"/{pre,post}
%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/"$dir"/{pre,post}
done
%{__install} -p -m 0744 extras/hook-scripts/start/post/*.sh   \
    %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/start/post
%{__install} -p -m 0744 extras/hook-scripts/stop/pre/*.sh   \
    %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/stop/pre
%{__install} -p -m 0744 extras/hook-scripts/set/post/*.sh   \
    %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/set/post
%{__install} -p -m 0744 extras/hook-scripts/S56glusterd-geo-rep-create-post.sh \
    %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/gsync-create/post
%{__install} -p -m 0744 extras/hook-scripts/add-brick/post/*.sh   \
    %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/add-brick/post
%{__install} -p -m 0744 extras/hook-scripts/add-brick/pre/*.sh   \
    %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/add-brick/pre
%endif

%if !0%{?_build_server}
echo "Removing files that are only used in the server subpackages."
rm %{buildroot}%{_sysconfdir}/glusterfs/glusterd.vol
rm %{buildroot}%{_sysconfdir}/init.d/glusterd
rm %{buildroot}%{_sbindir}/gluster
rm %{buildroot}%{_sbindir}/glusterd
rm %{buildroot}%{_libexecdir}/glusterfs/gsyncd
rm -rf %{buildroot}%{_libexecdir}/glusterfs/python/syncdaemon
rm -rf %{buildroot}%{_libexecdir}/glusterfs/quota
rm %{buildroot}%{_sysconfdir}/sysconfig/glusterd
rm %{buildroot}%{_libexecdir}/glusterfs/gverify.sh
rm %{buildroot}%{_libexecdir}/glusterfs/peer_add_secret_pub
rm %{buildroot}%{_libexecdir}/glusterfs/peer_gsec_create
rm -rf %{buildroot}%{_prefix}/lib/ocf/resource.d/glusterfs
rm %{buildroot}%{_datadir}/glusterfs/scripts/generate-gfid-file.sh
rm %{buildroot}%{_datadir}/glusterfs/scripts/get-gfid.sh
rm %{buildroot}%{_datadir}/glusterfs/scripts/gsync-sync-gfid
rm %{buildroot}%{_datadir}/glusterfs/scripts/gsync-upgrade.sh
rm %{buildroot}%{_datadir}/glusterfs/scripts/slave-upgrade.sh
%endif

%if ( 0%{!?_without_syslog:1} )
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} > 6 )
%{__install} -D -p -m 0644 extras/gluster-rsyslog-7.2.conf \
    %{buildroot}%{_sysconfdir}/rsyslog.d/gluster.conf
%endif

%if ( 0%{?rhel} && 0%{?rhel} == 6 )
%{__install} -D -p -m 0644 extras/gluster-rsyslog-5.8.conf \
    %{buildroot}%{_sysconfdir}/rsyslog.d/gluster.conf
%endif

%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
%{__install} -D -p -m 0644 extras/logger.conf.example \
    %{buildroot}%{_sysconfdir}/glusterfs/logger.conf.example
%endif
%endif

%if ( !0%{!?_without_syslog:1} )
rm %{buildroot}%{_sysconfdir}/glusterfs/gluster-rsyslog-5.8.conf
rm %{buildroot}%{_sysconfdir}/glusterfs/gluster-rsyslog-7.2.conf
rm %{buildroot}%{_sysconfdir}/glusterfs/logger.conf.example
%endif

# the rest of the ghosts
#touch %{buildroot}%{_sharedstatedir}/glusterd/glusterd.info
#touch %{buildroot}%{_sharedstatedir}/glusterd/options
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/stop
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/stop/post
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/stop/pre
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/start
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/start/post
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/start/pre
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/remove-brick
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/remove-brick/post
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/remove-brick/pre
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/add-brick
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/add-brick/post
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/add-brick/pre
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/set
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/set/post
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/set/pre
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/create
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/create/post
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/create/pre
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/delete
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/delete/post
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/delete/pre
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/copy-file
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/copy-file/post
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/copy-file/pre
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/gsync-create
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/gsync-create/post
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/gsync-create/pre
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/glustershd
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/peers
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/vols
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/groups
#%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/nfs/run
#touch %{buildroot}%{_sharedstatedir}/glusterd/nfs/nfs-server.vol
#touch %{buildroot}%{_sharedstatedir}/glusterd/nfs/run/nfs.pid

%clean
%{__rm} -rf %{buildroot}

%pre
pidof -c -o %PPID -x glusterfsd &>/dev/null
if [ $? -eq 0 ]; then
   echo "ERROR: Please kill gluster processes.. installation cannot proceed"
   echo "Usage: \$ pkill gluster "
   exit 1
fi

%post
/sbin/ldconfig

%postun
/sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc ChangeLog COPYING-GPLV2 COPYING-LGPLV3 INSTALL README THANKS
%config(noreplace) %{_sysconfdir}/glusterfs/glusterfs-logrotate
%config(noreplace) %{_sysconfdir}/glusterfs/glusterfs-georep-logrotate
#%config(noreplace) %{_sysconfdir}/logrotate.d/*
#%config(noreplace) %{_sysconfdir}/sysconfig/*
%config(noreplace) %{_sysconfdir}/glusterfs/group-virt.example
%config(noreplace) %{_sysconfdir}/glusterfs/group-small-file-perf.example
%if ( 0%{!?_without_syslog:1} )
%config(noreplace) %{_sysconfdir}/glusterfs/gluster-rsyslog-5.8.conf
%config(noreplace) %{_sysconfdir}/glusterfs/gluster-rsyslog-7.2.conf
%config(noreplace) %{_sysconfdir}/glusterfs/logger.conf.example
%endif
%{_libdir}/glusterfs
%{_sbindir}/glusterfs*
%{_mandir}/man8/*gluster*.8*
%dir %{_localstatedir}/log/glusterfs
%dir %{_localstatedir}/run/gluster
%if ( 0%{!?_without_rdma:1} )
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/rpc-transport/rdma*
%endif
# server-side, etc., xlators in other RPMs
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mount/api*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mount/fuse*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/storage*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/posix*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/protocol/server*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mgmt*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/nfs*
# sample xlators not generally used or usable
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/encryption/rot-13*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/mac-compat*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/testing/performance/symlink-cache*

%pre libs
pidof -c -o %PPID -x glusterfsd &>/dev/null
if [ $? -eq 0 ]; then
   echo "ERROR: Please kill gluster processes.. installation cannot proceed"
   echo "Usage: \$ pkill gluster "
   exit 1
fi

%post libs
/sbin/ldconfig
%if ( 0%{!?_without_syslog:1} )
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
%_init_restart rsyslog
%endif
%endif

%postun libs
/sbin/ldconfig
%if ( 0%{!?_without_syslog:1} )
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
%_init_restart rsyslog
%endif
%endif

%files libs
%{_libdir}/*.so.*
%if ( 0%{!?_without_syslog:1} )
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
%{_sysconfdir}/rsyslog.d/gluster.conf
%endif
%endif
%exclude %{_libdir}/libgfapi.*


%if ( 0%{!?_without_rdma:1} )

%pre rdma
pidof -c -o %PPID -x glusterfsd &>/dev/null
if [ $? -eq 0 ]; then
   echo "ERROR: Please kill gluster processes.. installation cannot proceed"
   echo "Usage: \$ pkill gluster "
   exit 1
fi

%files rdma
%defattr(-,root,root,-)
%{_libdir}/glusterfs/%{version}%{?prereltag}/rpc-transport/rdma*
%endif

%if 0%{?_build_server}
%if 0%{?_can_georeplicate}
%if ( 0%{!?_without_georeplication:1} )

%pre geo-replication
pidof -c -o %PPID -x glusterfsd &>/dev/null
if [ $? -eq 0 ]; then
   echo "ERROR: Please kill gluster processes.. installation cannot proceed"
   echo "Usage: \$ pkill gluster "
   exit 1
fi

%post geo-replication
%{__chmod} +x %{_datadir}/glusterfs/scripts/get-gfid.sh

#restart glusterd.
#if [ $1 -ge 1 ]; then
#    %_init_restart glusterd
#fi

%files geo-replication
%defattr(-,root,root)
%{_sysconfdir}/logrotate.d/glusterfs-georep
%{_libexecdir}/glusterfs/gsyncd
%{_libexecdir}/glusterfs/python/syncdaemon/*
%{_libexecdir}/glusterfs/gverify.sh
%{_libexecdir}/glusterfs/peer_add_secret_pub
%{_libexecdir}/glusterfs/peer_gsec_create
%{_sharedstatedir}/glusterd/hooks/1/gsync-create/post/S56glusterd-geo-rep-create-post.sh
%{_datadir}/glusterfs/scripts/get-gfid.sh
%{_datadir}/glusterfs/scripts/slave-upgrade.sh
%{_datadir}/glusterfs/scripts/gsync-upgrade.sh
%{_datadir}/glusterfs/scripts/generate-gfid-file.sh
%{_datadir}/glusterfs/scripts/gsync-sync-gfid
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/gsync-create/post
#%ghost %attr(0644,-,-) %{_sharedstatedir}/glusterd/hooks/1/gsync-create/post/S56glusterd-geo-rep-create-post.sh
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/geo-replication
#%ghost %attr(0644,-,-) %{_sharedstatedir}/glusterd/geo-replication/gsyncd_template.conf
%endif
# need to copy the upgrade scripts here
%endif
%endif

%pre fuse
pidof -c -o %PPID -x glusterfsd &>/dev/null
if [ $? -eq 0 ]; then
   echo "ERROR: Please kill gluster processes.. installation cannot proceed"
   echo "Usage: \$ pkill gluster "
   exit 1
fi

%files fuse
%defattr(-,root,root,-)
%if ( 0%{_for_fedora_koji_builds} )
%config(noreplace) %{_sysconfdir}/logrotate.d/glusterfs-fuse
%endif
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mount/fuse*
/sbin/mount.glusterfs
%if ( 0%{!?_without_fusermount:1} )
%{_bindir}/fusermount-glusterfs
%endif
%if ( 0%{_for_fedora_koji_builds} )
%if ( 0%{?rhel} && 0%{?rhel} <= 5 )
%{_sysconfdir}/sysconfig/modules/glusterfs-fuse.modules
%endif
%endif

%if 0%{?_build_server}
%pre server
pidof -c -o %PPID -x glusterfsd &>/dev/null
if [ $? -eq 0 ]; then
   echo "ERROR: Please kill gluster processes.. installation cannot proceed"
   echo "Usage: \$ pkill gluster "
   exit 1
fi

# Rename old hookscripts in an RPM-standard way.  These aren't actually
# overwritten in upgrade setup
if [ -d /var/lib/glusterd/hooks ]; then
    for file in $(find /var/lib/glusterd/hooks -type f); do
        if `echo ${file} | grep -q S56glusterd-geo-rep-create-post.sh$`; then
            continue
        fi
        newfile=`echo ${file} | sed s/S/K/1`.rpmsave
        echo "warning: ${file} saved as ${newfile}"
        mv ${file} ${newfile}
    done
fi


%files server
%defattr(-,root,root,-)
%doc extras/clear_xattrs.sh
%if ( 0%{_for_fedora_koji_builds} )
%config(noreplace) %{_sysconfdir}/logrotate.d/glusterd
%endif
%config(noreplace) %{_sysconfdir}/logrotate.d/glusterfs
#%config(noreplace) %{_sysconfdir}/logrotate.d/glusterfs-georep
%config(noreplace) %{_sysconfdir}/sysconfig/glusterd
%config(noreplace) %{_sysconfdir}/glusterfs
# Legacy configs
%if ( 0%{_for_fedora_koji_builds} )
%config(noreplace) %{_sysconfdir}/logrotate.d/glusterfsd
%config(noreplace) %{_sysconfdir}/sysconfig/glusterfsd
%endif
# init files
%_init_glusterd
%if ( 0%{_for_fedora_koji_builds} && 0%{?_with_systemd:1} )
%_init_glusterfsd
%endif
# binaries
%{_sbindir}/gluster
%{_sbindir}/glusterd
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/storage*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/posix*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/protocol/server*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mgmt*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/nfs*
%{_sharedstatedir}/glusterd
%if 0%{?_can_georeplicate}
%if ( 0%{!?_without_georeplication:1} )
%exclude %{_sharedstatedir}/glusterd/hooks/1/gsync-create/post/S56glusterd-geo-rep-create-post.sh
%endif
%endif
%{_libexecdir}/glusterfs/quota/quota-remove-xattr.sh
#%config(noreplace) %{_sharedstatedir}/glusterd/glusterd.info
#%ghost %attr(0644,-,-) %{_sharedstatedir}/glusterd/glusterd.info
#%ghost %attr(0600,-,-) %{_sharedstatedir}/glusterd/options
# This is really ugly, but I have no idea how to mark these directories in an
# other way. They should belong to the glusterfs-server package, but don't
# exist after installation. They are generated on the first start...
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/stop
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/stop/post
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/stop/pre
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/start
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/start/post
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/start/pre
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/remove-brick
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/remove-brick/post
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/remove-brick/pre
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick/post
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick/pre
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/set
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/set/post
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/set/pre
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/create
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/create/post
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/create/pre
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/delete
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/delete/post
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/delete/pre
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/copy-file
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/copy-file/post
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/copy-file/pre
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/gsync-create
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/gsync-create/post
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/gsync-create/pre
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/glustershd
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/vols
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/peers
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/groups
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/nfs
#%ghost      %attr(0600,-,-) %{_sharedstatedir}/glusterd/nfs/nfs-server.vol
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/nfs/run
#%ghost      %attr(0600,-,-) %{_sharedstatedir}/glusterd/nfs/run/nfs.pid
%endif

%pre api
pidof -c -o %PPID -x glusterfsd &>/dev/null
if [ $? -eq 0 ]; then
   echo "ERROR: Please kill gluster processes.. installation cannot proceed"
   echo "Usage: \$ pkill gluster "
   exit 1
fi

%post api
/sbin/ldconfig

%postun api
/sbin/ldconfig

%files api
%exclude %{_libdir}/*.so
%{_libdir}/libgfapi.*
%{_libdir}/glusterfs/%{version}/xlator/mount/api*


%if 0%{?_build_server}
%if ( 0%{!?_without_ocf:1} )
%pre resource-agents
pidof -c -o %PPID -x glusterfsd &>/dev/null
if [ $? -eq 0 ]; then
   echo "ERROR: Please kill gluster processes.. installation cannot proceed"
   echo "Usage: \$ pkill gluster "
   exit 1
fi

%files resource-agents
%defattr(-,root,root)
# /usr/lib is the standard for OCF, also on x86_64
%{_prefix}/lib/ocf/resource.d/glusterfs
%endif
%endif

%pre devel
pidof -c -o %PPID -x glusterfsd &>/dev/null
if [ $? -eq 0 ]; then
   echo "ERROR: Please kill gluster processes.. installation cannot proceed"
   echo "Usage: \$ pkill gluster "
   exit 1
fi

%files devel
%defattr(-,root,root,-)
%{_includedir}/glusterfs
%{_libdir}/pkgconfig/libgfchangelog.pc
%exclude %{_includedir}/glusterfs/y.tab.h
%exclude %{_includedir}/glusterfs/api
%exclude %{_libdir}/libgfapi.so
%{_libdir}/*.so

%pre api-devel
pidof -c -o %PPID -x glusterfsd &>/dev/null
if [ $? -eq 0 ]; then
   echo "ERROR: Please kill gluster processes.. installation cannot proceed"
   echo "Usage: \$ pkill gluster "
   exit 1
fi

%files api-devel
%{_libdir}/pkgconfig/glusterfs-api.pc
%{_libdir}/libgfapi.so
%{_includedir}/glusterfs/api/*

%if 0%{?_build_server}
%post server
# Legacy server
#%_init_enable glusterd
#%_init_enable glusterfsd
/sbin/chkconfig --add glusterd
/sbin/chkconfig glusterd on

# Genuine Fedora (and EPEL) builds never put gluster files in /etc; if
# there are any files in /etc from a prior gluster.org install, move them
# to /var/lib. (N.B. Starting with 3.3.0 all gluster files are in /var/lib
# in gluster.org RPMs.) Be careful to copy them on the off chance that
# /etc and /var/lib are on separate file systems
if [ -d /etc/glusterd -a ! -h /var/lib/glusterd ]; then
    %{__mkdir_p} /var/lib/glusterd
    cp -a /etc/glusterd /var/lib/glusterd
    rm -rf /etc/glusterd
    ln -sf /var/lib/glusterd /etc/glusterd
fi

# Rename old volfiles in an RPM-standard way.  These aren't actually
# considered package config files, so %config doesn't work for them.
if [ -d /var/lib/glusterd/vols ]; then
    for file in $(find /var/lib/glusterd/vols -name '*.vol'); do
        newfile=${file}.rpmsave
        echo "warning: ${file} saved as ${newfile}"
        cp ${file} ${newfile}
    done
fi

# Need to copy the file.
mkdir -p /var/lib/glusterd/groups
if [ ! -r /var/lib/glusterd/groups/virt ]; then
   cp %{_sysconfdir}/glusterfs/group-virt.example /var/lib/glusterd/groups/virt
fi
if [ ! -r /var/lib/glusterd/groups/small-file-perf ]; then
   cp %{_sysconfdir}/glusterfs/group-small-file-perf.example /var/lib/glusterd/groups/small-file-perf
fi

# add marker translator
# but first make certain that there are no old libs around to bite us
# BZ 834847
if [ -e /etc/ld.so.conf.d/glusterfs.conf ]; then
    rm -f /etc/ld.so.conf.d/glusterfs.conf
    /sbin/ldconfig
fi
pidof -c -o %PPID -x glusterd &> /dev/null
if [ $? -eq 0 ]; then
    kill -9 `pgrep -f gsyncd.py` &> /dev/null

    killall glusterd &> /dev/null
    glusterd --xlator-option *.upgrade=on -N
    glusterd
else
    glusterd --xlator-option *.upgrade=on -N
fi


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

%changelog
* Fri Nov 08 2013 Arumugam Balamurugan <barumuga@redhat.com> - 3.4.0.40rhs-2
- add aarch64 build support
* Thu Nov 07 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.40rhs-1
- fixes the bug 1016478 1019522 1025358 1025392 1027525 987292
* Tue Nov 05 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.39rhs-1
- fixes the bug 1000948 1002987 1010239 1014002 1022830 1025205 1025392
  1025408 1025476 1025604 1025953 1025954 1025956 1025967
* Fri Nov 01 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.38rhs-1
- fixes the bug 1002885 1022830 1025163 1025205 1025333 1025408 1025471
* Wed Oct 30 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.37rhs-1
- bug fixes for 1000903 1001895 1012900 1016019 1016019 1019504 1019518
  1019903 1019930 1019954 1020886 1022518 1022582 1022830 1023124 1023124
  1023124 1024496 871015 980910 980910 998793 998943
* Tue Oct 22 2013 Arumugam Balamurugan <barumuga@redhat.com> - 3.4.0.36rhs-1
- bug fixes for 1002885 1021808 1007536 1017014 1012216 998786 977544
  1016385 858434 1001895 1012900 980910 1001556
* Tue Oct 15 2013 Arumugam Balamurugan <barumuga@redhat.com> - 3.4.0.35rhs-1
- bug fixes for 969461 1000948 1000936 1011694 1013556 1016971 979641
  950314 852140 980778 1006172 1005553 1005478 1007866 998914 981035
* Mon Oct 07 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.34rhs-1
- bug fixes for 852140 950314 980778 998832 998914 998943 1000922
  1000996 1001893 1001895 1002022 1002613 1003580 1005460 1005478
  1005553 1006172 1007866 1008173 1009851 1011694 1011905
* Mon Oct 07 2013 Arumugam Balamurugan <barumuga@redhat.com> - 3.4.0.33rhs-2
- fix build issue in rhel 7.0 to include gluster rsyslog config files
  in glusterfs.rpm
* Sun Sep 08 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.33rhs-1
- fix for gfid mismatches in distribute when parallel 'mkdir()' is done
* Fri Sep 06 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.32rhs-1
- fixes to hardened build to pass execstack check in rpmdiff
- fix the compatibility issue with older servers (bz#999944)
* Thu Sep 05 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.31rhs-1
- fixes to geo-replication upgrade script to handle symlink (bz#1001089)
- fixes to glusterd to handle op-version properly to allow 'volume set' to
  happen even in older clients connected case (bz#1002871)
- fixes in geo-replication to handle hardlink migration properly (bz#1001498)
* Fri Aug 30 2013 Arumugam Balamurugan <barumuga@redhat.com> - 3.4.0.30rhs-2
- skip S56glusterd-geo-rep-create-post.sh in rename
* Fri Aug 30 2013 Arumugam Balamurugan <barumuga@redhat.com> - 3.4.0.30rhs-1
- remove rsyslog-mmcount than disabling syslog
- fixes few quota bugs
* Fri Aug 30 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.29rhs-1
- fix for smb crashes (bz#1000545 && bz#1001614)
- fix the hook script upgrade issues (bz#1002603)
* Thu Aug 29 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.28rhs-1
- fix for afr's wrong internal flag setting in case of a brick down (bz#1002069)
* Thu Aug 29 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.27rhs-1
- fix the glusterd crash (bz#990125)
- fix the hang seen in case of rebalance/self-heal with RHOS setup (bz#999528)
* Thu Aug 29 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.26rhs-1
- Build with the quota feature rework
* Thu Aug 29 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.25rhs-1
- fixes a issue with peer probe of newer servers after upgrade (bz#1000986)
- fixes NFS file handle sizes issue with older clients (bz#902857)
- geo-replication's session distribution is now more deterministic (bz#980049)
* Mon Aug 27 2013 Arumugam Balamurugan <barumuga@redhat.com> - 3.4.0.24rhs-1
- resolves rhbz#1000957 rhbz#999939 rhbz#994351 rhbz#988900 rhbz#999825 rhbz#1000396
* Mon Aug 26 2013 Arumugam Balamurugan <barumuga@redhat.com> - 3.4.0.23rhs-1
- resolves rhbz#982471, rhbz#902857, rhbz#993891, rhbz#999921, rhbz#999921
* Fri Aug 23 2013 Arumugam Balamurugan <barumuga@redhat.com> - 3.4.0.22rhs-2
- disable syslog temporarily till rsyslog is included in rhs channel
* Thu Aug 22 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.22rhs-1
- updated glusterfs.spec from the source repository.
- fixes the bugs: 893960 984921 987082 990125 991021 996083 996987 996999 998416
* Tue Aug 20 2013 Balamurugan Arumugam <barumuga@redhat.com> - 3.4.0.21rhs-1
- resolves rhbz#928784
* Wed Aug 14 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.20rhs-2
- fixed the path of 'chmod' in geo-replication 'post' section
* Wed Aug 14 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.20rhs-1
- fixed an issue with geo-rep create (bz996961)
- fixed an build issue in RHEL5 (in the source)
* Wed Aug 14 2013 Arumugam Balamurugan <barumuga@redhat.com> - 3.4.0.19rhs-2
- fixed 'Installed (but unpackaged) file(s) found' for non-server builds
* Mon Aug  13 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.19rhs-1
- resolves bugs (921385 923555 960046 980529 983507 989906 990125 994956 996312 996431)
* Mon Aug  7 2013 Arumugam Balamurugan <barumuga@redhat.com> - 3.4.0.18rhs-1
- resolves rhbz#988852, rhbz#989192, rhbz#989435, rhbz#990084, rhbz#992959, rhbz#993583, rhbz#993713
* Mon Aug  6 2013 Vijay Bellur <vbellur@redhat.com> - 3.4.0.17rhs-1
- Enables orthogonal-meta-data option in afr by default.
* Mon Aug  6 2013 Arumugam Balamurugan <barumuga@redhat.com> - 3.4.0.16rhs-1
- resolves rhbz#993270
* Mon Aug  6 2013 Arumugam Balamurugan <barumuga@redhat.com> - 3.4.0.15rhs-6
- remove /usr/lib/ocf/resource.d/glusterfs for client builds
* Mon Aug  6 2013 Arumugam Balamurugan <barumuga@redhat.com> - 3.4.0.15rhs-5
- set correct dependencies between glusterfs subpackages
* Mon Aug  5 2013 Arumugam Balamurugan <barumuga@redhat.com> - 3.4.0.15rhs-4
- remove /usr/bin/fusermount dependency for fuse
* Mon Aug  5 2013 Arumugam Balamurugan <barumuga@redhat.com> - 3.4.0.15rhs-3
- make geo-replication as dependency to server
* Mon Aug  5 2013 Arumugam Balamurugan <barumuga@redhat.com> - 3.4.0.15rhs-2
- rpm restructuring done
* Mon Aug 05 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.15rhs_1
- fixes for bugs (858492 924572 957685 958199 960938 968879 969372
  975343 980529 981158 981318 981612 983950 985236 988852 988914
  989248 989465 989906 990060 990368 990510 990548 990562 990958 990961)
* Tue Jul 30 2013 Arumugam Balamurugan <barumuga@redhat.com> - 3.4.0.14rhs-1
- resolves rhbz#989689
* Sun Jul 28 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.13rhs
- rebase of the branch back to 'rhs-2.1'
- 'gluster volume set <VOL> group small-file-perf' is added
- fixes an issue with init.d/glusterd output not right (bz958708)
* Wed Jul 24 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.12rhs.beta6
- fixes to few bugs in quota (multivolume support, etc)
- geo-rep xsync missing few files, now fixed
- patches for bzs: (850514 852294 928784 956494 975754 981553 981661 982184
  983040 984414 984942 985380 985384 985388 985752 986158 986162 986885
  986929 987126 987432)

* Thu Jul 18 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.12rhs.beta5_2
- fix a build warning, which caused failure of glusterd processes starting.
* Thu Jul 18 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.12rhs.beta5
- fixes for bugs 852578 956494 970686 974913 976292 976755 982181 983476
  983544 983966 984447.
* Fri Jul 12 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.12rhs.beta4
- more fixes to geo-rep and quota
- other bug fixes include (918510 920870 924048 952420 956494 956619 
  962621 980723 980725 981653 981949 982078 982479)
* Sat Jul 06 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.12rhs.beta3
- brick process crashes in debug mode during volume set/quota limit set
- fix issues with geo-replication syncing if data existed already.
- geo-replication entry creation when done in parallel
* Thu Jul 04 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.12rhs.beta2
- couple of minor fixes in geo-rep
- fixed the quota reconfigure issue (now restarts quotad to make
  sure the list is properly processed
- other bug fixes in base (bz919209 bz961608 bz969461 bz974055 bz974393
  bz974475 bz975343 bz980117 bz980348 bz980468 bz980518 bz980722 bz980798)
* Fri Jun 28 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.12rhs.beta1
- added one of the geo-replication hook file in install path
- fixed code in changelog to pass the rhel5 build
* Thu Jun 27 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.12rhs.beta0
- added distributed-geo-rep feature
- added server side quota feature
* Mon Jun 24 2013 Arumugam Balamurugan <barumuga@redhat.com> - 3.4.0.12rhs
- fixes rhbz#924572 rhbz#955948 rhbz#956034 rhbz#962286 rhbz#972653
- rhbz#975343
* Tue Jun 18 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.11rhs
- gfapi patches for support vfs_glusterfs for samba are merged
* Tue Jun 18 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.10rhs
- fixes to bugs 959208 959869 961250 962510 964020 964054 968289 974913
* Fri Jun 05 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.9rhs
- fix lockfile issue with init.d file
- clients not having /var/run/gluster directory for statedump (bz917544)
- other bugs from source tarball (bz923466 bz924572 bz956188 bz958076 bz959201 bz959907 bz960390 bz960834 bz960835 bz961271 bz962345 bz962400 bz963122 bz963534 bz963896 bz964020 bz965440 bz967483)
* Tue May 14 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.8rhs
- fix glusterd.info file re-writing issue (bz962343 & bz961703)
- fix port reconnect issues at socket layer (bz960586)
- add glusterd in chkconfig
* Mon May 13 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.7rhs
- fix a memory corruption issue with RPC layer (bz961198)
- fix in distribute migration check code (bz960843)
* Thu May 10 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.6rhs
- fix a missing hooks issue (bz960982)
* Thu May 09 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.5rhs
- fix issue with server package installation
- root-squash fixes
- reverted few replicate patches
* Tue May 07 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.4rhs
- fixed hook scripts
- nfs crash fix
- couple glusterd crashes fixed (syncop lock related fixes)
- dht rebalance crash fix
- quorum restart logic fixes
* Fri May 03 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.3rhs
- fixed issues 'virt' group file, and multiple option handling
- fixed couple of crashes with glusterd
* Thu May 02 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.2rhs
- rebase to upstream/master branch
  (commit: b6e10801bee030fe7fcd1ec3bfac947ce44d023d)
- added 'virt' group file.
* Tue Apr 09 2013 Amar Tumballi <atumball@redhat.com> - 3.4.0.1rhs
- rebase to upstream/release-3.4 branch
* Mon Feb 18 2013 Raghavendra Bhat <rabhat@redhat.com> - 3.4.0qa8
- quick-read refactor
- integrate trace and event-history
- performance/md-cache: make readdirp configurable
- io-stats: handle open failures gracefully
- object-storage: use temp file optimization
* Thu Jan 17 2013 Vijay Bellur <vbellur@redhat.com> - 3.4.0.qa6
- Added packaging for resource-agents
* Fri Jan 11 2013 Vijay Bellur <vbellur@redhat.com> - 3.4.0.qa6
- Upstream rebase #4 for 2.1
* Mon Dec 17 2012 Vijay Bellur <vbellur@redhat.com> - 3.4.0.qa5
- Upstream rebase #3 for 2.1
* Wed Dec 05 2012 Vijay Bellur <vbellur@redhat.com> - 3.4.0.qa4
- Upstream rebase #2 for 2.1
* Thu Nov 01 2012 Vijay Bellur <vbellur@redhat.com> - 3.4.0.1rhs
- 2.1 rebase
* Wed Oct 10 2012 Amar Tumballi <atumball@redhat.com> - 3.3.0.3rhs-33
- valid hostname fix (bz863908)
- smb.conf init script issues (bz863907)
- geo-replication: rsync number of argument (bz859173)
* Mon Oct 01 2012 Amar Tumballi <atumball@redhat.com> - 3.3.0.3rhs-32
- bug fixes in quorum support
* Fri Sep 28 2012 Amar Tumballi <atumball@redhat.com> - 3.3.0.3rhs-31
- server side quorum support added
* Tue Sep 11 2012 Amar Tumballi <atumball@redhat.com> - 3.3.0.2rhs-29
- changing the upstream tarball version (no code difference from -28)
* Mon Sep 10 2012 Amar Tumballi <atumball@redhat.com> - 3.3.0-28
- glusterd: Fix a crash when volume status is issued
* Fri Sep 07 2012 Vijay Bellur <vbellur@redhat.com> - 3.3.0-27
- Improvements in GlusterFS statedump infrastructure
- glusterd, glusterfsd: Fix a crash when rpc submission fails
* Fri Aug 17 2012 Vijay Bellur <vbellur@redhat.com> - 3.3.0-26
- Updated to gluster 3.3.0-26 build
* Wed Jul 25 2012 Vijay Bellur <vbellur@redhat.com> - 3.3.0-25
- Updated to gluster 3.3.0-25 build
* Tue Jul 24 2012 Vijay Bellur <vbellur@redhat.com> - 3.3.0-24
- Updated to gluster 3.3.0-24 build
* Thu Jul 19 2012 Vijay Bellur <vbellur@redhat.com> - 3.3.0-23
- Updated to gluster 3.3.0-23 build
* Tue Jun 19 2012 Vijay Bellur <vbellur@redhat.com> - 3.3.0-22
- Updated to gluster 3.3.0-22 build
* Fri Jun 15 2012 Anthony Towns <atowns@redhat.com> - 3.3.0-21
- Allow building only native client packages.
* Thu Jun 14 2012 Vijay Bellur <vbellur@redhat.com> - 3.3.0-20
- Updated to gluster 3.3.0 build
* Wed May 30 2012 Vijay Bellur <vbellur@redhat.com> - 3.3.0qa45-1
- Updated to gluster 3.3 qa45 build
* Tue May 29 2012 Vijay Bellur <vbellur@redhat.com> - 3.3.0qa44-1
- Updated to gluster 3.3 qa44 build
* Wed May 23 2012 Vijay Bellur <vbellur@redhat.com> - 3.3.0qa43-1
- Updated to gluster 3.3 qa43 build
* Wed May 16 2012 Vijay Bellur <vbellur@redhat.com> - 3.3.0qa41-1
- Updated to gluster 3.3 qa41 build
* Tue May 08 2012 Anthony Towns <atowns@redhat.com> - 3.3.0qa40-1
- Updated to gluster 3.3 qa40 build
