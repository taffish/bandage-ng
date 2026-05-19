# taf-bandage-ng

TAFFISH wrapper for [BandageNG](https://github.com/asl/BandageNG), a modern
fork of Bandage for interactive visualization and inspection of de novo
assembly graphs.

BandageNG is mainly a GUI application for GFA/FASTG assembly graphs, but it
also provides headless command-line subcommands for graph information, layout,
image rendering, graph reduction, and path queries. This TAFFISH app packages
both surfaces:

- `bandage-ng-gui`: a browser-accessible noVNC GUI session for normal TAFFISH
  interactive use.
- `bandage-ng`: a direct launcher for upstream `BandageNG`, with a clearer
  no-display diagnostic and support for headless CLI subcommands.
- `BandageNG`: the upstream binary, still available through command mode.

The image also includes BLAST+, minimap2, and HMMER because BandageNG can use
external search programs for graph search workflows from the GUI.

## Installation

Install from the public TAFFISH Hub index:

```sh
taf update
taf install bandage-ng
```

Install the exact release:

```sh
taf install bandage-ng 2026.4.1-r1
```

For local testing before the app is published to the public index:

```sh
taf install --from .
```

## Usage

Show TAFFISH app help:

```sh
taf-bandage-ng --help
```

Show the TAFFISH package version:

```sh
taf-bandage-ng --version
```

Start BandageNG GUI through Docker and noVNC:

```sh
TAFFISH_CONTAINER_BACKEND=docker \
TAFFISH_DOCKER_RUN_ARGS="-p 127.0.0.1:5801:5801" \
taf-bandage-ng bandage-ng-gui
```

Then open:

```text
http://127.0.0.1:5801/vnc.html?autoconnect=1&resize=scale
```

The helper prints this URL at startup, plus an SSH tunnel example for remote
servers.

Podman uses the same idea with the Podman run-args variable:

```sh
TAFFISH_CONTAINER_BACKEND=podman \
TAFFISH_PODMAN_RUN_ARGS="-p 127.0.0.1:5801:5801" \
taf-bandage-ng bandage-ng-gui
```

Use another host port if `5801` is already occupied:

```sh
TAFFISH_DOCKER_RUN_ARGS="-p 127.0.0.1:5802:5801" \
taf-bandage-ng bandage-ng-gui --host-port 5802
```

For a remote server:

```sh
ssh -L 5801:127.0.0.1:5801 user@server
```

Then open the same localhost URL in your local browser.

## GUI Options

The GUI helper creates an Xvfb display, starts Openbox and x11vnc, exposes it
through noVNC, then launches BandageNG.

Useful options:

```sh
taf-bandage-ng bandage-ng-gui --help
taf-bandage-ng bandage-ng-gui --geometry 1440x900
taf-bandage-ng bandage-ng-gui --password 'choose-a-password'
```

Pass extra BandageNG arguments after `--`:

```sh
taf-bandage-ng bandage-ng-gui -- graph.gfa
taf-bandage-ng bandage-ng-gui -- --help
```

The direct launcher is also available:

```sh
taf-bandage-ng bandage-ng --version
taf-bandage-ng -- --help
```

Running `bandage-ng` without a headless subcommand starts the desktop GUI and
requires an X display. For normal TAFFISH use, `taf-bandage-ng bandage-ng-gui`
is the recommended entry point.

## Headless CLI

BandageNG includes several command-line subcommands. Use command mode to call
the packaged launcher explicitly:

```sh
taf-bandage-ng bandage-ng info graph.gfa
taf-bandage-ng bandage-ng image graph.gfa graph.svg
taf-bandage-ng bandage-ng reduce graph.gfa reduced.gfa
taf-bandage-ng bandage-ng layout graph.gfa layout.csv
taf-bandage-ng bandage-ng querypaths graph.gfa queries.fasta
```

For option-leading upstream arguments, use `--`:

```sh
taf-bandage-ng -- --version
taf-bandage-ng -- --help
```

Because this is a normal taf-app with command mode enabled, other executables in
the same container can also be called explicitly:

```sh
taf-bandage-ng makeblastdb -version
taf-bandage-ng minimap2 --version
taf-bandage-ng hmmsearch -h
```

## Package

```text
name: bandage-ng
command: taf-bandage-ng
version: 2026.4.1-r1
kind: tool
image: ghcr.io/taffish/bandage-ng:2026.4.1-r1
upstream: BandageNG v2026.4.1
runtime version: BandageNG 2026.4.1
upstream binary: BandageNG-Linux-2aefa98.AppImage
native platform: linux/amd64
```

## Container

The container image is built from `docker/Dockerfile`. It starts from
`debian:13-slim`, downloads the official upstream
`BandageNG-Linux-2aefa98.AppImage` asset from the `v2026.4.1` release, verifies
its SHA-256 checksum, and extracts it into `/opt/bandage-ng`. This keeps the
packaged runtime aligned with the upstream Linux binary release instead of
rebuilding the Qt application from source inside TAFFISH.

Debian 12 is not sufficient for this upstream AppImage after extraction because
the packaged runtime expects newer `glibc`/`libstdc++` symbols such as
`GLIBC_2.38` and `GLIBCXX_3.4.32`.

It provides:

```text
BandageNG
bandage-ng
bandage-ng-gui
makeblastdb / blastn / tblastn
minimap2
nhmmer / hmmsearch
Xvfb
openbox
x11vnc
websockify/noVNC
```

The image is built and validated for:

```text
linux/amd64
```

The upstream Linux AppImage is an amd64 binary. On arm64 Docker/Podman hosts,
including Apple Silicon machines, the `<taf-app:...>` entry requests
`--platform linux/amd64` so the same app can run through Docker/Podman amd64
emulation. This is a compatibility path, not native `linux/arm64` support.

The `<taf-app:...>` entry also embeds `--init` for Docker and Podman so
long-running GUI sessions receive signals and clean up child processes more
reliably.

## Security And Ports

The documented examples bind the host port to `127.0.0.1`, not all network
interfaces. This is the safest default for local work and SSH tunneling.

By default the VNC session has no password because it is expected to be exposed
only on localhost. On shared machines or exposed network paths, use:

```sh
taf-bandage-ng bandage-ng-gui --password 'choose-a-password'
```

noVNC is served over plain HTTP inside the container. If a site needs TLS,
authentication, or external network exposure, put those controls outside the
container at the site level.

## Boundaries

This app packages BandageNG itself plus the external BLAST+, minimap2, and
HMMER commands that BandageNG can use for graph search features. It does not
download assembly graphs, references, read data, or workflow-specific databases
for the user.

The GUI path is intended for interactive inspection and visualization. Headless
CLI subcommands are useful for reproducible graph summaries and rendered images,
but full visual interpretation still requires representative user data and
manual review.

Apptainer GUI/noVNC behavior is site-dependent because port, network, and X/VNC
policies vary across clusters.

## Upstream

- Project: BandageNG
- Source: <https://github.com/asl/BandageNG>
- Release: <https://github.com/asl/BandageNG/releases/tag/v2026.4.1>
- Documentation: <https://github.com/asl/BandageNG/wiki>
- License: GPL-3.0-or-later
- Citation: upstream currently lists the BandageNG citation as TBD; for the
  original Bandage publication, see Wick et al. 2015, Bioinformatics
- Original Bandage DOI: <https://doi.org/10.1093/bioinformatics/btv383>
- Original Bandage PMID: 26099265
