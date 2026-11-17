/* SPDX-License-Identifier: LGPL-2.1-or-later */
#include "read78_body.h"

int validity_parse_read78_body(const uint8_t *data, size_t length, size_t capacity,
                               struct validity_read78_view *result)
{
    uint32_t count;
    if (!result) return 0;
    result->content = NULL;
    result->length = 0;
    if (!data || length < 4 || length > VALIDITY_READ78_ANALYSIS_LIMIT ||
        capacity > VALIDITY_READ78_ANALYSIS_LIMIT-4) return 0;
    count = (uint32_t)data[0] | ((uint32_t)data[1] << 8) |
            ((uint32_t)data[2] << 16) | ((uint32_t)data[3] << 24);
    if ((size_t)count != length-4 || (size_t)count > capacity) return 0;
    result->length = (size_t)count;
    if (count) result->content = data+4;
    return 1;
}
