/* SPDX-License-Identifier: LGPL-2.1-or-later */
#include "init_frame.h"
#include <assert.h>
#include <stdint.h>
#include <string.h>

int main(void)
{
    uint8_t arguments[600], guarded[503], snapshot[503], overlap[501];
    for (size_t i=0; i<sizeof(arguments); i++) arguments[i]=(uint8_t)i;
    for (size_t length=0; length<=600; length++) {
        memset(guarded, 0xa5, sizeof(guarded));
        memcpy(snapshot, guarded, sizeof(guarded));
        int result=validity_encode_init_frame(arguments, length, guarded+1, 501);
        if (length==484 || length==500) {
            assert(result==(int)(length+1) && guarded[1]==0x06);
            assert(memcmp(guarded+2, arguments, length)==0);
            assert(guarded[0]==0xa5);
            for (size_t i=length+2; i<sizeof(guarded); i++) assert(guarded[i]==0xa5);
        } else {
            assert(result==0 && memcmp(guarded, snapshot, sizeof(guarded))==0);
        }
    }
    for (size_t length=484; length<=500; length+=16) {
      for (size_t capacity=0; capacity<length+1; capacity++) {
        memset(guarded, 0xa5, sizeof(guarded));
        memcpy(snapshot, guarded, sizeof(guarded));
        assert(validity_encode_init_frame(arguments, length, guarded+1, capacity)==0);
        assert(memcmp(guarded, snapshot, sizeof(guarded))==0);
      }
      assert(validity_encode_init_frame(arguments, length, guarded+1, length+1)==(int)(length+1));
      assert(validity_encode_init_frame(NULL, length, guarded+1, 501)==0);
      assert(validity_encode_init_frame(arguments, length, NULL, 501)==0);
      memcpy(overlap, arguments, length);
      assert(validity_encode_init_frame(overlap, length, overlap, sizeof(overlap))==(int)(length+1));
      assert(overlap[0]==0x06 && memcmp(overlap+1, arguments, length)==0);
      memcpy(overlap+1, arguments, length);
      assert(validity_encode_init_frame(overlap+1, length, overlap, sizeof(overlap))==(int)(length+1));
      assert(memcmp(overlap+1, arguments, length)==0);
    }
    assert(validity_encode_init_frame(NULL, 500, guarded+1, 501)==0);
    assert(validity_encode_init_frame(arguments, 500, NULL, 501)==0);
    assert(validity_encode_init_frame(arguments, SIZE_MAX, guarded+1, SIZE_MAX)==0);
    memcpy(overlap, arguments, 500);
    assert(validity_encode_init_frame(overlap, 500, overlap, sizeof(overlap))==501);
    assert(overlap[0]==0x06 && memcmp(overlap+1, arguments, 500)==0);
    return 0;
}
