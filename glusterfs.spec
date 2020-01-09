%global _hardened_build 1

%global _for_fedora_koji_builds 0

# uncomment and add '%' to use the prereltag for pre-releases
# %%global prereltag qa3

##-----------------------------------------------------------------------------
## All argument definitions should be placed here and keep them sorted
##

# if you wish to compile an rpm without rdma support, compile like this...
# rpmbuild -ta glusterfs-3.6.0.54.tar.gz --without rdma
%{?_without_rdma:%global _without_rdma --disable-ibverbs}

# No RDMA Support on s390(x)
%ifarch s390 s390x
%global _without_rdma --disable-ibverbs
%endif

# if you wish to compile an rpm without epoll...
# rpmbuild -ta glusterfs-3.6.0.54.tar.gz --without epoll
%{?_without_epoll:%global _without_epoll --disable-epoll}

# if you wish to compile an rpm without fusermount...
# rpmbuild -ta glusterfs-3.6.0.54.tar.gz --without fusermount
%{?_without_fusermount:%global _without_fusermount --disable-fusermount}

# if you wish to compile an rpm without geo-replication support, compile like this...
# rpmbuild -ta glusterfs-3.6.0.54.tar.gz --without georeplication
%{?_without_georeplication:%global _without_georeplication --disable-georeplication}

# Disable geo-replication on EL5, as its default Python is too old
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
%global _without_georeplication --disable-georeplication
%endif

# if you wish to compile an rpm without the OCF resource agents...
# rpmbuild -ta glusterfs-3.6.0.54.tar.gz --without ocf
%{?_without_ocf:%global _without_ocf --without-ocf}

# if you wish to build rpms without syslog logging, compile like this
# rpmbuild -ta glusterfs-3.6.0.54.tar.gz --without syslog
%{?_without_syslog:%global _without_syslog --disable-syslog}

# disable syslog forcefully as rhel <= 6 doesn't have rsyslog or rsyslog-mmcount
%if ( 0%{?rhel} && 0%{?rhel} <= 6 )
%global _without_syslog --disable-syslog
%endif

# if you wish to compile an rpm without the BD map support...
# rpmbuild -ta glusterfs-3.6.0.54.tar.gz --without bd
%{?_without_bd:%global _without_bd --disable-bd-xlator}

%if ( 0%{?rhel} && 0%{?rhel} < 6 || 0%{?sles_version} )
%define _without_bd --disable-bd-xlator
%endif

# if you wish to compile an rpm without the qemu-block support...
# rpmbuild -ta glusterfs-3.6.0.54.tar.gz --without qemu-block
%{?_without_qemu_block:%global _without_qemu_block --disable-qemu-block}

%if ( 0%{?rhel} && 0%{?rhel} < 6 )
# xlators/features/qemu-block fails to build on RHEL5, disable it
%define _without_qemu_block --disable-qemu-block
%endif

# if you wish not to build server rpms, compile like this.
# rpmbuild -ta glusterfs-3.6.0.54.tar.gz --without server

%global _build_server 1
%if "%{?_without_server}"
%global _build_server 0
%endif

%if ( "%{?dist}" == ".el6rhs" ) || ( "%{?dist}" == ".el7rhs" )
%global _build_server 1
%else
%global _build_server 0
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
%define _init_stop()    /bin/systemctl stop %1.service ;
%define _init_install() install -D -p -m 0644 %1 %{buildroot}%{_unitdir}/%2.service ;
# can't seem to make a generic macro that works
%define _init_glusterd   %{_unitdir}/glusterd.service
%define _init_glusterfsd %{_unitdir}/glusterfsd.service
%else
%define _init_enable()  /sbin/chkconfig --add %1 ;
%define _init_disable() /sbin/chkconfig --del %1 ;
%define _init_restart() /sbin/service %1 condrestart &>/dev/null ;
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
Summary:          Cluster File System
%if ( 0%{_for_fedora_koji_builds} )
Name:             glusterfs
Version:          3.5.0
Release:          0.1%{?prereltag:.%{prereltag}}%{?dist}
Vendor:           Fedora Project
%else
Name:             glusterfs
Version:          3.6.0.54
Release:          1%{?dist}
ExclusiveArch:    x86_64 aarch64
%endif
License:          GPLv2 or LGPLv3+
Group:            System Environment/Base
URL:              http://www.gluster.org/docs/index.php/GlusterFS
%if ( 0%{_for_fedora_koji_builds} )
Source0:          http://bits.gluster.org/pub/gluster/glusterfs/src/glusterfs-%{version}%{?prereltag}.tar.gz
Source1:          glusterd.sysconfig
Source2:          glusterfsd.sysconfig
Source3:          glusterfs-fuse.logrotate
Source4:          glusterd.logrotate
Source5:          glusterfsd.logrotate
Source6:          rhel5-load-fuse-modules
Source7:          glusterfsd.service
Source8:          glusterfsd.init
%else
Source0:          glusterfs-3.6.0.54.tar.gz
Source9:	enable-server-packages.patch
Source10:	glusterfs.ini
%endif

