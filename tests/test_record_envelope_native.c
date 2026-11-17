/* SPDX-License-Identifier: LGPL-2.1-or-later */
#include "record_envelope.h"
#include <assert.h>
#include <stdlib.h>
#include <string.h>

static void reject(const uint8_t *data, size_t length)
{
    struct validity_envelope_summary s = {9, 9, 9};
    assert(!validity_inspect_record_envelope(data, length, &s));
    assert(s.record_count == 0 && s.application_record_count == 0 && s.content_bytes == 0);
}
int main(void)
{
    uint8_t *data = malloc(65537), *copy = malloc(65537);
    struct validity_envelope_summary s;
    assert(data && copy);
    memset(data, 0xa5, 65537);
    data[0] = 0x17; data[1] = 3; data[2] = 3;
    data[3] = 0xff; data[4] = 0xfb; /* largest content in analysis budget */
    memcpy(copy, data, 65537);
    for (size_t n = 0; n < 65536; n++)
        reject(data, n);
    assert(validity_inspect_record_envelope(data, 65536, &s));
    assert(s.record_count == 1 && s.application_record_count == 1 && s.content_bytes == 65531);
    reject(data, 65537);
    assert(memcmp(data, copy, 65537) == 0);
    reject(NULL, 6);
    assert(!validity_inspect_record_envelope(data, 65536, NULL));
    /* Maximum number of minimum-size records, followed by incomplete tails. */
    for (size_t p = 0; p < 65532; p += 6) {
        data[p] = (uint8_t)(0x14 + (p / 6) % 4);
        data[p+1] = 3; data[p+2] = 3; data[p+3] = 0; data[p+4] = 1;
    }
    assert(validity_inspect_record_envelope(data, 65532, &s));
    assert(s.record_count == 10922 && s.application_record_count == 2730 && s.content_bytes == 10922);
    for (size_t n = 65533; n <= 65536; n++) reject(data, n);
    data[6] = 0x13; reject(data, 12); /* valid prefix cannot leak partial counts */
    free(copy); free(data);
    return 0;
}
