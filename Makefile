CC = cc
CFLAGS = -O2 -g -std=c11 -Wall -Wextra -Werror
USB_CFLAGS = $(shell pkg-config --cflags libusb-1.0)
USB_LIBS = $(shell pkg-config --libs libusb-1.0)

.PHONY: probe test clean
probe: build/probe-rom-info

build/probe-rom-info: src/probe_rom_info.c
	mkdir -p build
	$(CC) $(CFLAGS) $(USB_CFLAGS) $< -o $@ $(USB_LIBS)

test:
	python3 -m unittest discover -s tests -v

clean:
	rm -rf build
