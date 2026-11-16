/* SPDX-License-Identifier: LGPL-2.1-or-later */
#include "rom_info.h"
#include <assert.h>
#include <string.h>

int main(void)
{
    unsigned char data[64] = {0};
    struct rom_info_candidate out, zero = {0}, expected = {0};
    data[6] = 0x78; data[7] = 0x56; data[8] = 0x34; data[9] = 0x12;
    data[10] = 6; data[11] = 7; data[13] = 0x30;
    for (size_t length = 0; length <= sizeof(data); length++) {
        memset(&out, 0xff, sizeof(out));
        const char *status = rom_info_decode(data, length, &out);
        if (length != 38) {
            assert(strcmp(status, "unexpected_length") == 0);
            assert(memcmp(&out, &zero, sizeof(out)) == 0);
        } else {
            assert(strcmp(status, "candidate_layout_unverified") == 0);
            assert(out.firmware_build == 0x12345678);
            assert(out.firmware_major == 6 && out.firmware_minor == 7);
            assert(out.product_code == 0x30);
            expected = out;
        }
    }
    /* Timestamp, padding, unknown fields and trailing identifiers cannot affect output. */
    for (size_t i = 2; i < sizeof(data); i++) {
        if ((i >= 6 && i <= 11) || i == 13) continue;
        data[i] = 0xed;
        assert(strcmp(rom_info_decode(data, 38, &out), "candidate_layout_unverified") == 0);
        assert(memcmp(&out, &expected, sizeof(out)) == 0);
    }
    for (int i = 0; i < 2; i++) {
        data[i] = 1;
        assert(strcmp(rom_info_decode(data, 38, &out), "device_status_nonzero") == 0);
        assert(memcmp(&out, &zero, sizeof(out)) == 0);
        data[i] = 0;
    }
    assert(strcmp(rom_info_decode(NULL, 38, &out), "unexpected_length") == 0);
    assert(memcmp(&out, &zero, sizeof(out)) == 0);
    assert(strcmp(rom_info_decode(data, 38, NULL), "invalid_argument") == 0);
    struct rom_info_discriminator_candidate branch, branch_zero = {0};
    memset(data, 0, sizeof(data));
    data[10] = 6;
    for (unsigned int value = 0; value < 256; value++) {
        data[0x19] = (unsigned char)value;
        assert(strcmp(rom_info_discriminator_decode(data, 38, &branch),
                      "candidate_layout_unverified") == 0);
        assert(branch.firmware_major == 6);
        assert(branch.flag_0x20_set == ((value & 0x20u) != 0));
        assert(branch.derived_value == ((value & 0x20u) ? 2u : 3u));
    }
    struct rom_info_discriminator_candidate baseline = branch;
    for (size_t i = 2; i < sizeof(data); i++) {
        if (i == 10 || i == 0x19) continue;
        data[i] ^= 0xff;
        rom_info_discriminator_decode(data, 38, &branch);
        assert(memcmp(&baseline, &branch, sizeof(branch)) == 0);
    }
    for (size_t length = 0; length <= sizeof(data); length++) {
        if (length == 38) continue;
        memset(&branch, 0xff, sizeof(branch));
        assert(strcmp(rom_info_discriminator_decode(data, length, &branch),
                      "unexpected_length") == 0);
        assert(memcmp(&branch, &branch_zero, sizeof(branch)) == 0);
    }
    data[10] = 5;
    rom_info_discriminator_decode(data, 38, &branch);
    assert(branch.derived_value == 0);
    for (int i = 0; i < 2; i++) {
        data[i] = 1;
        assert(strcmp(rom_info_discriminator_decode(data, 38, &branch),
                      "device_status_nonzero") == 0);
        assert(memcmp(&branch, &branch_zero, sizeof(branch)) == 0);
        data[i] = 0;
    }
    assert(strcmp(rom_info_discriminator_decode(NULL, 38, &branch), "unexpected_length") == 0);
    assert(memcmp(&branch, &branch_zero, sizeof(branch)) == 0);
    assert(strcmp(rom_info_discriminator_decode(data, 38, NULL), "invalid_argument") == 0);
    return 0;
}
