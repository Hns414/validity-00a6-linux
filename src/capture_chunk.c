/* SPDX-License-Identifier: LGPL-2.1-or-later */
#include "capture_chunk.h"
#include "status_reply.h"
#include <string.h>

int validity_inspect_reference_chunk(const uint8_t *data, size_t length,
                                    size_t rows_seen,
                                    struct validity_reference_chunk *out)
{
    if (!out) return 0;
    memset(out, 0, sizeof(*out));
    if (!data || length < 6 || rows_seen >= 112) return 0;
    struct validity_status_reply status;
    if (!validity_parse_status_reply(data, length, &status) || status.device_status)
        return 0;
    size_t payload = (size_t)data[2] | ((size_t)data[3] << 8);
    if (!payload || payload != length-6 || payload % 120) return 0;
    size_t rows = payload/120;
    if (rows > 112-rows_seen) return 0;
    out->payload_bytes = payload;
    out->rows_in_chunk = rows;
    out->total_rows = rows_seen+rows;
    out->frame_complete = out->total_rows == 112;
    return 1;
}
