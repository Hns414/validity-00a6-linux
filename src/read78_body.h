/* SPDX-License-Identifier: LGPL-2.1-or-later */
#ifndef VALIDITY_READ78_BODY_H
#define VALIDITY_READ78_BODY_H
#include <stddef.h>
#include <stdint.h>

#define VALIDITY_READ78_ANALYSIS_LIMIT ((size_t)65536)
struct validity_read78_view {
    const uint8_t *content;
    size_t length;
};
/* Offline candidate format only: LE uint32 count followed by exactly count bytes.
 * Input must already be independently normalized, authenticated as required,
 * and separated from device status. This function establishes none of those.
 * Returns 1 on structural acceptance, 0 on rejection (clears result if nonnull).
 * capacity is the intended content destination size, at most 65532 in this
 * local analysis scope. Zero content is structurally accepted with NULL view.
 * Caller supplies actual accessible input length; result must not overlap input.
 * A nonempty view borrows data+4: retain input unchanged while using the view.
 * No allocation, content copy, USB, logging, or biometric interpretation. */
int validity_parse_read78_body(const uint8_t *data, size_t length, size_t capacity,
                               struct validity_read78_view *result);
#endif
