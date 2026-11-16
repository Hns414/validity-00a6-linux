/* SPDX-License-Identifier: LGPL-2.1-or-later */
#ifndef VALIDITY_ROM_INFO_H
#define VALIDITY_ROM_INFO_H
#include <stddef.h>
#include <stdint.h>

struct rom_info_candidate {
    uint32_t firmware_build;
    unsigned int firmware_major;
    unsigned int firmware_minor;
    unsigned int product_code;
};
/* Hypothesis from the pinned python-validity RomInfo layout. Not a 00a6 spec.
 * Only four candidate shared metadata fields are extracted. No timestamp,
 * unknown fields, serials or trailing bytes are exported. */
const char *rom_info_decode(const unsigned char *data, size_t length,
                            struct rom_info_candidate *out);
struct rom_info_discriminator_candidate {
    unsigned int firmware_major;
    unsigned int flag_0x20_set;
    unsigned int derived_value;
};
/* Candidate mapping for the cleartext 38-byte E1 layout. Exports one bit,
 * never the complete internal flag byte. Does not perform full selection. */
const char *rom_info_discriminator_decode(const unsigned char *data, size_t length,
                             struct rom_info_discriminator_candidate *out);
#endif
