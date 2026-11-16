/* SPDX-License-Identifier: LGPL-2.1-or-later
 * Link-time USB simulator: never links to libusb or touches USB devices.
 */
#define _POSIX_C_SOURCE 200809L
#include <libusb.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static int64_t millis;
static struct libusb_transfer *pending;
static int cancelled;
static int events;
static int scenario(const char *s) {
    const char *value = getenv("FAKE_SCENARIO");
    return value && strcmp(s, value) == 0;
}
static void trace(const char *s) {
    const char *path = getenv("FAKE_TRACE");
    if (!path) return;
    FILE *f = fopen(path, "a");
    if (!f) abort();
    fprintf(f, "%s\n", s);
    fclose(f);
}
int fake_clock_gettime(clockid_t id, struct timespec *ts) {
    (void)id;
    ts->tv_sec = millis / 1000;
    ts->tv_nsec = (millis % 1000) * 1000000;
    return 0;
}
int LIBUSB_CALL libusb_init(libusb_context **ctx) {
    trace("init");
    *ctx = (libusb_context *)(uintptr_t)1;
    return scenario("init_error") ? LIBUSB_ERROR_OTHER : 0;
}
void LIBUSB_CALL libusb_exit(libusb_context *ctx) { (void)ctx; trace("exit"); }
ssize_t LIBUSB_CALL libusb_get_device_list(libusb_context *ctx, libusb_device ***list) {
    static libusb_device *items[] = {(libusb_device *)(uintptr_t)2, (libusb_device *)(uintptr_t)3, NULL};
    (void)ctx; *list = items;
    trace("enumerate");
    return scenario("no_target") ? 0 : scenario("multiple") ? 2 : 1;
}
void LIBUSB_CALL libusb_free_device_list(libusb_device **list, int unref) {
    (void)list; (void)unref; trace("free_list");
}
int LIBUSB_CALL libusb_get_device_descriptor(libusb_device *dev, struct libusb_device_descriptor *d) {
    (void)dev;
    memset(d, 0, sizeof(*d));
    d->idVendor = 0x138a; d->idProduct = 0x00a6;
    d->bcdDevice = scenario("wrong_revision") ? 0x0100 : 0x0164;
    d->bcdUSB = 0x0200; d->bDeviceClass = 0xff; d->bDeviceSubClass = 0x10;
    d->bDeviceProtocol = 0xff; d->bNumConfigurations = 1;
    return 0;
}
int LIBUSB_CALL libusb_get_device_speed(libusb_device *dev) { (void)dev; return LIBUSB_SPEED_FULL; }
int LIBUSB_CALL libusb_get_active_config_descriptor(libusb_device *dev, struct libusb_config_descriptor **cfg) {
    static struct libusb_endpoint_descriptor eps[5];
    static struct libusb_interface_descriptor alt;
    static struct libusb_interface iface;
    static struct libusb_config_descriptor config;
    const unsigned char addresses[] = {1, 0x81, 0x82, 0x83, 0x84};
    const uint16_t sizes[] = {64, 64, 64, 8, 16};
    (void)dev;
    for (int i = 0; i < 5; i++) {
        eps[i].bEndpointAddress = addresses[i]; eps[i].bmAttributes = i < 3 ? 2 : 3;
        eps[i].wMaxPacketSize = sizes[i];
    }
    if (scenario("wrong_endpoint")) eps[4].bEndpointAddress = 0x85;
    if (scenario("wrong_type")) eps[0].bmAttributes = 3;
    if (scenario("duplicate_endpoint")) eps[4].bEndpointAddress = 0x83;
    alt.bInterfaceClass = 0xff; alt.bNumEndpoints = 5; alt.endpoint = eps;
    iface.num_altsetting = 1; iface.altsetting = &alt;
    config.bConfigurationValue = 1; config.bNumInterfaces = 1; config.interface = &iface;
    *cfg = &config;
    return 0;
}
void LIBUSB_CALL libusb_free_config_descriptor(struct libusb_config_descriptor *cfg) { (void)cfg; trace("free_config"); }
int LIBUSB_CALL libusb_open(libusb_device *dev, libusb_device_handle **handle) {
    (void)dev; trace("open");
    if (scenario("permission")) return LIBUSB_ERROR_ACCESS;
    *handle = (libusb_device_handle *)(uintptr_t)4; return 0;
}
void LIBUSB_CALL libusb_close(libusb_device_handle *handle) { (void)handle; trace("close"); }
int LIBUSB_CALL libusb_kernel_driver_active(libusb_device_handle *handle, int iface) {
    (void)handle; (void)iface; return scenario("busy") ? 1 : 0;
}
int LIBUSB_CALL libusb_claim_interface(libusb_device_handle *handle, int iface) {
    (void)handle; (void)iface; trace("claim");
    return scenario("claim_busy") ? LIBUSB_ERROR_BUSY : 0;
}
int LIBUSB_CALL libusb_release_interface(libusb_device_handle *handle, int iface) {
    (void)handle; (void)iface; trace("release");
    return scenario("release_error") ? LIBUSB_ERROR_OTHER : 0;
}
struct libusb_transfer *LIBUSB_CALL libusb_alloc_transfer(int count) {
    (void)count;
    return calloc(1, sizeof(struct libusb_transfer));
}
void LIBUSB_CALL libusb_free_transfer(struct libusb_transfer *t) { trace("free_transfer"); free(t); }
int LIBUSB_CALL libusb_submit_transfer(struct libusb_transfer *t) {
    if (t->type != LIBUSB_TRANSFER_TYPE_BULK || t->timeout == 0 || t->timeout > 1000) abort();
    if (t->endpoint == 1) {
        if (t->length != 1 || t->buffer[0] != 1) abort();
        trace("write_01");
    } else if (t->endpoint == 0x81 && t->length == 64) trace("read_64");
    else abort();
    if (scenario("submit_error")) return LIBUSB_ERROR_IO;
    pending = t; cancelled = 0; events = 0;
    return 0;
}
int LIBUSB_CALL libusb_cancel_transfer(struct libusb_transfer *t) {
    if (t != pending) abort();
    trace("cancel"); cancelled = 1; return 0;
}
int LIBUSB_CALL libusb_handle_events_timeout_completed(libusb_context *ctx, struct timeval *tv, int *done) {
    (void)ctx; (void)tv; (void)done;
    if (!pending) abort();
    millis += 100;
    events++;
    if ((scenario("cancel_write") && pending->endpoint == 1) ||
        (scenario("cancel_read") && pending->endpoint == 0x81)) {
        if (events == 1) { raise(SIGINT); return 0; }
    }
    if (scenario("stuck")) return 0;
    if (scenario("hang_write") && pending->endpoint == 1 && !cancelled) return 0;
    if (scenario("event_error") && events == 1) return LIBUSB_ERROR_IO;
    struct libusb_transfer *t = pending;
    t->status = LIBUSB_TRANSFER_COMPLETED;
    t->actual_length = t->endpoint == 1 ? 1 : 38;
    if (t->endpoint == 0x81) {
        memset(t->buffer, 0xa5, 64); /* timestamp, padding and tail must remain private */
        t->buffer[0] = 0; t->buffer[1] = 0;
        t->buffer[6] = 0x78; t->buffer[7] = 0x56; t->buffer[8] = 0x34; t->buffer[9] = 0x12;
        t->buffer[10] = 6; t->buffer[11] = 7; t->buffer[13] = 0x30;
        if (scenario("summary_error")) t->buffer[1] = 1;
        if (scenario("summary_short")) t->actual_length = 17;
        if (scenario("summary_long")) t->actual_length = 39;
    }
    if (scenario("short_write") && t->endpoint == 1) t->actual_length = 0;
    if (scenario("empty_read") && t->endpoint == 0x81) t->actual_length = 0;
    if (scenario("overflow") && t->endpoint == 0x81) t->actual_length = 65;
    if (scenario("read_timeout") && t->endpoint == 0x81) t->status = LIBUSB_TRANSFER_TIMED_OUT;
    if (scenario("write_timeout") && t->endpoint == 1) t->status = LIBUSB_TRANSFER_TIMED_OUT;
    if (scenario("disconnect") && t->endpoint == 0x81) t->status = LIBUSB_TRANSFER_NO_DEVICE;
    if (scenario("late_completion")) millis += 3000;
    if (cancelled) t->status = LIBUSB_TRANSFER_CANCELLED;
    pending = NULL;
    t->callback(t);
    return 0;
}
