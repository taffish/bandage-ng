# syntax=docker/dockerfile:1.7

# Fixed base/source digests detect content changes, not permanent availability.
# Debian's live APT repositories below can change dependency versions or retire
# packages. On failure, re-check the official repository and create a successor;
# do not silently replace digests or claim a permanently reproducible snapshot.
# The official AppImage and noVNC/websockify tag archives have the same retention
# boundary. Verify any newly obtained bytes before changing a pinned checksum.

ARG BANDAGENG_IMAGE_PLATFORM=linux/amd64
ARG DEBIAN_IMAGE=debian:13-slim@sha256:abc9cb88a5587630d7f915f47b23b0668fe250fbfc6457aa4d52b534c1bbf73f

FROM --platform=$BANDAGENG_IMAGE_PLATFORM ${DEBIAN_IMAGE} AS novnc

ENV DEBIAN_FRONTEND=noninteractive

ARG NOVNC_VERSION=1.7.0
ARG NOVNC_SOURCE_SHA256=b1003a11b6e6e8d8f7f5e5586daae7f8ca651d8aee0aa155ff9ac841c48f52c6
ARG WEBSOCKIFY_VERSION=0.13.0
ARG WEBSOCKIFY_SOURCE_SHA256=b6413e364efd04f3c92ec8c17747e3c4adc20157c2ef1c5d019a26d944a46df8

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked set -eux; \
    rm -f /etc/apt/apt.conf.d/docker-clean; \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache; \
    for i in 1 2 3 4 5; do \
      rm -rf /var/lib/apt/lists/*; \
      apt-get -o Acquire::Retries=5 -o Acquire::http::No-Cache=true update \
      && apt-get -o Acquire::Retries=5 -o Acquire::http::No-Cache=true install -y --no-install-recommends \
        ca-certificates \
        curl \
      && break; \
      if [ "$i" = "5" ]; then exit 1; fi; \
      sleep $((i * 5)); \
    done; \
    rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    curl --http1.1 -fL --retry 5 --retry-delay 5 --retry-all-errors -o /tmp/novnc.tar.gz "https://github.com/novnc/noVNC/archive/refs/tags/v${NOVNC_VERSION}.tar.gz"; \
    echo "${NOVNC_SOURCE_SHA256}  /tmp/novnc.tar.gz" | sha256sum -c -; \
    curl --http1.1 -fL --retry 5 --retry-delay 5 --retry-all-errors -o /tmp/websockify.tar.gz "https://github.com/novnc/websockify/archive/refs/tags/v${WEBSOCKIFY_VERSION}.tar.gz"; \
    echo "${WEBSOCKIFY_SOURCE_SHA256}  /tmp/websockify.tar.gz" | sha256sum -c -; \
    mkdir -p /opt; \
    tar -xzf /tmp/novnc.tar.gz -C /opt; \
    mv "/opt/noVNC-${NOVNC_VERSION}" /opt/noVNC; \
    tar -xzf /tmp/websockify.tar.gz -C /opt; \
    mv "/opt/websockify-${WEBSOCKIFY_VERSION}" /opt/websockify; \
    rm -f /tmp/novnc.tar.gz /tmp/websockify.tar.gz

FROM --platform=$BANDAGENG_IMAGE_PLATFORM ${DEBIAN_IMAGE} AS bandage

ENV DEBIAN_FRONTEND=noninteractive

ARG BANDAGENG_VERSION=2026.10.1
ARG BANDAGENG_UPSTREAM_COMMIT=4ac44b0cecbc056a212e8d65d27e3fcf4c0ebbc7
ARG BANDAGENG_APPIMAGE_COMMIT=4ac44b0
ARG BANDAGENG_APPIMAGE_SHA256=8db0a2f0ee7c1fadd8c76b88ea41be721116b94a30d9ecc9ed6c091e5ebb608a
ARG BANDAGENG_APPIMAGE_SQUASHFS_OFFSET=944632
ARG BANDAGENG_COPYING_SHA256=8ceb4b9ee5adedde47b31e975c1d90c73ad27b6b165a1dcd80c7c545eb65b903

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked set -eux; \
    rm -f /etc/apt/apt.conf.d/docker-clean; \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache; \
    for i in 1 2 3 4 5; do \
      rm -rf /var/lib/apt/lists/*; \
      apt-get -o Acquire::Retries=5 -o Acquire::http::No-Cache=true update \
      && apt-get -o Acquire::Retries=5 -o Acquire::http::No-Cache=true install -y --no-install-recommends \
        ca-certificates \
        curl \
        squashfs-tools \
      && break; \
      if [ "$i" = "5" ]; then exit 1; fi; \
      sleep $((i * 5)); \
    done; \
    rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    curl --http1.1 -fL --retry 5 --retry-delay 5 --retry-all-errors \
      -o /tmp/BandageNG.AppImage \
      "https://github.com/asl/BandageNG/releases/download/v${BANDAGENG_VERSION}/BandageNG-Linux-${BANDAGENG_APPIMAGE_COMMIT}.AppImage"; \
    echo "${BANDAGENG_APPIMAGE_SHA256}  /tmp/BandageNG.AppImage" | sha256sum -c -; \
    curl --http1.1 -fL --retry 5 --retry-delay 5 --retry-all-errors \
      -o /tmp/BandageNG-COPYING \
      "https://raw.githubusercontent.com/asl/BandageNG/${BANDAGENG_UPSTREAM_COMMIT}/COPYING"; \
    echo "${BANDAGENG_COPYING_SHA256}  /tmp/BandageNG-COPYING" | sha256sum -c -; \
    mkdir -p /opt/bandage-ng; \
    unsquashfs -q -f -d /opt/bandage-ng -o "${BANDAGENG_APPIMAGE_SQUASHFS_OFFSET}" /tmp/BandageNG.AppImage; \
    install -Dm0644 /tmp/BandageNG-COPYING /opt/bandage-ng/TAFFISH-UPSTREAM-COPYING; \
    printf '%s\n' \
      "upstream_tag=v${BANDAGENG_VERSION}" \
      "upstream_commit=${BANDAGENG_UPSTREAM_COMMIT}" \
      "asset=BandageNG-Linux-${BANDAGENG_APPIMAGE_COMMIT}.AppImage" \
      "asset_sha256=${BANDAGENG_APPIMAGE_SHA256}" \
      "appimage_squashfs_offset=${BANDAGENG_APPIMAGE_SQUASHFS_OFFSET}" \
      > /opt/bandage-ng/TAFFISH-SOURCE.txt; \
    rm -f /tmp/BandageNG.AppImage /tmp/BandageNG-COPYING

FROM --platform=$BANDAGENG_IMAGE_PLATFORM ${DEBIAN_IMAGE}

ENV DEBIAN_FRONTEND=noninteractive

COPY --from=bandage /opt/bandage-ng/ /opt/bandage-ng/

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked set -eux; \
    printf '%s\n' '#!/bin/sh' 'exec /opt/bandage-ng/AppRun "$@"' > /usr/local/bin/BandageNG; \
    rm -f /etc/apt/apt.conf.d/docker-clean; \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache; \
    for i in 1 2 3 4 5; do \
      rm -rf /var/lib/apt/lists/*; \
      apt-get -o Acquire::Retries=5 -o Acquire::http::No-Cache=true update \
      && apt-get -o Acquire::Retries=5 -o Acquire::http::No-Cache=true install -y --no-install-recommends \
        ca-certificates \
        curl \
        dbus-x11 \
        fonts-dejavu-core \
        hmmer \
        libegl1 \
        libgl1 \
        libglib2.0-0 \
        libnss3 \
        libopengl0 \
        libx11-6 \
        libxkbcommon-x11-0 \
        libxcb-cursor0 \
        minimap2 \
        ncbi-blast+ \
        procps \
        python3-minimal \
        twm \
        x11vnc \
        x11-utils \
        xauth \
        xdotool \
        xvfb \
      && break; \
      if [ "$i" = "5" ]; then exit 1; fi; \
      sleep $((i * 5)); \
    done; \
    rm -rf /var/lib/apt/lists/*

COPY --from=novnc /opt/noVNC/ /opt/noVNC/
COPY --from=novnc /opt/websockify/ /opt/websockify/
COPY docker/bandage-ng /usr/local/bin/bandage-ng
COPY docker/bandage-ng-gui /usr/local/bin/bandage-ng-gui
COPY docker/bandage-ng-smoke /usr/local/bin/bandage-ng-smoke
COPY docker/rfb-probe.py /usr/local/libexec/bandage-ng/rfb-probe.py
COPY docker/session-contract.py /usr/local/libexec/bandage-ng/session-contract.py

RUN set -eux; \
    printf '%s\n' '#!/bin/sh' 'exec /opt/websockify/run "$@"' > /usr/local/bin/websockify; \
    chmod +x /opt/bandage-ng/AppRun /opt/websockify/run /usr/local/bin/BandageNG /usr/local/bin/bandage-ng /usr/local/bin/bandage-ng-gui /usr/local/bin/bandage-ng-smoke /usr/local/bin/websockify; \
    command -v BandageNG; \
    command -v bandage-ng; \
    command -v bandage-ng-gui; \
    command -v bandage-ng-smoke; \
    command -v Xvfb; \
    command -v x11vnc; \
    command -v websockify; \
    command -v twm; \
    command -v xdotool; \
    command -v makeblastdb; \
    command -v blastn; \
    command -v tblastn; \
    command -v minimap2; \
    command -v nhmmer; \
    command -v hmmsearch; \
    bandage-ng-smoke buildtime

WORKDIR /root

ENV BANDAGENG_VERSION=2026.10.1
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV QT_XKB_CONFIG_ROOT=/usr/share/X11/xkb
ENV TAFFISH_ENV=TAFFISH
ENV TAFFISH_NAME=bandage-ng
