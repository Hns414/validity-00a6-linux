/* SPDX-License-Identifier: LGPL-2.1-or-later */
#include "rom_info.h"
#include "status_reply.h"
#include <string.h>

const char *rom_info_decode(const unsigned char *data, size_t length,
                            struct rom_info_candidate *out)
{
    if (!out) return "invalid_argument";
    memset(out, 0, sizeof(*out));
    if (!data || length != 38) return "unexpected_length";
    struct validity_status_reply header;
    if (!validity_parse_status_reply(data, length, &header)) return "unexpected_length";
    if (header.device_status != 0) return "device_status_nonzero";
    out->firmware_build = (uint32_t)data[6] | ((uint32_t)data[7] << 8) |
                          ((uint32_t)data[8] << 16) | ((uint32_t)data[9] << 24);
    out->firmware_major = data[10];
    out->firmware_minor = data[11];
    out->product_code = data[13];
    return "candidate_layout_unverified";
}
