quotadir = $(libexecdir)/glusterfs/quota
quota_SCRIPTS = quota-remove-xattr.sh

EditorModedir = $(docdir)
EditorMode_DATA = glusterfs-mode.el glusterfs.vim

SUBDIRS = init.d benchmarking hook-scripts $(OCF_SUBDIR) LinuxRPM geo-rep

confdir = $(sysconfdir)/glusterfs
conf_DATA = glusterfs-logrotate group-virt.example group-small-file-perf.example \
	glusterfs-georep-logrotate gluster-rsyslog-7.2.conf \
	gluster-rsyslog-5.8.conf logger.conf.example

EXTRA_DIST = specgen.scm MacOSX/Portfile glusterfs-mode.el glusterfs.vim  \
	migrate-unify-to-distribute.sh backend-xattr-sanitize.sh          \
	backend-cleanup.sh disk_usage_sync.sh quota-remove-xattr.sh       \
        glusterfs-logrotate clear_xattrs.sh \
	group-virt.example glusterd-sysconfig group-small-file-perf.example \
	glusterfs-georep-logrotate gluster-rsyslog-7.2.conf \
	gluster-rsyslog-5.8.conf logger.conf.example