BuildRoot:        %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

%if ( 0%{?rhel} && 0%{?rhel} <= 5 )
BuildRequires:    python-simplejson
%endif
%if ( 0%{?_with_systemd:1} )
BuildRequires:    systemd-units
Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
%else
Requires(post):   /sbin/chkconfig
Requires(preun):  /sbin/service
Requires(preun):  /sbin/chkconfig
Requires(postun): /sbin/service
%endif

Requires:         %{name}-libs = %{version}-%{release}
BuildRequires:    bison flex
BuildRequires:    gcc make automake libtool
BuildRequires:    ncurses-devel readline-devel
BuildRequires:    libxml2-devel openssl-devel
BuildRequires:    libaio-devel
BuildRequires:    python-devel
BuildRequires:    python-ctypes
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

Obsoletes:        hekafs
Obsoletes:        %{name}-common < %{version}-%{release}
Obsoletes:        %{name}-core < %{version}-%{release}
Obsoletes:        %{name}-ufo
Provides:         %{name}-common = %{version}-%{release}
Provides:         %{name}-core = %{version}-%{release}

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

%package api
Summary:          Clustered file-system api library
Group:            System Environment/Daemons
Requires:         %{name} = %{version}-%{release}
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

This package provides the glusterfs libgfapi library.

%package api-devel
Summary:          Development Libraries
Group:            Development/Libraries
Requires:         %{name} = %{version}-%{release}
Requires:         %{name}-devel = %{version}-%{release}

%description api-devel
GlusterFS is a clustered file-system capable of scaling to several
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
GlusterFS is a clustered file-system capable of scaling to several
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
GlusterFS is a clustered file-system capable of scaling to several
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
# We need -api rpm for its __init__.py in Python site-packages area
Requires:         %{name}-api = %{version}-%{release}
Requires:         python python-ctypes

%description extra-xlators
GlusterFS is a clustered file-system capable of scaling to several
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

%if ( 0%{?_build_server} )
%if ( 0%{!?_without_georeplication:1} )
%package geo-replication
Summary:          GlusterFS Geo-replication
Group:            Applications/File
Requires:         %{name} = %{version}-%{release}
Requires:         %{name}-server = %{version}-%{release}
Requires:         python python-ctypes

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

%if ( 0%{?_build_server} )
%if ( 0%{!?_without_regression_tests:1} )
%package regression-tests
Summary:          Development Tools
Group:            Development/Tools
Requires:         %{name} = %{version}-%{release}
Requires:         %{name}-fuse = %{version}-%{release}
Requires:         %{name}-server = %{version}-%{release}
Requires:         perl(App::Prove) perl(Test::Harness) gcc util-linux-ng lvm2
Requires:         python attr dbench git nfs-utils xfsprogs

%description regression-tests
The Gluster Test Framework, is a suite of scripts used for
regression testing of Gluster.
%endif

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

%package server
Summary:          Clustered file-system server
Group:            System Environment/Daemons
Requires:         %{name} = %{version}-%{release}
Requires:         %{name}-cli = %{version}-%{release}
Requires:         %{name}-libs = %{version}-%{release}
Requires:         %{name}-fuse = %{version}-%{release}
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
Requires:         rpcbind
%else
Requires:         portmap
%endif
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
Obsoletes:        %{name}-geo-replication = %{version}-%{release}
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

