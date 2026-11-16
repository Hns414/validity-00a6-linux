/* SPDX-License-Identifier: LGPL-2.1-or-later */
#include "capture_chunk.h"
#include <assert.h>
#include <string.h>

static void declared(uint8_t *data, size_t bytes)
{
    data[2] = (uint8_t)bytes;
    data[3] = (uint8_t)(bytes >> 8);
}

int main(void)
{
    uint8_t data[6+120*113+1] = {0};
    struct validity_reference_chunk out, baseline, zero = {0};
    for (size_t rows=1; rows<=112; rows++) {
        declared(data, rows*120);
        assert(validity_inspect_reference_chunk(data, 6+rows*120, 112-rows, &out));
        assert(out.payload_bytes == rows*120 && out.rows_in_chunk == rows);
        assert(out.total_rows == 112 && out.frame_complete);
    }
    declared(data, 120);
    assert(validity_inspect_reference_chunk(data, 126, 0, &baseline));
    assert(baseline.total_rows == 1 && !baseline.frame_complete);
    /* Control pixels, unknown header bytes and image bytes cannot escape. */
    for (size_t i=4; i<126; i++) {
        data[i] ^= 0xff;
        assert(validity_inspect_reference_chunk(data, 126, 0, &out));
        assert(memcmp(&out, &baseline, sizeof(out)) == 0);
    }
    for (size_t length=0; length<127; length++) {
        if (length == 126) continue;
        memset(&out, 0xff, sizeof(out));
        assert(!validity_inspect_reference_chunk(data, length, 0, &out));
        assert(memcmp(&out, &zero, sizeof(out)) == 0);
    }
    for (size_t payload=0; payload<=120*113; payload++) {
        if (payload && payload%120 == 0 && payload<=120*112) continue;
        declared(data, payload);
        assert(!validity_inspect_reference_chunk(data, payload+6, 0, &out));
        assert(memcmp(&out, &zero, sizeof(out)) == 0);
    }
    declared(data, 120);
    for (int i=0; i<2; i++) {
        data[i] = 1;
        assert(!validity_inspect_reference_chunk(data, 126, 0, &out));
        assert(memcmp(&out, &zero, sizeof(out)) == 0);
        data[i] = 0;
    }
    for (size_t seen=112; seen<=113; seen++)
        assert(!validity_inspect_reference_chunk(data, 126, seen, &out));
    declared(data, 240);
    assert(!validity_inspect_reference_chunk(data, 246, 111, &out));
    assert(memcmp(&out, &zero, sizeof(out)) == 0);
    declared(data, 120);
    assert(!validity_inspect_reference_chunk(data, 126, SIZE_MAX, &out));
    assert(!validity_inspect_reference_chunk(NULL, 126, 0, &out));
    assert(memcmp(&out, &zero, sizeof(out)) == 0);
    assert(!validity_inspect_reference_chunk(data, 126, 0, NULL));
    return 0;
}
