# if you make changes, the it is advised to increment this number, and provide
# a descriptive suffix to identify who owns or what the change represents
# e.g. release_version 2.MSW
%global release 1%{?dist}
%global _sharedstatedir /var/lib

%global version 3.4.0.59rhs


# if you wish to build the server rpms, compile like this...
# rpmbuild -ta glusterfs-VERSION.tar.gz --with server
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
# rpmbuild -ta glusterfs-VERSION.tar.gz --without rdma
%{?_without_rdma:%global _without_rdma --disable-ibverbs}

# No RDMA Support on s390(x)
%ifarch s390 s390x
%global _without_rdma --disable-ibverbs
%endif

# if you wish to compile an rpm without epoll...
# rpmbuild -ta glusterfs-VERSION.tar.gz --without epoll
%{?_without_epoll:%global _without_epoll --disable-epoll}

# if you wish to compile an rpm without fusermount...
# rpmbuild -ta glusterfs-VERSION.tar.gz --without fusermount
%{?_without_fusermount:%global _without_fusermount --disable-fusermount}

%global _can_georeplicate 1

# if you wish to compile an rpm without geo-replication support, compile like this...
# rpmbuild -ta glusterfs-VERSION.tar.gz --without georeplication
%{?_without_georeplication:%global _without_georeplication --disable-geo-replication}

# if you wish to compile an rpm without the OCF resource agents...
# rpmbuild -ta glusterfs-VERSION.tar.gz --without ocf
%{?_without_ocf:%global _without_ocf --without-ocf}

# disable ocf as it is not required for rhs
%global _without_ocf --without-ocf

# if you wish to compile an rpm without the BD map support...
# rpmbuild -ta glusterfs-VERSION.tar.gz --without bd
%{?_without_bd:%global _without_bd --disable-bd-xlator}

%if ( 0%{?rhel} && 0%{?rhel} < 6 )
%define _without_bd true
%endif

# if you wish to build rpms without syslog logging, compile like this
# rpmbuild -ta glusterfs-VERSION.tar.gz --without syslog
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

# From https://fedoraproject.org/wiki/Packaging:Python#Macros
%if ( 0%{?rhel} && 0%{?rhel} <= 5 )
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
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
# we provide the Python package/namespace 'gluster'
Provides:         python-gluster = %{version}-%{release}

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
%if ( 0%{?rhel} && 0%{?rhel} >= 5 )
%{__mkdir_p} %{buildroot}%{python_sitelib}/gluster
touch %{buildroot}%{python_sitelib}/gluster/__init__.py
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
%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/glustershd
%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/nfs
%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/peers
%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/quotad
%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/vols
%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/groups

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
# geo replication logrotate file.
%{__install} -D -p -m 0644 extras/glusterfs-georep-logrotate \
    %{buildroot}%{_sysconfdir}/logrotate.d/glusterfs-georep
%endif

%if ( 0%{!?_without_georeplication:1} )
# geo-rep ghosts
%{__mkdir_p} %{buildroot}%{_sharedstatedir}/glusterd/geo-replication
touch %{buildroot}%{_sharedstatedir}/glusterd/geo-replication/gsyncd_template.conf
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

%{__install} -p -m 0644 extras/group-virt.example \
    %{buildroot}%{_sharedstatedir}/glusterd/groups/virt
%{__install} -p -m 0644 extras/group-small-file-perf.example \
    %{buildroot}%{_sharedstatedir}/glusterd/groups/small-file-perf
%endif

%if !0%{?_build_server}
echo "Removing files that are only used in the server subpackages."
rm %{buildroot}%{_sysconfdir}/glusterfs/glusterd.vol
rm %{buildroot}%{_sysconfdir}/init.d/glusterd
rm %{buildroot}%{_sbindir}/gluster
rm %{buildroot}%{_sbindir}/glusterd
rm %{buildroot}%{_sbindir}/glfsheal
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
    %{buildroot}%{_sysconfdir}/rsyslog.d/gluster.conf.example
%endif

%if ( 0%{?rhel} && 0%{?rhel} == 6 )
%{__install} -D -p -m 0644 extras/gluster-rsyslog-5.8.conf \
    %{buildroot}%{_sysconfdir}/rsyslog.d/gluster.conf.example
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
%endif

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

%if 0%{?_build_server}
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
%endif

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
%{_sysconfdir}/rsyslog.d/gluster.conf.example
%endif
%endif
%exclude %{_libdir}/libgfapi.*


%if ( 0%{!?_without_rdma:1} )
%if 0%{?_build_server}
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

