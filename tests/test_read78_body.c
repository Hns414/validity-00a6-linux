/* SPDX-License-Identifier: LGPL-2.1-or-later */
#include "read78_body.h"
#include <assert.h>
#include <stdlib.h>
#include <string.h>

static void reject(const uint8_t *data, size_t length, size_t capacity)
{
    struct validity_read78_view out = {data, 123};
    assert(!validity_parse_read78_body(data, length, capacity, &out));
    assert(!out.content && !out.length);
}

int main(void)
{
    uint8_t *data = malloc(65537), *snapshot = malloc(65537);
    struct validity_read78_view out;
    assert(data && snapshot);
    for (size_t n = 0; n <= 65532; n += n < 256 ? 1 : 251) {
        memset(data, 0xa5, n+4);
        data[0] = (uint8_t)n; data[1] = (uint8_t)(n >> 8);
        data[2] = 0; data[3] = 0;
        memcpy(snapshot, data, n+4);
        assert(validity_parse_read78_body(data, n+4, n, &out));
        assert(out.length == n && out.content == (n ? data+4 : NULL));
        assert(!memcmp(data, snapshot, n+4));
        if (n) reject(data, n+4, n-1);
        for (size_t cut = 0; cut < n+4; cut += cut < 16 ? 1 : 997)
            reject(data, cut, n);
        reject(data, n+5, n);
    }
    memset(data, 0, 65537);
    data[0] = 0xfc; data[1] = 0xff;
    assert(validity_parse_read78_body(data, 65536, 65532, &out));
    assert(out.length == 65532 && out.content == data+4);
    reject(data, 65537, 65532);
    memset(data, 0xff, 4); reject(data, 4, 65532);
    data[0] = 0; data[1] = 0; data[2] = 0; data[3] = 1;
    reject(data, 5, 1); /* big-endian representation must not be accepted */
    memset(data, 0, 4);
    assert(validity_parse_read78_body(data, 4, 0, &out));
    assert(!out.content && !out.length);
    reject(data, 4, SIZE_MAX);
    reject(NULL, 4, 0);
    assert(!validity_parse_read78_body(data, 4, 0, NULL));
    free(snapshot); free(data);
    return 0;
}
