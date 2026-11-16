/* SPDX-License-Identifier: LGPL-2.1-or-later
 * Experimental 00a6 single-query probe. No reset, configuration change or retry.
 * See docs/lab.md. Response semantics remain unvalidated for this device.
 */
#define _POSIX_C_SOURCE 200809L
#include <libusb.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "rom_info.h"
#include "status_reply.h"

static int summarize_requested;
static int discriminator_requested;
static struct rom_info_discriminator_candidate discriminator_candidate;
static int cmd19_requested;
static int cmd19_reply_observed;
static int cmd19_has_status;
static int cmd19_status_zero;
static struct rom_info_candidate candidate;
static const char *decode_status = "not_attempted";

static volatile sig_atomic_t interrupted;
static void on_signal(int signo) { (void)signo; interrupted = 1; }

static int64_t now_ms(void)
{
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0) return -1;
    return (int64_t)ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}

static void report(const char *status, const char *stage, int bytes)
{
    /* No raw response, serial, host/user identity, USB path or library error text. */
    printf("{\"schema_version\":%d,\"experiment\":\"%s\",\"status\":\"%s\","
           "\"stage\":\"%s\",\"received_bytes\":%d,\"biometric_support\":false",
           discriminator_requested ? 4 : cmd19_requested ? 3 : summarize_requested ? 2 : 1,
           cmd19_requested ? "E2" : "E1", status, stage, bytes);
    if (summarize_requested) {
        printf(",\"decode_status\":\"%s\",\"rom_info_candidate\":", decode_status);
        if (strcmp(decode_status, "candidate_layout_unverified") == 0)
            printf("{\"firmware_build\":%u,\"firmware_major\":%u,"
                   "\"firmware_minor\":%u,\"product_code\":%u}",
                   (unsigned int)candidate.firmware_build, candidate.firmware_major,
                   candidate.firmware_minor, candidate.product_code);
        else printf("null");
    }
    if (discriminator_requested) {
        printf(",\"decode_status\":\"%s\",\"discriminator_candidate\":", decode_status);
        if (strcmp(decode_status, "candidate_layout_unverified") == 0)
            printf("{\"firmware_major\":%u,\"flag_0x20_set\":%s,\"derived_value\":%u}",
                   discriminator_candidate.firmware_major,
                   discriminator_candidate.flag_0x20_set ? "true" : "false",
                   discriminator_candidate.derived_value);
        else printf("null");
        printf(",\"full_selection_evaluated\":false");
    }
    if (cmd19_requested) {
        printf(",\"command\":\"0x19\",\"candidate_status_zero\":%s,"
               "\"reference_length_bytes\":68,\"reference_length_match\":%s",
               cmd19_has_status ? (cmd19_status_zero ? "true" : "false") : "null",
               cmd19_reply_observed ? (bytes == 68 ? "true" : "false") : "null");
    }
    puts("}");
}

static int valid_config(const struct libusb_config_descriptor *cfg)
{
    static const unsigned char address[] = {0x01, 0x81, 0x82, 0x83, 0x84};
    static const unsigned char type[] = {2, 2, 2, 3, 3};
    static const uint16_t packet[] = {64, 64, 64, 8, 16};
    unsigned int seen = 0;
    if (cfg->bConfigurationValue != 1 || cfg->bNumInterfaces != 1 || !cfg->interface)
        return 0;
    const struct libusb_interface *iface = &cfg->interface[0];
    if (iface->num_altsetting != 1 || !iface->altsetting) return 0;
    const struct libusb_interface_descriptor *alt = &iface->altsetting[0];
    if (alt->bInterfaceNumber != 0 || alt->bAlternateSetting != 0 ||
        alt->bInterfaceClass != 0xff || alt->bInterfaceSubClass != 0 ||
        alt->bInterfaceProtocol != 0 || alt->bNumEndpoints != 5 || !alt->endpoint)
        return 0;
    for (int i = 0; i < 5; i++) {
        const struct libusb_endpoint_descriptor *ep = &alt->endpoint[i];
        int found = 0;
        for (int j = 0; j < 5; j++) {
            if (ep->bEndpointAddress != address[j]) continue;
            if ((seen & (1u << j)) || (ep->bmAttributes & 3) != type[j] ||
                ep->wMaxPacketSize != packet[j]) return 0;
            seen |= 1u << j;
            found = 1;
        }
        if (!found) return 0;
    }
    return seen == 31;
}

struct pending { int done; enum libusb_transfer_status status; int actual; };
static void LIBUSB_CALL complete(struct libusb_transfer *transfer)
{
    struct pending *p = transfer->user_data;
    p->status = transfer->status;
    p->actual = transfer->actual_length;
    p->done = 1;
}

