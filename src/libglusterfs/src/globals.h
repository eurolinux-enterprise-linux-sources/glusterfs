/*
  Copyright (c) 2008-2012 Red Hat, Inc. <http://www.redhat.com>
  This file is part of GlusterFS.

  This file is licensed to you under your choice of the GNU Lesser
  General Public License, version 3 or any later version (LGPLv3 or
  later), or the GNU General Public License, version 2 (GPLv2), in all
  cases as published by the Free Software Foundation.
*/

#ifndef _GLOBALS_H
#define _GLOBALS_H

#define GF_DEFAULT_BASE_PORT 24007

#define GD_OP_VERSION_KEY     "operating-version"
#define GD_MIN_OP_VERSION_KEY "minimum-operating-version"
#define GD_MAX_OP_VERSION_KEY "maximum-operating-version"

/* RHS versions - OP-VERSION mapping
 *
 * RHS-2.0 Z    - 1
 * RHS-2.1 Z    - 2
 * RHS-2.1 u5   - 20105
 * RHS-3.0 Z    - 30000
 *
 *
 * Starting with RHS-3.0, the op-version will be multi-digit integer values
 * based on the RHS version, instead of a simply incrementing integer value. The
 * op-version for a given RHS X(Major).Y(Minor).Z(Update) release will be an
 * integer with digits XYZ. The Y and Z values will be 2 digits wide always
 * padded with 0 as needed. This should allow for some gaps between two Y
 * releases for backports of features in Z releases.
 */
#define GD_OP_VERSION_MIN  1 /* MIN is the fresh start op-version, mostly
                                should not change */
#define GD_OP_VERSION_MAX  30000 /* MAX VERSION is the maximum count in VME table,
                                should keep changing with introduction of newer
                                versions */

#define GD_OP_VERSION_RHS_3_0    30000 /* Op-Version of RHS 3.0 */
#define GD_OP_VER_PERSISTENT_AFR_XATTRS GD_OP_VERSION_RHS_3_0

#define GD_OP_VERSION_RHS_2_1_5  20105 /* RHS 2.1 update 5 */

#include "xlator.h"

/* THIS */
#define THIS (*__glusterfs_this_location())

xlator_t **__glusterfs_this_location ();
xlator_t *glusterfs_this_get ();
int glusterfs_this_set (xlator_t *);

/* syncopctx */
void *syncopctx_getctx ();
int syncopctx_setctx (void *ctx);

/* task */
void *synctask_get ();
int synctask_set (void *);

/* uuid_buf */
char *glusterfs_uuid_buf_get();
/* lkowner_buf */
char *glusterfs_lkowner_buf_get();

/* init */
int glusterfs_globals_init (glusterfs_ctx_t *ctx);

extern const char *gf_fop_list[];

#endif /* !_GLOBALS_H */
