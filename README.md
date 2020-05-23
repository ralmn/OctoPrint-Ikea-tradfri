# OctoPrint-Ikea-tradfri

Turn on your printer with Ikea Tradfri Outlet.

## Requierements

1. [Ikea Tradfri Gateway](https://www.ikea.com/us/en/catalog/products/00337813/)
2. [Ikea Tradfri Outlet](https://www.ikea.com/us/en/catalog/products/30356169/)

## Setup

## Install libcoap

You need libcoap for communicate with your Ikea Gateway.

    git clone --recursive https://github.com/obgm/libcoap.git
    cd libcoap
    git checkout dtls
    git submodule update --init --recursive
    ./autogen.sh
    ./configure --disable-documentation --disable-shared --without-debug CFLAGS="-D COAP_DEBUG_FD=stderr"
    make
    make install

## Install plugin

Install manually using this URL:

    https://github.com/ralmn/OctoPrint-Ikea-tradfri/archive/master.zip


## Configuration

1. Indicate your gateway ip and your security code (found under your gateway)
2. Save
3. Select your outlet
4. Save