/* The libusb callback owns completion: never free an in-flight transfer. */
static const char *exchange(libusb_context *ctx, libusb_device_handle *handle,
                            unsigned char endpoint, unsigned char *data, int length,
                            int64_t deadline, int *actual)
{
    struct pending p = {0};
    int64_t start = now_ms();
    if (start < 0) return "clock_error";
    if (interrupted) return "cancelled";
    int64_t remaining = deadline - start;
    if (remaining <= 0) return "deadline";
    unsigned int timeout = remaining < 1000 ? (unsigned int)remaining : 1000;
    struct libusb_transfer *t = libusb_alloc_transfer(0);
    if (!t) return "allocation_error";
    libusb_fill_bulk_transfer(t, handle, endpoint, data, length, complete, &p, timeout);
    if (libusb_submit_transfer(t) != 0) {
        libusb_free_transfer(t);
        return "submit_error";
    }
    int cancelling = 0;
    int64_t cancel_start = 0;
    const char *abort_reason = NULL;
    while (!p.done) {
        int64_t current = now_ms();
        if (!cancelling && (interrupted || current < 0 || current >= deadline ||
                            current - start >= timeout)) {
            abort_reason = interrupted ? "cancelled" :
                current < 0 ? "clock_error" : current >= deadline ? "deadline" : "timeout";
            (void)libusb_cancel_transfer(t);
            cancelling = 1;
            cancel_start = current;
        }
        struct timeval wait = {0, 10000};
        int rc = libusb_handle_events_timeout_completed(ctx, &wait, &p.done);
        if (rc < 0 && rc != LIBUSB_ERROR_INTERRUPTED && !cancelling) {
            abort_reason = "event_error";
            (void)libusb_cancel_transfer(t);
            cancelling = 1;
            cancel_start = now_ms();
        }
        if (cancelling && !p.done) {
            current = now_ms();
            if (current < 0 || cancel_start < 0 || current - cancel_start >= 1000) {
                /* Completion could not be drained. Exit rather than free live buffers.
                 * OS process teardown closes resources; never reset the device. */
                report("cancel_drain_failed", endpoint == 1 ? "write" : "read", 0);
                fflush(stdout);
                _Exit(2);
            }
        }
    }
    libusb_free_transfer(t);
    if (!abort_reason) {
        int64_t completed_at = now_ms();
        if (completed_at < 0) abort_reason = "clock_error";
        else if (completed_at >= deadline) abort_reason = "deadline";
        else if (completed_at - start >= timeout) abort_reason = "timeout";
    }
    if (abort_reason) return abort_reason;
    if (interrupted) return "cancelled";
    if (p.status == LIBUSB_TRANSFER_TIMED_OUT) return "timeout";
    if (p.status == LIBUSB_TRANSFER_CANCELLED) return "cancelled";
    if (p.status == LIBUSB_TRANSFER_NO_DEVICE) return "disconnected";
    if (p.status != LIBUSB_TRANSFER_COMPLETED) return "transfer_error";
    if (p.actual < 0 || p.actual > length) return "invalid_length";
    if (endpoint == 1 && p.actual != length) return "short_write";
    *actual = p.actual;
    return NULL;
}

