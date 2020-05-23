---
layout: plugin

id: ikea_tradfri
title: Ikea Tradfri
description: Control Ikea Tradfri outlet
author: Mathieu "ralmn" HIREL
license: AGPLv3

date: 2019-08-18

homepage: https://github.com/ralmn/OctoPrint-Ikea-tradfri
source: https://github.com/ralmn/OctoPrint-Ikea-tradfri
archive: https://github.com/ralmn/OctoPrint-Ikea-tradfri/archive/master.zip

# TODO
# Set this to true if your plugin uses the dependency_links setup parameter to include
# library versions not yet published on PyPi. SHOULD ONLY BE USED IF THERE IS NO OTHER OPTION!
#follow_dependency_links: false

tags:
- ikea
- tradfri
- outlet

# TODO
screenshots:
- url: /assets/img/plugins/ikea_tradfri/navbar.png
  alt: Navbar of plugin
  caption: Navbar of plugin
- url: /assets/img/plugins/ikea_tradfri/settings.png
  alt: Settings of plugin
  caption: Settings of plugin

featuredimage: /assets/img/plugins/ikea_tradfri/navbar.png

# You only need the following if your plugin requires specific OctoPrint versions or
# specific operating systems to function - you can safely remove the whole
# "compatibility" block if this is not the case.

compatibility:

  # List of compatible versions
  #
  # A single version number will be interpretated as a minimum version requirement,
  # e.g. "1.3.1" will show the plugin as compatible to OctoPrint versions 1.3.1 and up.
  # More sophisticated version requirements can be modelled too by using PEP440
  # compatible version specifiers.
  #
  # You can also remove the whole "octoprint" block. Removing it will default to all
  # OctoPrint versions being supported.

  octoprint:
  - 1.3.1
  - 1.4.0

  # List of compatible operating systems
  #
  # Valid values:
  #
  # - windows
  # - linux
  # - macos
  # - freebsd
  #
  # There are also two OS groups defined that get expanded on usage:
  #
  # - posix: linux, macos and freebsd
  # - nix: linux and freebsd
  #
  # You can also remove the whole "os" block. Removing it will default to all
  # operating systems being supported.

  os:
  - linux
  - windows
  - macos
  - freebsd

---

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
    ./configure --disable-documentation --disable-shared
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
