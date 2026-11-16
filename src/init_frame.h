/* SPDX-License-Identifier: LGPL-2.1-or-later */
#ifndef VALIDITY_INIT_FRAME_H
#define VALIDITY_INIT_FRAME_H
#include <stddef.h>
#include <stdint.h>
/* Offline research only. Not linked into the active USB probe.
 * Frames exactly 500 arguments behind opcode 0x06, without interpreting them.
 * Returns 501 on success, 0 on invalid input. Output unchanged on failure.
 * Overlapping argument/output ranges are supported. */
int validity_encode_init_frame(const uint8_t *arguments, size_t length,
                               uint8_t *output, size_t capacity);
#endif
