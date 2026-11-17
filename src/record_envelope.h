/* SPDX-License-Identifier: LGPL-2.1-or-later */
#ifndef VALIDITY_RECORD_ENVELOPE_H
#define VALIDITY_RECORD_ENVELOPE_H
#include <stddef.h>
#include <stdint.h>
#define VALIDITY_ENVELOPE_ANALYSIS_LIMIT ((size_t)65536)
struct validity_envelope_summary {
    size_t record_count;
    size_t application_record_count;
    size_t content_bytes;
};
/* Offline strict candidate scope: complete, nonempty 3/3 records of types
 * 0x14..0x17. Rejects partial input, empty records and trailing markers.
 * Returns 1 on structural acceptance, 0 on rejection; clears nonnull result
 * on rejection. Caller supplies actual accessible length and a result that
 * does not overlap input. No authentication, decryption, response association,
 * stream reassembly, allocation, content copy, logging or USB. Acceptance
 * does not establish completeness of a device response or biometric meaning. */
int validity_inspect_record_envelope(const uint8_t *data, size_t length,
                                    struct validity_envelope_summary *result);
#endif
