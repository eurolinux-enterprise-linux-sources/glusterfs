/*
  Copyright (c) 2008-2013 Red Hat, Inc. <http://www.redhat.com>
  This file is part of GlusterFS.

  This file is licensed to you under your choice of the GNU Lesser
  General Public License, version 3 or any later version (LGPLv3 or
  later), or the GNU General Public License, version 2 (GPLv2), in all
  cases as published by the Free Software Foundation.
*/

#ifndef _CONFIG_H
#define _CONFIG_H
#include "config.h"
#endif

#include "rpc-clnt.h"
#include "xdr-generic.h"

#include "protocol-common.h"
#include "glusterd-utils.h"
#include "common-utils.h"
#include "rpc-common-xdr.h"
#include "glusterfs3-xdr.h"
#include "rpcsvc.h"

int
glusterd_ping (rpcsvc_request_t *req)
{
        gf_common_rsp rsp = {0,};

        /* Accepted */
        rsp.op_ret = 0;

        glusterd_submit_reply (req, &rsp, NULL, 0, NULL,
                               (xdrproc_t)xdr_gf_common_rsp);

        return 0;
}

char *glusterd_ping_proc[GD_PING_MAXVALUE] = {
        [GD_PING_NULL]         = "NULL",
        [GD_PING_PING]         = "PING",
};

rpc_clnt_prog_t glusterd_ping_prog = {
        .progname  = "Glusterd PING",
        .prognum   = GD_PING_PROGRAM,
        .progver   = GD_PING_VERSION,
        .procnames = glusterd_ping_proc,
};

rpcsvc_actor_t gluster_ping_actors[] = {
        [GD_PING_PING]       = {"PING",       GD_PING_PING,       glusterd_ping,           NULL, 0},
};


struct rpcsvc_program glusterd_pingsvc = {
        .progname  = "Glusterd PING",
        .prognum   = GD_PING_PROGRAM,
        .progver   = GD_PING_VERSION,
        .actors    = gluster_ping_actors,
        .numactors = GD_PING_MAXVALUE,
};

int glusterd_ping_cbk (struct rpc_req *req, struct iovec *iov, int count,
                       void *myframe);
void
rpc_glusterd_ping_timer_expired (void *data)
{
        rpc_transport_t         *trans              = NULL;
        rpc_clnt_connection_t   *conn               = NULL;
        int                      disconnect         = 0;
        int                      transport_activity = 0;
        struct timespec          timeout            = {0, };
        struct timeval           current            = {0, };
        struct rpc_clnt         *rpc               = NULL;
        xlator_t                *this               = THIS;
        int                      ret                = -1;
        int                      ping_timeout       = 0;

        rpc = data;
        if (!rpc) {
                gf_log (this->name, GF_LOG_WARNING, "rpc not initialized");
                goto out;
        }

        conn = &rpc->conn;
        trans = conn->trans;

        if (!trans) {
                gf_log (this->name, GF_LOG_WARNING, "transport not initialized");
                goto out;
        }

        ret = dict_get_int32 (this->options, "ping-timeout", &ping_timeout);
        if (ret) {
                gf_log (this->name, GF_LOG_INFO, "defaulting ping-timeout "
                        "to 10");
                ret = 0;
                ping_timeout = 10;
        }

        pthread_mutex_lock (&conn->lock);
        {
                if (conn->ping_timer) {
                        gf_timer_call_cancel (this->ctx,
                                              conn->ping_timer);
                        conn->ping_timer = NULL;
                        rpc_clnt_unref (rpc);
                }
                gettimeofday (&current, NULL);

                if (((current.tv_sec - conn->last_received.tv_sec) <
                     ping_timeout)
                    || ((current.tv_sec - conn->last_sent.tv_sec) <
                        ping_timeout)) {
                        transport_activity = 1;
                }

                if (transport_activity) {
                        gf_log (trans->name, GF_LOG_TRACE,
                                "ping timer expired but transport activity "
                                "detected - not bailing transport");
                        timeout.tv_sec = ping_timeout;
                        timeout.tv_nsec = 0;

                        conn->ping_timer =
                                gf_timer_call_after (this->ctx, timeout,
                                                     rpc_glusterd_ping_timer_expired,
                                                     (void *) rpc);
                        if (conn->ping_timer == NULL) {
                                gf_log (trans->name, GF_LOG_WARNING,
                                        "unable to setup ping timer");
			} else {
				rpc_clnt_ref (rpc);
			}

                } else {
                        conn->ping_started = 0;
                        conn->ping_timer = NULL;
                        disconnect = 1;
                }
        }
        pthread_mutex_unlock (&conn->lock);

        if (disconnect) {
                gf_log (trans->name, GF_LOG_CRITICAL,
                        "server %s has not responded in the last %d "
                        "seconds, disconnecting.",
                        conn->trans->peerinfo.identifier,
                        ping_timeout);

                rpc_transport_disconnect (conn->trans);
        }

out:
        return;
}

