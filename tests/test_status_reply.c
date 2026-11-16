/* SPDX-License-Identifier: LGPL-2.1-or-later */
#include "status_reply.h"
#include <assert.h>
#include <string.h>

int main(void)
{
    uint8_t data[128];
    struct validity_status_reply result, zero = {0};
    memset(&zero, 0, sizeof(zero));
    memset(data, 0xa5, sizeof(data));
    data[0]=0xef; data[1]=0xbe;
    for (size_t length=0; length<=sizeof(data); length++) {
        memset(&result, 0xff, sizeof(result));
        int parsed=validity_parse_status_reply(data, length, &result);
        if (length<2) {
            assert(parsed==0 && memcmp(&result, &zero, sizeof(result))==0);
        } else {
            assert(parsed==1 && result.device_status==0xbeef);
            assert(result.payload_length==length-2);
        }
    }
    assert(validity_parse_status_reply(NULL, 38, &result)==0);
    assert(memcmp(&result, &zero, sizeof(result))==0);
    assert(validity_parse_status_reply(data, 38, NULL)==0);
    data[0]=0; data[1]=0;
    assert(validity_parse_status_reply(data, 2, &result)==1);
    assert(result.device_status==0 && result.payload_length==0);
    for (size_t i=2; i<sizeof(data); i++) data[i]=(uint8_t)i;
    assert(validity_parse_status_reply(data, sizeof(data), &result)==1);
    assert(result.device_status==0 && result.payload_length==126);
    return 0;
}