%prep
%setup -q -n %{name}-%{version}%{?prereltag}

%build
./autogen.sh
%configure \
        %{?_without_rdma} \
        %{?_without_epoll} \
        %{?_without_fusermount} \
        %{?_without_georeplication} \
        %{?_without_ocf} \
        %{?_without_syslog} \
        %{?_without_bd} \
        %{?_without_qemu_block} \
        %{?_without_systemtap}

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

# Build the Python libgfapi examples
pushd api/examples
FLAGS="$RPM_OPT_FLAGS" python setup.py build
popd

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
# install the Glupy Python library in /usr/lib/python*/site-packages
pushd xlators/features/glupy/src
python setup.py install --skip-build --verbose --root %{buildroot}
popd
# install the gfapi Python library in /usr/lib/python*/site-packages
pushd api/examples
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
%if ( 0%{?_build_server} )
%if ( 0%{_for_fedora_koji_builds} )
install -D -p -m 0644 %{SOURCE1} \
    %{buildroot}%{_sysconfdir}/sysconfig/glusterd
install -D -p -m 0644 %{SOURCE2} \
    %{buildroot}%{_sysconfdir}/sysconfig/glusterfsd
%else
install -D -p -m 0644 extras/glusterd-sysconfig \
    %{buildroot}%{_sysconfdir}/sysconfig/glusterd
%endif
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

%if ( 0%{?_build_server} )
# Create working directory
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd

# Update configuration file to /var/lib working directory
sed -i 's|option working-directory /etc/glusterd|option working-directory %{_sharedstatedir}/glusterd|g' \
    %{buildroot}%{_sysconfdir}/glusterfs/glusterd.vol

# Install glusterfsd .service or init.d file
%if ( 0%{_for_fedora_koji_builds} )
%_init_install %{glusterfsd_service} glusterfsd
%endif
%endif

%if ( 0%{_for_fedora_koji_builds} )
# Client logrotate entry
install -D -p -m 0644 %{SOURCE3} \
    %{buildroot}%{_sysconfdir}/logrotate.d/glusterfs-fuse

# Server logrotate entry
%if ( 0%{?_build_server} )
install -D -p -m 0644 %{SOURCE4} \
    %{buildroot}%{_sysconfdir}/logrotate.d/glusterd
# Legacy server logrotate entry
install -D -p -m 0644 %{SOURCE5} \
    %{buildroot}%{_sysconfdir}/logrotate.d/glusterfsd
%endif
%else
install -D -p -m 0644 extras/glusterfs-logrotate \
    %{buildroot}%{_sysconfdir}/logrotate.d/glusterfs
%endif

%if ( 0%{?_build_server} )
%if ( 0%{!?_without_georeplication:1} )
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/geo-replication
touch %{buildroot}%{_sharedstatedir}/glusterd/geo-replication/gsyncd_template.conf
install -D -p -m 0644 extras/glusterfs-georep-logrotate \
    %{buildroot}%{_sysconfdir}/logrotate.d/glusterfs-georep
%endif
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

%if ( 0%{?_build_server} )
subdirs=("add-brick" "create" "copy-file" "delete" "gsync-create" "remove-brick" "reset" "set" "start" "stop")
for dir in ${subdirs[@]}
do
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/"$dir"/{pre,post}
done
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/glustershd
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/peers
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/vols
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/nfs/run
touch %{buildroot}%{_sharedstatedir}/glusterd/glusterd.info
touch %{buildroot}%{_sharedstatedir}/glusterd/options
touch %{buildroot}%{_sharedstatedir}/glusterd/nfs/nfs-server.vol
touch %{buildroot}%{_sharedstatedir}/glusterd/nfs/run/nfs.pid

%if ( 0%{!?_without_georeplication:1} )
install -p -m 0744 extras/hook-scripts/S56glusterd-geo-rep-create-post.sh \
    %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/gsync-create/post
%endif
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


find ./tests ./run-tests.sh -type f | cpio -pd %{buildroot}%{_prefix}/share/glusterfs
%endif

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
%_init_enable glusterfsd

