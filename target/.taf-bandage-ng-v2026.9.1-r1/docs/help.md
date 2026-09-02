taf-bandage-ng 2026.9.1-r1

Purpose:
  Inspect GFA/FASTG assembly graphs in a browser-served BandageNG desktop, or
  run reproducible graph info, render, reduce, layout and querypaths commands.

Usage:
  taf-bandage-ng -- --version
  taf-bandage-ng -- --helpall
  taf-bandage-ng bandage-ng-gui --help

Start the GUI with Docker:
  TAFFISH_DOCKER_RUN_ARGS="-p 127.0.0.1:8765:5801" \
  TAFFISH_CONTAINER_BACKEND=docker \
    taf-bandage-ng bandage-ng-gui --port 5801 --host-port 8765

Start the GUI with Podman:
  TAFFISH_PODMAN_RUN_ARGS="-p 127.0.0.1:8765:5801" \
  TAFFISH_CONTAINER_BACKEND=podman \
    taf-bandage-ng bandage-ng-gui --port 5801 --host-port 8765

Start the GUI with Apptainer:
  TAFFISH_CONTAINER_BACKEND=apptainer \
    taf-bandage-ng bandage-ng-gui --bind-address 127.0.0.1 \
      --port 8765 --host-port 8765
  Apptainer shares the host network and has no -p mapping; use an unused port.

GUI steps:
  1. Wait for "BandageNG GUI is ready.", then open the printed host URL.
  2. Load a GFA/FASTG graph, draw and inspect nodes, paths or graph searches.
  3. Press Ctrl-C in the launching terminal to stop the complete session.
  Preload a graph with:
    taf-bandage-ng bandage-ng-gui -- load graph.gfa --draw
  If the upstream canvas is still blank, click "Draw graph" in the left panel.
  Logs and observed window geometry are printed before/at readiness.

Remote GUI access:
  Keep the service on loopback and run locally:
    ssh -N -L 8765:127.0.0.1:8765 user@server
  Then open the printed URL. noVNC is plain HTTP; protect sensitive graphs.

Headless graph tasks:
  taf-bandage-ng bandage-ng info graph.gfa
  taf-bandage-ng bandage-ng image graph.gfa graph.svg
  taf-bandage-ng bandage-ng reduce graph.gfa reduced.gfa
  taf-bandage-ng bandage-ng layout graph.gfa graph.layout
  taf-bandage-ng bandage-ng querypaths graph.gfa queries.fa result

Paths containing spaces (TAFFISH 0.11.0):
  Preserve each such path as a literal quoted argument:
    taf-bandage-ng bandage-ng image \
      '"graph with spaces.gfa"' '"output with spaces.svg"'

Draw one complete connected component (new in 2026.9.1):
  taf-bandage-ng bandage-ng image graph.gfa component.svg \
    --scope aroundcomponent --nodes NODE_ID
  Use --path NAME or --walk NAME instead of/in addition to --nodes. Multiple
  seeds are comma-separated. At least one seed is required.

Inputs and outputs:
  Inputs: GFA/FASTG assembly graphs; querypaths also needs query FASTA.
  Images: .svg, .png or .jpg. Layout output: .layout or .tsv.
  Reduce writes GFA; querypaths writes a TSV prefix and optional FASTA files.
  Work in a writable directory so output paths remain available on the host.

Packaged graph-search tools:
  taf-bandage-ng makeblastdb -version
  taf-bandage-ng blastn -version
  taf-bandage-ng minimap2 --version
  taf-bandage-ng hmmsearch -h

Runtime boundaries:
  The official Linux AppImage is native linux/amd64 only. Docker/Podman on
  arm64 use app-declared amd64 emulation; this is not native arm64 support.
  Apptainer requires an amd64 Linux host.
  The GUI's Logan download action is explicit network I/O for one accession;
  it is not a packaged reusable resource. Save it to a writable mounted path.
  Normal offline graph inspection and smoke do not download data.
  Use --password only when required; prefer loopback plus SSH over exposure.

More documentation: https://github.com/taffish/bandage-ng
