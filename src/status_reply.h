/* SPDX-License-Identifier: LGPL-2.1-or-later */
#ifndef VALIDITY_STATUS_REPLY_H
#define VALIDITY_STATUS_REPLY_H
#include <stddef.h>
#include <stdint.h>

struct validity_status_reply {
    uint16_t device_status;
    size_t payload_length;
};
/* For replies independently identified as status-framed cleartext.
 * Returns 1 for a parsed header, including nonzero device status, else 0.
 * Does not interpret/copy the payload or decide biometric/protocol success.
 * Caller supplies actual accessible length. Result is cleared on invalid input. */
int validity_parse_status_reply(const uint8_t *data, size_t length,
                                struct validity_status_reply *result);
#endif
