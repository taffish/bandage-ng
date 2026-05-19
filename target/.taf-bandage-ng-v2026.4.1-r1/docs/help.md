taf-bandage-ng 2026.4.1-r1

TAFFISH wrapper for BandageNG, a modern Bandage fork for interactive
visualization and inspection of GFA/FASTG de novo assembly graphs.

Modes:
  GUI mode       browser-accessible BandageNG through Xvfb, x11vnc, and noVNC
  CLI/headless   graph info, image, reduce, layout, and querypaths subcommands

Usage:
  taf-bandage-ng [TAF-APP-OPTION]
  taf-bandage-ng bandage-ng-gui [GUI-OPTIONS] [-- BANDAGENG-ARGS...]
  taf-bandage-ng bandage-ng [BANDAGENG-ARGS...]
  taf-bandage-ng BandageNG [BANDAGENG-ARGS...]
  taf-bandage-ng [IN-CONTAINER-COMMAND] [ARGS...]

TAF app options:
  -h, --help       Show this help text
  -v, --version    Show package and command version
  --compile        Print generated shell code instead of running it
  --               Stop parsing TAFFISH wrapper options

GUI mode:
  Docker:
    TAFFISH_CONTAINER_BACKEND=docker \
    TAFFISH_DOCKER_RUN_ARGS="-p 127.0.0.1:5801:5801" \
    taf-bandage-ng bandage-ng-gui

  Podman:
    TAFFISH_CONTAINER_BACKEND=podman \
    TAFFISH_PODMAN_RUN_ARGS="-p 127.0.0.1:5801:5801" \
    taf-bandage-ng bandage-ng-gui

  Open after startup:
    http://127.0.0.1:5801/vnc.html?autoconnect=1&resize=scale

  bandage-ng-gui also prints this URL when it starts.

  Alternate host port:
    TAFFISH_DOCKER_RUN_ARGS="-p 127.0.0.1:5802:5801" \
    taf-bandage-ng bandage-ng-gui --host-port 5802

  SSH tunnel:
    ssh -L 5801:127.0.0.1:5801 user@server

  Useful options:
    --geometry WxH, --port PORT, --host-port PORT, --password PASS

CLI/headless mode:
  taf-bandage-ng bandage-ng --version
  taf-bandage-ng bandage-ng --help
  taf-bandage-ng bandage-ng info graph.gfa
  taf-bandage-ng bandage-ng image graph.gfa graph.svg
  taf-bandage-ng bandage-ng reduce graph.gfa reduced.gfa
  taf-bandage-ng bandage-ng layout graph.gfa layout.csv
  taf-bandage-ng bandage-ng querypaths graph.gfa queries.fasta

Default upstream command:
  taf-bandage-ng -- --version
  taf-bandage-ng -- --help

Command-mode helpers:
  taf-bandage-ng makeblastdb -version
  taf-bandage-ng blastn -version
  taf-bandage-ng minimap2 --version
  taf-bandage-ng nhmmer -h
  taf-bandage-ng hmmsearch -h

Notes:
  - This app packages the official BandageNG v2026.4.1 Linux AppImage.
  - BLAST+, minimap2, and HMMER are included because BandageNG can call them
    for graph search workflows.
  - The helper prints the exact browser URL at startup.
  - Docker/Podman runs embed --init for more predictable Ctrl-C cleanup.
  - The upstream Linux AppImage is amd64. Docker/Podman arm64 hosts use
    amd64 emulation declared by this app; this is not native arm64 support.
  - Use --password if exposing noVNC beyond localhost.
  - The example binds the host port to 127.0.0.1. On shared machines, keep this
    local binding unless you have explicit access control.
  - Apptainer GUI/noVNC use is site-dependent because port, network, and X/VNC
    behavior vary across clusters.

Container:
  image: ghcr.io/taffish/bandage-ng:2026.4.1-r1
  backends: apptainer, podman, docker
  native platform: linux/amd64
  arm64 Docker/Podman hosts: amd64 emulation through --platform linux/amd64

Upstream:
  source: https://github.com/asl/BandageNG
  release: https://github.com/asl/BandageNG/releases/tag/v2026.4.1
  docs: https://github.com/asl/BandageNG/wiki
  license: GPL-3.0-or-later
  citation: BandageNG citation TBD upstream; original Bandage DOI
    10.1093/bioinformatics/btv383, PMID 26099265
