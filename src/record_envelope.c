/* SPDX-License-Identifier: LGPL-2.1-or-later */
#include "record_envelope.h"

int validity_inspect_record_envelope(const uint8_t *data, size_t length,
                                    struct validity_envelope_summary *result)
{
    size_t pos = 0;
    struct validity_envelope_summary counts = {0, 0, 0};
    if (result == NULL)
        return 0;
    *result = counts;
    if (data == NULL || length < 6 || length > VALIDITY_ENVELOPE_ANALYSIS_LIMIT)
        return 0;
    while (pos < length) {
        size_t count;
        if (length - pos < 5)
            return 0;
        if (data[pos] < 0x14 || data[pos] > 0x17 ||
            data[pos + 1] != 3 || data[pos + 2] != 3)
            return 0;
        count = ((size_t)data[pos + 3] << 8) | data[pos + 4];
        if (count == 0 || count > length - pos - 5)
            return 0;
        counts.record_count++;
        counts.application_record_count += data[pos] == 0x17;
        counts.content_bytes += count;
        pos += 5 + count;
    }
    *result = counts;
    return 1;
}
