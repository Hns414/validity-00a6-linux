/* SPDX-License-Identifier: LGPL-2.1-or-later */
#ifndef VALIDITY_CAPTURE_CHUNK_H
#define VALIDITY_CAPTURE_CHUNK_H
#include <stddef.h>
#include <stdint.h>

/* Offline candidate format from the pinned 0091 reference, NOT a 00a6 spec.
 * No pixel copy, storage or USB access. Not linked into the hardware probe. */
struct validity_reference_chunk {
    size_t payload_bytes;
    size_t rows_in_chunk;
    size_t total_rows;
    int frame_complete;
};

/* Requires an exact standalone frame: status(2), length LE(2), unknown(2),
 * then whole rows of 8 control bytes + 112 pixels, at most 112 rows total.
 * Returns 1 only for a candidate shape, not validated biometric data.
 * Clears available output on failure. Caller supplies accessible length. */
int validity_inspect_reference_chunk(const uint8_t *data, size_t length,
                                    size_t rows_seen,
                                    struct validity_reference_chunk *out);
#endif