# ".cmd_log_history" is renamed to "cmd_history.log" in RHS 3.0.4
# While upgrading glusterfs-server package from version <= 3.0.3 to
# 3.0.4, ".cmd_log_history" should be renamed to cmd_history.log to retain cli
# command history contents.
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

cp %{_sysconfdir}/glusterfs/group-small-file-perf.example /var/lib/glusterd/groups/small-file-perf
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
else
    glusterd --xlator-option *.upgrade=on -N
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

%postun libs
/sbin/ldconfig

##-----------------------------------------------------------------------------
## All %files should be placed here and keep them sorted
##
%files
%doc ChangeLog COPYING-GPLV2 COPYING-LGPLV3 INSTALL README THANKS
%config(noreplace) %{_sysconfdir}/logrotate.d/*
%if ( 0%{!?_without_syslog:1} )
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
%{_sysconfdir}/rsyslog.d/gluster.conf.example
%endif
%endif
%{_libdir}/glusterfs
%{_sbindir}/glusterfs*
%{_mandir}/man8/*gluster*.8*
%exclude %{_mandir}/man8/gluster.8*
%dir %{_localstatedir}/log/glusterfs
%dir %{_localstatedir}/run/gluster
%dir %{_sharedstatedir}/glusterd
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
# Glupy files are in the -extra-xlators package
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy*
# sample xlators not generally used or usable
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/encryption/rot-13*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/mac-compat*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/testing/performance/symlink-cache*
%{_datadir}/glusterfs/scripts/post-upgrade-script-for-quota.sh
%{_datadir}/glusterfs/scripts/pre-upgrade-script-for-quota.sh
%if ( ! 0%{?_build_server} )
%if ( 0%{?rhel} && 0%{?rhel} > 5 )
%exclude %{_libexecdir}/glusterfs/*
%endif
%exclude %{_datadir}/glusterfs/*
%exclude %{_prefix}/lib/ocf/*
%exclude %{_sharedstatedir}/glusterd/*
%exclude %{_sysconfdir}/glusterfs/*
%exclude %_init_glusterd
%exclude %{_sbindir}/glusterd
%endif
%exclude %{_prefix}/share/glusterfs/*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy.so
%exclude %{python_sitelib}/gluster/glupy.*
%if ( 0%{?rhel} && 0%{?rhel} > 5 )
%exclude %{python_sitelib}/glusterfs_glupy*.egg-info
%endif
%exclude %{_sbindir}/glfsheal

%files api
%exclude %{_libdir}/*.so
# Shared Python-GlusterFS files
%{python_sitelib}/gluster/__init__.*
# libgfapi files
%{_libdir}/libgfapi.*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mount/api*
%{python_sitelib}/gluster/gfapi.*
# Don't expect a .egg-info file on EL5
%if ( ! ( 0%{?rhel} && 0%{?rhel} < 6 ) )
%{python_sitelib}/glusterfs_api*.egg-info
%endif

%files api-devel
%{_libdir}/pkgconfig/glusterfs-api.pc
%{_libdir}/pkgconfig/libgfchangelog.pc
%{_libdir}/libgfapi.so
%{_includedir}/glusterfs/api/*

%files cli
%{_sbindir}/gluster
%{_mandir}/man8/gluster.8*

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

%if ( 0%{!?_without_extra_xlators:1} )
%files extra-xlators
# Glupy C shared library
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy.so
# Glupy Python files
%{python_sitelib}/gluster/glupy.*
# Don't expect a .egg-info file on EL5
%if ( ! ( 0%{?rhel} && 0%{?rhel} < 6 ) )
%{python_sitelib}/glusterfs_glupy*.egg-info
%endif
%endif

%files fuse
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

%if ( 0%{?_build_server} )
%if ( 0%{!?_without_georeplication:1} )
%files geo-replication
%{_sysconfdir}/logrotate.d/glusterfs-georep
%{_libexecdir}/glusterfs/gsyncd
%{_libexecdir}/glusterfs/python/syncdaemon/*
%{_libexecdir}/glusterfs/gverify.sh
%{_libexecdir}/glusterfs/set_geo_rep_pem_keys.sh
%{_libexecdir}/glusterfs/peer_add_secret_pub
%{_libexecdir}/glusterfs/peer_gsec_create
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/geo-replication
%{_sharedstatedir}/glusterd/hooks/1/gsync-create/post/S56glusterd-geo-rep-create-post.sh
%{_datadir}/glusterfs/scripts/get-gfid.sh
%{_datadir}/glusterfs/scripts/slave-upgrade.sh
%{_datadir}/glusterfs/scripts/gsync-upgrade.sh
%{_datadir}/glusterfs/scripts/generate-gfid-file.sh
%{_datadir}/glusterfs/scripts/gsync-sync-gfid
%ghost %attr(0644,-,-) %{_sharedstatedir}/glusterd/geo-replication/gsyncd_template.conf
%endif
%endif

%files libs
%{_libdir}/*.so.*
%exclude %{_libdir}/libgfapi.*

%if ( 0%{!?_without_rdma:1} )
%files rdma
%{_libdir}/glusterfs/%{version}%{?prereltag}/rpc-transport/rdma*
%endif

%if ( 0%{?_build_server} )
%if ( 0%{!?_without_regression_tests:1} )
%files regression-tests
%{_prefix}/share/glusterfs/*
%exclude %{_prefix}/share/glusterfs/tests/basic/rpm.t
%endif

%if ( 0%{!?_without_ocf:1} )
%files resource-agents
# /usr/lib is the standard for OCF, also on x86_64
%{_prefix}/lib/ocf/resource.d/glusterfs
%endif

%files server
%doc extras/clear_xattrs.sh
%if ( 0%{_for_fedora_koji_builds} )
%config(noreplace) %{_sysconfdir}/logrotate.d/glusterd
%endif
%config(noreplace) %{_sysconfdir}/sysconfig/glusterd
%config(noreplace) %{_sysconfdir}/glusterfs
%dir %{_sharedstatedir}/glusterd/groups
%config(noreplace) %{_sharedstatedir}/glusterd/groups/virt
# Legacy configs
%if ( 0%{_for_fedora_koji_builds} )
%config(noreplace) %{_sysconfdir}/logrotate.d/glusterfsd
%config(noreplace) %{_sysconfdir}/sysconfig/glusterfsd
%endif
%config %{_sharedstatedir}/glusterd/hooks/1/add-brick/post/disabled-quota-root-xattr-heal.sh
%config %{_sharedstatedir}/glusterd/hooks/1/add-brick/pre/S28Quota-enable-root-xattr-heal.sh
%config %{_sharedstatedir}/glusterd/hooks/1/set/post/S30samba-set.sh
%config %{_sharedstatedir}/glusterd/hooks/1/set/post/S31ganesha-set.sh
%config %{_sharedstatedir}/glusterd/hooks/1/start/post/S29CTDBsetup.sh
%config %{_sharedstatedir}/glusterd/hooks/1/start/post/S30samba-start.sh
%config %{_sharedstatedir}/glusterd/hooks/1/stop/pre/S30samba-stop.sh
%config %{_sharedstatedir}/glusterd/hooks/1/stop/pre/S29CTDB-teardown.sh
%config %{_sharedstatedir}/glusterd/hooks/1/reset/post/S31ganesha-reset.sh
# extra scripts
%{_datadir}/glusterfs/scripts/stop-all-gluster-processes.sh
# init files
%_init_glusterd
%if ( 0%{_for_fedora_koji_builds} )
%_init_glusterfsd
%endif
# binaries
%{_sbindir}/glusterd
%{_sbindir}/glfsheal
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/storage*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/posix*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/protocol/server*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mgmt*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/nfs*
%{_sharedstatedir}/glusterd/*
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

%ghost %attr(0644,-,-) %config(noreplace) %{_sharedstatedir}/glusterd/glusterd.info
%ghost %attr(0600,-,-) %{_sharedstatedir}/glusterd/options
%ghost %attr(0600,-,-) %{_sharedstatedir}/glusterd/nfs/nfs-server.vol
%ghost %attr(0600,-,-) %{_sharedstatedir}/glusterd/nfs/run/nfs.pid
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
%endif
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
* Wed Jul 22 2015 Scientific Linux Auto Patch Process <SCIENTIFIC-LINUX-DEVEL@LISTSERV.FNAL.GOV>
- Added Source: enable-server-packages.patch
-->  Enable building the glusterfs-server package
- Added Source: glusterfs.ini
-->  Config file for automated patch script

* Thu May 21 2015 Bala.FA <barumuga@redhat.com> - v3.6.0.54-1
- fixes bugs bz#1196057 bz#1196520 bz#1205579 bz#1211656

* Wed Mar 18 2015 Bala.FA <barumuga@redhat.com> - v3.6.0.53-1
- fixes bugs bz#1201633 bz#1202541

* Mon Mar 16 2015 Bala.FA <barumuga@redhat.com> - v3.6.0.52-1
- fixes bugs bz#1189792 bz#1198056 bz#1200677 bz#1201613 bz#BUG:

* Wed Mar 11 2015 Bala.FA <barumuga@redhat.com> - v3.6.0.51-1
- fixes bugs bz#1111944 bz#1200246

* Fri Mar 06 2015 Bala.FA <barumuga@redhat.com> - v3.6.0.50-1
- fixes bugs bz#1111944 bz#1195378 bz#1199441

* Thu Mar 05 2015 Bala.FA <barumuga@redhat.com> - v3.6.0.49-1
- fixes bugs bz#1104039 bz#1194544 bz#1196029 bz#1196546 bz#1196557 bz#1198562

* Mon Mar 02 2015 Bala.FA <barumuga@redhat.com> - v3.6.0.48-1
- fixes bugs bz#1104039 bz#1194525 bz#1194605 bz#1196607

* Wed Feb 25 2015 Bala.FA <barumuga@redhat.com> - v3.6.0.47-1
- fixes bugs bz#1194275 bz#1194574

* Fri Feb 20 2015 Bala.FA <barumuga@redhat.com> - v3.6.0.46-1
- fixes bugs bz#1061594 bz#1110730 bz#1128156 bz#1136714 bz#1144117 
  bz#825748 bz#987511

* Thu Feb 12 2015 Bala.FA <barumuga@redhat.com> - v3.6.0.45-1
- fixes bugs bz#1104459 bz#1139104 bz#1172332 bz#1179563 bz#1180560 
  bz#1181044 bz#1182554 bz#BUG:

* Sun Feb 08 2015 Bala.FA <barumuga@redhat.com> - v3.6.0.44-1
- fixes bugs bz#1090910 bz#1099374 bz#1104112 bz#1104618 bz#1132920 
  bz#1188522

* Sun Feb 01 2015 Bala.FA <barumuga@redhat.com> - v3.6.0.43-1
- fixes bugs bz#1156224 bz#1162306 bz#1171847 bz#1178134 bz#1179183 bz#BUG:

* Thu Jan 08 2015 Bala.FA <barumuga@redhat.com> - v3.6.0.42-1
- fixes bugs bz#1178620

* Thu Jan 01 2015 Bala.FA <barumuga@redhat.com> - v3.6.0.41-1
- fixes bugs bz#1177927

* Wed Dec 17 2014 Bala.FA <barumuga@redhat.com> - v3.6.0.40-1
- fixes bugs bz#1119710

* Wed Dec 17 2014 Bala.FA <barumuga@redhat.com> - v3.6.0.39-1
- fixes bugs bz#1152992 bz#1163209 bz#1171132 bz#1173624

* Thu Dec 11 2014 Bala.FA <barumuga@redhat.com> - v3.6.0.38-1
- fixes bugs bz#1119710

* Mon Dec 08 2014 Bala.FA <barumuga@redhat.com> - v3.6.0.37-1
- fixes bugs bz#1154018 bz#1161531 bz#1168159 bz#1169764 bz#1169916

* Wed Dec 03 2014 Bala FA <barumuga@redhat.com> - v3.6.0.36-1
- fixes bugs bz#1119710 bz#1165026 bz#1168607

* Mon Dec 01 2014 Bala FA <barumuga@redhat.com> - v3.6.0.35-1
- fixes bugs bz#1107606 bz#1160233 bz#1165097 bz#1165704

* Mon Nov 24 2014 Bala FA <barumuga@redhat.com> - v3.6.0.34-1
- fixes bugs bz#1154617 bz#1157381

* Tue Nov 18 2014 Bala FA <barumuga@redhat.com> - v3.6.0.33-1
- fixes bugs bz#1061585 bz#1101438 bz#1104635 bz#1107606 bz#1111534 
  bz#1160280 bz#1162468 bz#1163703 bz#991300 bz#BUG: bz#of

* Fri Nov 07 2014 Bala FA <barumuga@redhat.com> - v3.6.0.32-1
- fixes bugs bz#1102647 bz#1104061 bz#1118359 bz#1130158 bz#1142283
  bz#1146906 bz#1147460 bz#1154836

* Tue Nov 04 2014 Bala FA <barumuga@redhat.com> - v3.6.0.31-1
- fixes bugs bz#969355 bz#1054712 bz#1055489 bz#1102594 bz#1104061
  bz#1109742 bz#1114999 bz#1115441 bz#1122511 bz#1123732 bz#1138547
  bz#1139156 bz#1142087 bz#1142960 bz#1144423 bz#1144428 bz#1146369
  bz#1146830 bz#1147427 bz#1152990

* Tue Oct 28 2014 Bala FA <barumuga@redhat.com> - v3.6.0.30-1
- fixes bugs bz#1110864 bz#1113923 bz#1115899 bz#1131466 bz#1157950
  bz#1157975 bz#1157980 bz#1157982

* Sat Oct 18 2014 Bala FA <barumuga@redhat.com> - v3.6.0.29-3
- respin to use new RHEL base

* Fri Sep 19 2014 Bala FA <barumuga@redhat.com> - v3.6.0.29-1
- fixes bugs bz#1136711 bz#1138288 bz#1139213 bz#1139273 bz#1139473 
  bz#1140643 bz#1143960

* Wed Sep 03 2014 Bala FA <barumuga@redhat.com> - v3.6.0.28-1
- fixes bugs bz#1110694 bz#1116150 bz#1121099 bz#1124692 bz#1127234 
  bz#1136711 bz#921528 bz#969298

* Mon Aug 04 2014 Bala FA <barumuga@redhat.com> - v3.6.0.27-1
- fixes bugs bz#1048930 bz#1108588 bz#1123305 bz#1124583 bz#1125818

* Thu Jul 31 2014 Bala FA <barumuga@redhat.com> - v3.6.0.26-1
- fixes bugs bz#1111029 bz#1111577 bz#1113852 bz#1116761 bz#1117135 
  bz#1117283 bz#1119223 bz#1120830 bz#1121059 bz#1121603

* Tue Jul 22 2014 Bala FA <barumuga@redhat.com> - v3.6.0.25-1
- fixes bugs bz#1007033 bz#1101910 bz#1104121 bz#1104921 bz#1109150 
  bz#1116376 bz#1116703 bz#1116992 bz#1117135 bz#1120198 bz#1120245 bz#BUG:

* Thu Jul 03 2014 Bala FA <barumuga@redhat.com> - v3.6.0.24-1
- fixes bugs bz#1104153 bz#1109149 bz#1112582 bz#1113961 bz#1114008 
  bz#1114592 bz#1115266 bz#1115267

* Wed Jun 25 2014 Bala FA <barumuga@redhat.com> - v3.6.0.23-1
- fixes bugs bz#1111148 bz#1111612

* Mon Jun 23 2014 Bala FA <barumuga@redhat.com> - v3.6.0.22-1
- fixes bugs bz#1006809 bz#1111122

* Fri Jun 20 2014 Bala FA <barumuga@redhat.com> - v3.6.0.21-1
- fixes bugs bz#1101407 bz#1103155 bz#1110211 bz#1110224 bz#1110252 bz#1111468

* Thu Jun 19 2014 Bala FA <barumuga@redhat.com> - v3.6.0.20-1
- fixes bugs bz#1030309 bz#1082951 bz#1103644

* Wed Jun 18 2014 Bala FA <barumuga@redhat.com> - v3.6.0.19-1
- fixes bugs bz#1030309 bz#1088231 bz#1090986 bz#1094681 bz#1095314 
  bz#1098971 bz#1108018 bz#1108505 bz#1108570 bz#1109149

* Mon Jun 16 2014 Bala FA <barumuga@redhat.com> - v3.6.0.18-1
- fixes bugs bz#1006729 bz#1064597 bz#1066389 bz#1082951 bz#1098971 
  bz#1102550 bz#1103688 bz#1105323 bz#1107665 bz#1107961 bz#1108018 bz#1109141

* Fri Jun 13 2014 Bala FA <barumuga@redhat.com> - v3.6.0.17-1
- fixes bugs bz#1082951 bz#1086145 bz#1097102 bz#1100211 bz#1103680 
  bz#1104159 bz#1104574 bz#1104635 bz#1105102 bz#1107523 bz#1108652

* Wed Jun 11 2014 Bala FA <barumuga@redhat.com> - v3.6.0.16-1
- fixes bugs bz#1096565 bz#1096614 bz#1097512 bz#1098087 bz#1099385 
  bz#1101407 bz#1101514 bz#1101961 bz#1104602 bz#1105444

* Mon Jun 09 2014 Bala FA <barumuga@redhat.com> - v3.6.0.15-1
- fixes bugs bz#1096729 bz#1102747

* Sat Jun 07 2014 Bala FA <barumuga@redhat.com> - v3.6.0.14-1
- fixes bugs bz#1094716 bz#1101525

* Thu Jun 05 2014 Bala FA <barumuga@redhat.com> - v3.6.0.13-1
- fixes bugs bz#1046908 bz#1082043 bz#1094832 bz#1095267 bz#1096139 
  bz#1098196 bz#1100282 bz#1104016 bz#1104486

* Tue Jun 03 2014 Bala FA <barumuga@redhat.com> - v3.6.0.12-1
- fixes bugs bz#1099079 bz#1101588 bz#1103576 bz#921528 bz#970813

* Fri May 30 2014 Bala FA <barumuga@redhat.com> - v3.6.0.11-1
- fixes bugs bz#1043566 bz#1080245

* Thu May 29 2014 Bala FA <barumuga@redhat.com> - v3.6.0.10-1
- fixes bugs bz#1102053

* Tue May 27 2014 Bala FA <barumuga@redhat.com> - v3.6.0.9-1
- fixes bugs bz#1098862 bz#1099833

* Mon May 26 2014 Bala FA <barumuga@redhat.com> - v3.6.0.8-1
- fixes bugs bz#1098053

* Fri May 23 2014 Bala FA <barumuga@redhat.com> - v3.6.0.7-1
- fixes bugs bz#1098691

* Thu May 22 2014 Bala FA <barumuga@redhat.com> - v3.6.0.6-1
- fixes bugs bz#1097782 bz#1099010 bz#989480

* Tue May 20 2014 Bala FA <barumuga@redhat.com> - v3.6.0.5-1
- fixes bugs bz#1096729

* Mon May 19 2014 Bala FA <barumuga@redhat.com> - v3.6.0.4-1
- fixes bugs bz#1095190 bz#1096565 bz#1097679 bz#1098069 bz#1098070

* Sat May 17 2014 Bala FA <barumuga@redhat.com> - v3.6.0.3-1
- fixes bugs bz#1094681

* Thu May 15 2014 Bala FA <barumuga@redhat.com> - v3.6.0.2-1
- fixes bugs bz#1061580 bz#1077452 bz#1091961 bz#1093602 bz#1096616 
  bz#1096700 bz#1097224 bz#1098020 bz#1098053

* Wed May 14 2014 Sreenath G <sgirijan@redhat.com> - v3.6.0.1-1
- fixes bugs bz#1062158 bz#1097565 bz#1097581 bz#1097603

* Tue May 13 2014 Bala.FA <barumuga@redhat.com> - v3.6.0.0-1
- Initial build fixes bugs bz#1032894, bz#1039544, bz#1040351,
  bz#1046853, bz#1047782, bz#1053579, bz#1061685, bz#1074947,
  bz#1078061, bz#1080970, bz#1089172, bz#1091926, bz#1091934,
  bz#1092841, bz#1093602, bz#1094708, bz#1095097, bz#1095585,
  bz#1096026, bz#874554, bz#959986
