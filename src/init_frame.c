/* SPDX-License-Identifier: LGPL-2.1-or-later */
#include "init_frame.h"
#include <string.h>

int validity_encode_init_frame(const uint8_t *arguments, size_t length,
                               uint8_t *output, size_t capacity)
{
    if (!arguments || !output || length != 500 || capacity < 501)
        return 0;
    memmove(output+1, arguments, 500);
    output[0] = 0x06;
    return 501;
}
