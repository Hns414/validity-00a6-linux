/* SPDX-License-Identifier: LGPL-2.1-or-later */
#include "status_reply.h"
#include <string.h>

int validity_parse_status_reply(const uint8_t *data, size_t length,
                                struct validity_status_reply *result)
{
    if (!result) return 0;
    memset(result, 0, sizeof(*result));
    if (!data || length < 2) return 0;
    result->device_status = (uint16_t)((uint16_t)data[0] | ((uint16_t)data[1] << 8));
    result->payload_length = length-2;
    return 1;
}