%files rdma
%defattr(-,root,root,-)
%{_libdir}/glusterfs/%{version}%{?prereltag}/rpc-transport/rdma*
%endif

%if 0%{?_build_server}
%if 0%{?_can_georeplicate}
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
%dir %{_sharedstatedir}/glusterd/hooks
%dir %{_sharedstatedir}/glusterd/hooks/1
%dir %{_sharedstatedir}/glusterd/hooks/1/gsync-create
%dir %{_sharedstatedir}/glusterd/hooks/1/gsync-create/post
%{_sharedstatedir}/glusterd/hooks/1/gsync-create/post/S56glusterd-geo-rep-create-post.sh
%{_datadir}/glusterfs/scripts/get-gfid.sh
%{_datadir}/glusterfs/scripts/slave-upgrade.sh
%{_datadir}/glusterfs/scripts/gsync-upgrade.sh
%{_datadir}/glusterfs/scripts/generate-gfid-file.sh
%{_datadir}/glusterfs/scripts/gsync-sync-gfid
%{_sharedstatedir}/glusterd/geo-replication
%config(noreplace) %{_sharedstatedir}/glusterd/geo-replication/gsyncd_template.conf
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/gsync-create/post
#%ghost %attr(0644,-,-) %{_sharedstatedir}/glusterd/hooks/1/gsync-create/post/S56glusterd-geo-rep-create-post.sh
#%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/geo-replication
#%ghost %attr(0644,-,-) %{_sharedstatedir}/glusterd/geo-replication/gsyncd_template.conf
%endif
# need to copy the upgrade scripts here
%endif
%endif

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
%endif

%if 0%{?_build_server}
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

%pre server
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
%{_sbindir}/glfsheal
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/storage*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/posix*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/protocol/server*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mgmt*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/nfs*
%{_sharedstatedir}/glusterd
%dir %{_sharedstatedir}/glusterd/groups
%config(noreplace) %{_sharedstatedir}/glusterd/groups/virt
%config(noreplace) %{_sharedstatedir}/glusterd/groups/small-file-perf
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

%if 0%{?_build_server}
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
%endif

%post api
/sbin/ldconfig

%postun api
/sbin/ldconfig