int main(int argc, char **argv)
{
    discriminator_requested = argc == 2 && strcmp(argv[1], "--summarize-init-discriminator") == 0;
    cmd19_requested = argc == 2 && strcmp(argv[1], "--probe-cmd19") == 0;
    summarize_requested = argc == 2 && strcmp(argv[1], "--summarize-rom-info") == 0;
    if (argc != 2 || (!discriminator_requested && !cmd19_requested && !summarize_requested && strcmp(argv[1], "--probe-rom-info") != 0)) {
        puts("Experimental 138a:00a6 probe. Read docs/lab.md before hardware use.\n"
             "Usage: probe-rom-info --probe-rom-info | --summarize-rom-info | --summarize-init-discriminator | --probe-cmd19\n"
             "Summary emits only candidate build/version/product metadata, never raw bytes.\n"
             "Discriminator summary emits major, one candidate flag bit and derived value; no payload selection.\n"
             "E1 sends 0x01, reads <=64 bytes. E2 sends only 0x19, reads <=128 bytes. No reset or subsequent initialization blocks.\n"
             "Response semantics are unvalidated. No USB access without the explicit flag.");
        return argc == 2 && strcmp(argv[1], "--help") == 0 ? 0 : 1;
    }
    struct sigaction action = {0};
    action.sa_handler = on_signal;
    sigemptyset(&action.sa_mask);
    if (sigaction(SIGINT, &action, NULL) || sigaction(SIGTERM, &action, NULL)) {
        report("signal_setup_error", "setup", 0);
        return 2;
    }
    libusb_context *ctx = NULL;
    libusb_device **list = NULL;
    libusb_device_handle *handle = NULL;
    struct libusb_config_descriptor *config = NULL;
    const char *status = "setup_error", *stage = "enumeration";
    int claimed = 0, received = 0, count = 0, index = -1;
    int rc = libusb_init(&ctx);
    if (rc != 0) { report("usb_unavailable", stage, 0); return 2; }
    ssize_t n = libusb_get_device_list(ctx, &list);
    if (n < 0) goto finish;
    for (ssize_t i = 0; i < n; i++) {
        struct libusb_device_descriptor desc;
        if (libusb_get_device_descriptor(list[i], &desc) != 0) {
            status = "descriptor_unavailable";
            goto finish;
        }
        if (desc.idVendor == 0x138a && desc.idProduct == 0x00a6) {
            count++; index = (int)i;
            if (desc.bcdDevice != 0x0164 || desc.bcdUSB != 0x0200 ||
                desc.bDeviceClass != 0xff || desc.bDeviceSubClass != 0x10 ||
                desc.bDeviceProtocol != 0xff || desc.bNumConfigurations != 1) {
                status = "unexpected_device_descriptor";
                goto finish;
            }
        }
    }
    if (count != 1) { status = count ? "ambiguous_target" : "target_not_found"; goto finish; }
    stage = "preflight";
    if (libusb_get_device_speed(list[index]) != LIBUSB_SPEED_FULL) {
        status = "unexpected_speed"; goto finish;
    }
    if (libusb_get_active_config_descriptor(list[index], &config) != 0 || !valid_config(config)) {
        status = "unexpected_configuration"; goto finish;
    }
    rc = libusb_open(list[index], &handle);
    if (rc != 0) { status = rc == LIBUSB_ERROR_ACCESS ? "permission_denied" : "open_error"; goto finish; }
    rc = libusb_kernel_driver_active(handle, 0);
    if (rc != 0) { status = rc > 0 ? "interface_busy" : "driver_state_error"; goto finish; }
    if (interrupted) { status = "cancelled"; goto finish; }
    rc = libusb_claim_interface(handle, 0);
    if (rc != 0) { status = rc == LIBUSB_ERROR_BUSY ? "interface_busy" : "claim_error"; goto finish; }
    claimed = 1;
    int64_t start = now_ms();
    if (start < 0) { status = "clock_error"; goto finish; }
    int64_t deadline = start + 3000;
    unsigned char query = cmd19_requested ? 0x19 : 0x01;
    unsigned char response[128] = {0};
    int receive_capacity = cmd19_requested ? 128 : 64;
    int written = 0;
    stage = "write";
    status = exchange(ctx, handle, 0x01, &query, 1, deadline, &written);
    if (status) goto finish;
    stage = "read";
    status = exchange(ctx, handle, 0x81, response, receive_capacity, deadline, &received);
    if (!status && cmd19_requested) {
        cmd19_reply_observed = 1;
        struct validity_status_reply header;
        if (validity_parse_status_reply(response, (size_t)received, &header)) {
            cmd19_has_status = 1;
            cmd19_status_zero = header.device_status == 0;
        }
    }
    if (!status && summarize_requested)
        decode_status = rom_info_decode(response, (size_t)received, &candidate);
    if (!status && discriminator_requested)
        decode_status = rom_info_discriminator_decode(response, (size_t)received,
                                                     &discriminator_candidate);
    /* Only allowlisted candidate fields may escape; never log raw response bytes. */
    memset(response, 0, sizeof(response));
    if (!status) status = received ? "reply_received_unvalidated" : "empty_reply";
finish:
    if (claimed && libusb_release_interface(handle, 0) != 0) {
        status = "release_error";
        decode_status = "not_attempted";
        cmd19_reply_observed = 0;
        cmd19_has_status = 0;
        memset(&candidate, 0, sizeof(candidate));
        memset(&discriminator_candidate, 0, sizeof(discriminator_candidate));
        stage = "cleanup";
    }
    if (handle) libusb_close(handle);
    if (config) libusb_free_config_descriptor(config);
    if (list) libusb_free_device_list(list, 1);
    libusb_exit(ctx);
    report(status, stage, received);
    return strcmp(status, "reply_received_unvalidated") == 0 ? 0 : 2;
}