void
glusterd_start_ping (void *data)
{
        rpc_clnt_connection_t   *conn        = NULL;
        int32_t                  ret         = -1;
        struct timespec          timeout     = {0, };
        call_frame_t            *frame       = NULL;
        int                      frame_count = 0;
        int                      ping_timeout = 0;
        struct rpc_clnt         *rpc         = NULL;
        xlator_t                *this       = THIS;


        rpc = data;
        if (!rpc) {
                gf_log (this->name, GF_LOG_WARNING, "rpc not initialized");
                goto fail;
        }
        ret = dict_get_int32 (this->options, "ping-timeout", &ping_timeout);
        if (ret) {
                gf_log (this->name, GF_LOG_INFO, "defaulting ping-timeout "
                        "to 10s");
                ret = 0;
                ping_timeout = 10;
        }
        conn = &rpc->conn;

        if (ping_timeout == 0) {
                gf_log (this->name, GF_LOG_INFO, "ping timeout is 0, returning");
                return;
        }

        pthread_mutex_lock (&conn->lock);
        {
                if (conn->ping_timer) {
                        gf_timer_call_cancel (this->ctx, conn->ping_timer);
                        conn->ping_timer = NULL;
                        rpc_clnt_unref (rpc);
                }

                conn->ping_started = 0;

                if (conn->saved_frames)
                        /* treat the case where conn->saved_frames is NULL
                           as no pending frames */
                        frame_count = conn->saved_frames->count;

                if ((frame_count == 0) || !conn->connected) {
                        /* using goto looked ugly here,
                         * hence getting out this way */
                        /* unlock */
                        gf_log (this->name, GF_LOG_DEBUG,
                                "returning as transport is already disconnected"
                                " OR there are no frames (%d || %d)",
                                frame_count, !conn->connected);

                        pthread_mutex_unlock (&conn->lock);
                        return;
                }

                if (frame_count < 0) {
                        gf_log (this->name, GF_LOG_WARNING,
                                "saved_frames->count is %"PRId64,
                                conn->saved_frames->count);
                        conn->saved_frames->count = 0;
                }

                timeout.tv_sec = ping_timeout;
                timeout.tv_nsec = 0;

                conn->ping_timer =
                        gf_timer_call_after (this->ctx, timeout,
                                             rpc_glusterd_ping_timer_expired,
                                             (void *) rpc);

                if (conn->ping_timer == NULL) {
                        gf_log (this->name, GF_LOG_WARNING,
                                "unable to setup ping timer");
                } else {
			rpc_clnt_ref (rpc);
                        conn->ping_started = 1;
                }
        }
        pthread_mutex_unlock (&conn->lock);

        frame = create_frame (this, this->ctx->pool);
        if (!frame)
                goto fail;

        frame->local = rpc_clnt_ref (rpc);
        ret = glusterd_submit_request_unlocked (rpc, NULL, frame,
                        &glusterd_ping_prog,
                        GD_PING_PING, NULL,
                        this, glusterd_ping_cbk,
                            (xdrproc_t) NULL);
        if (ret) {
                gf_log (this->name, GF_LOG_ERROR,
                        "failed to start ping timer");
                goto fail;
        }

        return;

fail:
        if (frame) {
                STACK_DESTROY (frame->root);
        }

        return;
}


int
glusterd_ping_cbk (struct rpc_req *req, struct iovec *iov, int count,
                 void *myframe)
{
        xlator_t              *this    = THIS;
        rpc_clnt_connection_t *conn    = NULL;
        struct timespec        timeout = {0, };
        call_frame_t          *frame   = NULL;
        int                    ret     = 0;
        int                    ping_timeout = 0;
        struct rpc_clnt       *rpc     = NULL;

        if (!myframe) {
                gf_log (this->name, GF_LOG_WARNING,
                        "frame with the request is NULL");
                goto out;
        }
        frame = myframe;
        rpc = frame->local;
        conn = &rpc->conn;
	frame->local = NULL;

        ret = dict_get_int32 (this->options, "ping-timeout", &ping_timeout);
        if (ret) {
                gf_log (this->name, GF_LOG_INFO, "defaulting ping-timeout "
                        "to 10s");
                ret = 0;
                ping_timeout = 10;
        }

        pthread_mutex_lock (&conn->lock);
        {
                if (req->rpc_status == -1) {
                        if (conn->ping_timer != NULL) {
                                gf_log (this->name, GF_LOG_WARNING,
                                        "socket or ib related error");
                                gf_timer_call_cancel (this->ctx,
                                                      conn->ping_timer);
                                conn->ping_timer = NULL;
                                conn->ping_started = 0;
                                rpc_clnt_unref (rpc);

                        } else {
                                /* timer expired and transport bailed out */
                                gf_log (this->name, GF_LOG_WARNING,
                                        "timer must have expired");
                        }

                        goto unlock;
                }


                timeout.tv_sec  = ping_timeout;
                timeout.tv_nsec = 0;

                if (conn->ping_timer) {
                        gf_timer_call_cancel (this->ctx,
                                      conn->ping_timer);
                        conn->ping_timer = NULL;
                        rpc_clnt_unref (rpc);
                }

                conn->ping_timer =
                        gf_timer_call_after (this->ctx, timeout,
                                             glusterd_start_ping, (void *)rpc);

                if (conn->ping_timer == NULL) {
                        gf_log (this->name, GF_LOG_WARNING,
                                "failed to set the ping timer");
                        conn->ping_started = 0;

                } else {
                        rpc_clnt_ref (rpc);

                }
        }
unlock:
        pthread_mutex_unlock (&conn->lock);
out:
        if (frame)
                STACK_DESTROY (frame->root);
        if (rpc)
                rpc_clnt_unref (rpc);
        return 0;
}