%files api
%exclude %{_libdir}/*.so
%{_libdir}/libgfapi.*
%{_libdir}/glusterfs/%{version}/xlator/mount/api*
%{python_sitelib}/*


%if 0%{?_build_server}
%if ( 0%{!?_without_ocf:1} )
%files resource-agents
%defattr(-,root,root)
# /usr/lib is the standard for OCF, also on x86_64
%{_prefix}/lib/ocf/resource.d/glusterfs

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
%endif

%files devel
%defattr(-,root,root,-)
%{_includedir}/glusterfs
%{_libdir}/pkgconfig/libgfchangelog.pc
%exclude %{_includedir}/glusterfs/y.tab.h
%exclude %{_includedir}/glusterfs/api
%exclude %{_libdir}/libgfapi.so
%{_libdir}/*.so

%if 0%{?_build_server}
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
%endif

%files api-devel
%{_libdir}/pkgconfig/glusterfs-api.pc
%{_libdir}/libgfapi.so
%{_includedir}/glusterfs/api/*

%if 0%{?_build_server}
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
%endif

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
* Mon Feb  3 2014 Arumugam Balamurugan <barumuga@redhat.com>
- enable %pretrans only for server builds (bz#1056204)

* Mon Jan 27 2014 Niels de Vos <ndevos@redhat.com>
- Re-add Lua scripts for all sub-packages (bz#1056204)

* Wed Jan 22 2014 Niels de Vos <ndevos@redhat.com>
- make the pretrans Lua scripts RHEL-5 compatible (bz#1056204)

* Thu Jan 16 2014 Arumugam Balamurugan <barumuga@redhat.com>
- /var/lib/glusterd/groups/{virt,small-file-perf} are tracked by rpm
  now (bz#829734)

* Fri Jan 03 2014 Arumugam Balamurugan <barumuga@redhat.com>
- fix build error for rhel5 about missing
  /usr/lib/python2.4/site-packages/*

* Thu Dec 26 2013 Balamurugan Arumugam <barumuga@redhat.com>
- provide the Python package/namespace 'gluster' (bz#1046571)

* Tue Dec 24 2013 Niels de Vos <ndevos@redhat.com>
- migrate %pretrans scripts to Lua (bz#1016385)

* Tue Dec 18 2013 Pranith Kumar Karampuri <pkarampu@redhat.com>
- Add glfsheal to rpm

* Tue Dec 17 2013 Harshavardhana <fharshav@redhat.com>
- Rename `%pretrans` to `%pre` - since `%pretrans` during kickstart doesn't
  check for dependencies (bash code would fail with exit status 127)

* Tue Dec 17 2013 Balamurugan Arumugam <barumuga@redhat.com>
- clean up left overs after uninstalling glusterfs RPMs (bz#829734)

* Sun Dec 08 2013 Harshavardhana <fharshav@redhat.com>
- `%pretrans` checks carry more detailed vol type based verification leading to
  more user friendly messaging (bz#1016385)

* Fri Oct 25 2013 Balamurugan Arumugam <barumuga@redhat.com>
- sync the spec file with dist-git

* Fri Oct 11 2013 Harshavardhana <fharshav@redhat.com>
- Change messaging for `%pre` checks from 'volume stop' to 'pkill gluster' (bz#1016385)

* Tue Aug 27 2013 Amar Tumballi  <atumball@redhat.com>
- remove the 'patch' files handling part from 'fedora_koji' section (bz#1000396)

* Mon Aug 26 2013 Amar Tumballi  <atumball@redhat.com>
- stop the geo-replication's log-rotate file from installing.

* Wed Aug 21 2013 Harshavardhana  <fharshav@redhat.com> 
- Avoid doing rolling upgrades - volume should be stopped before upgrade (RHBZ#902857)
 
* Tue Jul 30 2013 Kaleb S. KEITHLEY <kkeithle@redhat.com>
- Sync with Fedora glusterfs.spec, add glusterfs-libs RPM for oVirt/qemu-kvm

* Fri Jul 10 2013 Csaba Henk <csaba@redhat.com>
- Replaced secret_pub_ops.sh of %{_libexecdir}/glusterfs with peer_add_secret_pub and peer_gsec_create

* Tue Jul 10 2013 Avra Sengupta <asengupt@redhat.com>
- Added secret_pub_ops.sh to %{_libexecdir}/glusterfs directory.

* Wed Jul 10 2013 Aravinda VK <avishwan@redhat.com>
- Added gverify.sh to %{_libexecdir}/glusterfs directory.

* Thu Jun 27 2013 Kaleb S. KEITHLEY <kkeithle@redhat.com>
- fix the hardening fix for shlibs, use %%{__sed} macro, shorter ChangeLog

* Wed Jun 26 2013 Niels de Vos <ndevos@redhat.com>
- move the mount/api xlator to glusterfs-api

* Fri Jun 7 2013 Kaleb S. KEITHLEY <kkeithle@redhat.com>
- Sync with Fedora glusterfs.spec, remove G4S/UFO and Swift

* Mon Mar 4 2013 Niels de Vos <ndevos@redhat.com>
- Package /var/run/gluster so that statedumps can be created

* Wed Feb 6 2013 Kaleb S. KEITHLEY <kkeithle@redhat.com>
- Sync with Fedora glusterfs.spec

* Tue Dec 11 2012 Filip Pytloun <filip.pytloun@gooddata.com>
- add sysconfig file

* Thu Oct 25 2012 Niels de Vos <ndevos@redhat.com>
- Add a sub-package for the OCF resource agents

* Wed Sep 05 2012 Niels de Vos <ndevos@redhat.com>
- Don't use python-ctypes on SLES (from Jörg Petersen)

* Tue Jul 10 2012 Niels de Vos <ndevos@redhat.com>
- Include extras/clear_xattrs.sh in the glusterfs-server sub-package

* Thu Jun 07 2012 Niels de Vos <ndevos@redhat.com>
- Mark /var/lib/glusterd as owned by glusterfs, subdirs belong to -server

* Wed May 9 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- Add BuildRequires: libxml2-devel so that configure will DTRT on for
- Fedora's Koji build system

* Wed Nov 9 2011 Joe Julian <me@joejulian.name> - git master
- Merge fedora specfile into gluster's spec.in.
- Add conditionals to allow the same spec file to be used for both 3.1 and 3.2
- http://bugs.gluster.com/show_bug.cgi?id=2970

* Wed Oct  5 2011 Joe Julian <me@joejulian.name> - 3.2.4-1
- Update to 3.2.4
- Removed the $local_fs requirement from the init scripts as in RHEL/CentOS that's provided
- by netfs, which needs to be started after glusterd.

* Sun Sep 25 2011 Joe Julian <me@joejulian.name> - 3.2.3-2
- Merged in upstream changes
- Fixed version reporting 3.2git
- Added nfs init script (disabled by default)

* Fri Sep  1 2011 Joe Julian <me@joejulian.name> - 3.2.3-1
- Update to 3.2.3

* Tue Jul 19 2011 Joe Julian <me@joejulian.name> - 3.2.2-3
- Add readline and libtermcap dependencies

* Tue Jul 19 2011 Joe Julian <me@joejulian.name> - 3.2.2-2
- Critical patch to prevent glusterd from walking outside of its own volume during rebalance

* Thu Jul 14 2011 Joe Julian <me@joejulian.name> - 3.2.2-1
- Update to 3.2.2

* Wed Jul 13 2011 Joe Julian <me@joejulian.name> - 3.2.1-2
- fix hardcoded path to gsyncd in source to match the actual file location

* Mon Jun 21 2011 Joe Julian <me@joejulian.name> - 3.2.1
- Update to 3.2.1

* Mon Jun 20 2011 Joe Julian <me@joejulian.name> - 3.1.5
- Update to 3.1.5

* Mon May 31 2011 Joe Julian <me@joejulian.name> - 3.1.5-qa1.4
- Current git

* Sun May 29 2011 Joe Julian <me@joejulian.name> - 3.1.5-qa1.2
- set _sharedstatedir to /var/lib for FHS compliance in RHEL5/CentOS5
- mv /etc/glusterd, if it exists, to the new state dir for upgrading from gluster packaging

* Sat May 28 2011 Joe Julian <me@joejulian.name> - 3.1.5-qa1.1
- Update to 3.1.5-qa1
- Add patch to remove optimization disabling
- Add patch to remove forced 64 bit compile
- Obsolete glusterfs-core to allow for upgrading from gluster packaging

* Sun Mar 19 2011 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.1.3-1
- Update to 3.1.3
- Merge in more upstream SPEC changes
- Remove patches from GlusterFS bugzilla #2309 and #2311
- Remove inode-gen.patch

* Sun Feb 06 2011 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.1.2-3
- Add back in legacy SPEC elements to support older branches

* Tue Feb 03 2011 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.1.2-2
- Add patches from CloudFS project

* Tue Jan 25 2011 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.1.2-1
- Update to 3.1.2

* Wed Jan 5 2011 Dan Horák <dan[at]danny.cz> - 3.1.1-3
- no InfiniBand on s390(x)

* Sat Jan 1 2011 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.1.1-2
- Update to support readline
- Update to not parallel build

* Mon Dec 27 2010 Silas Sewell <silas@sewell.ch> - 3.1.1-1
- Update to 3.1.1
- Change package names to mirror upstream

* Mon Dec 20 2010 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.0.7-1
- Update to 3.0.7

* Wed Jul 28 2010 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.0.5-1
- Update to 3.0.x

* Sat Apr 10 2010 Jonathan Steffan <jsteffan@fedoraproject.org> - 2.0.9-2
- Move python version requires into a proper BuildRequires otherwise
  the spec always turned off python bindings as python is not part
  of buildsys-build and the chroot will never have python unless we
  require it
- Temporarily set -D_FORTIFY_SOURCE=1 until upstream fixes code
  GlusterFS Bugzilla #197 (#555728)
- Move glusterfs-volgen to devel subpackage (#555724)
- Update description (#554947)

* Sat Jan 2 2010 Jonathan Steffan <jsteffan@fedoraproject.org> - 2.0.9-1
- Update to 2.0.9

* Sat Nov 8 2009 Jonathan Steffan <jsteffan@fedoraproject.org> - 2.0.8-1
- Update to 2.0.8
- Remove install of glusterfs-volgen, it's properly added to
  automake upstream now

* Sat Oct 31 2009 Jonathan Steffan <jsteffan@fedoraproject.org> - 2.0.7-1
- Update to 2.0.7
- Install glusterfs-volgen, until it's properly added to automake
  by upstream
- Add macro to be able to ship more docs

* Thu Sep 17 2009 Peter Lemenkov <lemenkov@gmail.com> 2.0.6-2
- Rebuilt with new fuse

* Sat Sep 12 2009 Matthias Saou <http://freshrpms.net/> 2.0.6-1
- Update to 2.0.6.
- No longer default to disable the client on RHEL5 (#522192).
- Update spec file URLs.

* Mon Jul 27 2009 Matthias Saou <http://freshrpms.net/> 2.0.4-1
- Update to 2.0.4.

* Thu Jun 11 2009 Matthias Saou <http://freshrpms.net/> 2.0.1-2
- Remove libglusterfs/src/y.tab.c to fix koji F11/devel builds.

* Sat May 16 2009 Matthias Saou <http://freshrpms.net/> 2.0.1-1
- Update to 2.0.1.

* Thu May  7 2009 Matthias Saou <http://freshrpms.net/> 2.0.0-1
- Update to 2.0.0 final.

* Wed Apr 29 2009 Matthias Saou <http://freshrpms.net/> 2.0.0-0.3.rc8
- Move glusterfsd to common, since the client has a symlink to it.

* Fri Apr 24 2009 Matthias Saou <http://freshrpms.net/> 2.0.0-0.2.rc8
- Update to 2.0.0rc8.

* Sun Apr 12 2009 Matthias Saou <http://freshrpms.net/> 2.0.0-0.2.rc7
- Update glusterfsd init script to the new style init.
- Update files to match the new default vol file names.
- Include logrotate for glusterfsd, use a pid file by default.
- Include logrotate for glusterfs, using killall for lack of anything better.

* Sat Apr 11 2009 Matthias Saou <http://freshrpms.net/> 2.0.0-0.1.rc7
- Update to 2.0.0rc7.
- Rename "libs" to "common" and move the binary, man page and log dir there.

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 16 2009 Matthias Saou <http://freshrpms.net/> 2.0.0-0.1.rc1
- Update to 2.0.0rc1.
- Include new libglusterfsclient.h.

* Mon Feb 16 2009 Matthias Saou <http://freshrpms.net/> 1.3.12-1
- Update to 1.3.12.
- Remove no longer needed ocreat patch.

* Thu Jul 17 2008 Matthias Saou <http://freshrpms.net/> 1.3.10-1
- Update to 1.3.10.
- Remove mount patch, it's been included upstream now.

* Fri May 16 2008 Matthias Saou <http://freshrpms.net/> 1.3.9-1
- Update to 1.3.9.

* Fri May  9 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-1
- Update to 1.3.8 final.

* Tue Apr 23 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.10
- Include short patch to include fixes from latest TLA 751.

* Mon Apr 22 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.9
- Update to 1.3.8pre6.
- Include glusterfs binary in both the client and server packages, now that
  glusterfsd is a symlink to it instead of a separate binary.
* Sun Feb  3 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.8
- Add python version check and disable bindings for version < 2.4.

* Sun Feb  3 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.7
- Add --without client rpmbuild option, make it the default for RHEL (no fuse).
  (I hope "rhel" is the proper default macro name, couldn't find it...)

* Wed Jan 30 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.6
- Add --without ibverbs rpmbuild option to the package.

* Mon Jan 14 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.5
- Update to current TLA again, patch-636 which fixes the known segfaults.

* Thu Jan 10 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.4
- Downgrade to glusterfs--mainline--2.5--patch-628 which is more stable.

* Tue Jan  8 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.3
- Update to current TLA snapshot.
- Include umount.glusterfs wrapper script (really needed? dunno).
- Include patch to mount wrapper to avoid multiple identical mounts.

* Sun Dec 30 2007 Matthias Saou <http://freshrpms.net/> 1.3.8-0.1
- Update to current TLA snapshot, which includes "volume-name=" fstab option.

* Mon Dec  3 2007 Matthias Saou <http://freshrpms.net/> 1.3.7-6
- Re-add the /var/log/glusterfs directory in the client sub-package (required).
- Include custom patch to support vol= in fstab for -n glusterfs client option.

* Mon Nov 26 2007 Matthias Saou <http://freshrpms.net/> 1.3.7-4
- Re-enable libibverbs.
- Check and update License field to GPLv3+.
- Add glusterfs-common obsoletes, to provide upgrade path from old packages.
- Include patch to add mode to O_CREATE opens.

* Thu Nov 22 2007 Matthias Saou <http://freshrpms.net/> 1.3.7-3
- Remove Makefile* files from examples.
- Include RHEL/Fedora type init script, since the included ones don't do.

* Wed Nov 21 2007 Matthias Saou <http://freshrpms.net/> 1.3.7-1
- Major spec file cleanup.
- Add missing %%clean section.
- Fix ldconfig calls (weren't set for the proper sub-package).

* Sat Aug 4 2007 Matt Paine <matt@mattsoftware.com> - 1.3.pre7
- Added support to build rpm without ibverbs support (use --without ibverbs
  switch)

* Sun Jul 15 2007 Matt Paine <matt@mattsoftware.com> - 1.3.pre6
- Initial spec file
