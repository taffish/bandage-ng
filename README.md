# taf-bandage-ng

`taf-bandage-ng` packages [BandageNG](https://github.com/asl/BandageNG), a
modern Bandage fork for visualizing and inspecting de novo assembly graphs.

Package identity:

- name: `bandage-ng`
- command: `taf-bandage-ng`
- kind: `tool`
- version: `2026.9.1-r1`
- TAFFISH packaging license: Apache-2.0
- upstream release: BandageNG `v2026.9.1`
- native image platform: `linux/amd64`

## What This App Packages

BandageNG is primarily a Qt desktop application for GFA/FASTG assembly graphs,
and also exposes headless `info`, `image`, `reduce`, `layout`, and `querypaths`
subcommands. This app provides both surfaces:

- `bandage-ng-gui`: supervised Xvfb + twm + x11vnc + noVNC desktop;
- `bandage-ng`: direct launcher with clearer no-display diagnostics;
- `BandageNG`: unmodified upstream command through TAFFISH command mode;
- `bandage-ng-smoke`: packaging and GUI-lifecycle self-test;
- BLAST+, minimap2, and HMMER, which BandageNG invokes for graph searches.

Version `2026.9.1` adds drawing/reducing the complete connected component that
contains selected nodes, paths, or walks. The upstream Qt bundle was also
updated.

## Scope

This app supports interactive graph loading, drawing, node/path inspection,
image export, graph reduction, layout export, query-path analysis, and the
external graph-search commands used by BandageNG.

It does not assemble reads, choose a biologically appropriate graph region,
provide a shared reference database/model, or replace manual review of complex
graph visualizations.

## Install and Inspect

```sh
taf update
taf install bandage-ng
taf-bandage-ng --version
taf-bandage-ng -- --version
taf-bandage-ng -- --helpall
```

For a local unpublished candidate, `taf install --from .` is available from the
app checkout. `docs/help.md` intentionally documents only installed-wrapper
commands.

For local GUI development, do not use long-running `taf run` with TAFFISH
0.11.0: that entry currently buffers child output and does not propagate
Ctrl-C cleanup correctly. Build and use the real target wrapper instead:

```sh
taf build
TAFFISH_DOCKER_RUN_ARGS="-p 127.0.0.1:8765:5801" \
TAFFISH_CONTAINER_BACKEND=docker \
target/taf-bandage-ng-v2026.9.1-r1 bandage-ng-gui \
  --port 5801 --host-port 8765
```

## GUI Usage

Docker:

```sh
TAFFISH_DOCKER_RUN_ARGS="-p 127.0.0.1:8765:5801" \
TAFFISH_CONTAINER_BACKEND=docker \
taf-bandage-ng bandage-ng-gui --port 5801 --host-port 8765
```

Podman:

```sh
TAFFISH_PODMAN_RUN_ARGS="-p 127.0.0.1:8765:5801" \
TAFFISH_CONTAINER_BACKEND=podman \
taf-bandage-ng bandage-ng-gui --port 5801 --host-port 8765
```

Apptainer shares the host network and therefore does not use Docker-style port
publishing:

```sh
TAFFISH_CONTAINER_BACKEND=apptainer \
taf-bandage-ng bandage-ng-gui --bind-address 127.0.0.1 \
  --port 8765 --host-port 8765
```

Wait for `BandageNG GUI is ready.`, then open the printed URL. To preload a
graph, pass the upstream `load` subcommand after the helper's `--`:

```sh
taf-bandage-ng bandage-ng-gui -- load graph.gfa --draw
```

The upstream `--draw` option can leave the canvas blank for a small graph in an
interactive session. When that occurs, click **Draw graph** in the left panel;
the graph is already loaded.

The helper prints the URL, SSH command, stop instruction, log directory, and
requested layout before starting the first long-running process. Readiness
requires Xvfb, twm, x11vnc, noVNC, and a stable visible BandageNG window.
All five components remain supervised after readiness; a critical component
failure is reported with its log. Ctrl-C returns 130 and TERM returns 143 after
bounded cleanup.

The default desktop is `1440x900`. The main workbench is fitted below a
48-pixel top safe area so its title and menus remain clear of noVNC chrome.
`--geometry WxH`, `--window-top-offset PX`, and `--no-fit-window` adjust this
behavior. `resize=scale` changes browser rendering, not the upstream window.

For a remote host, keep the listener on loopback and tunnel it:

```sh
ssh -N -L 8765:127.0.0.1:8765 user@server
```

noVNC is plain HTTP. A VNC password can be supplied with `--password`, but it
can appear in shell history/process listings; loopback plus SSH or a protected
site reverse proxy is the preferred boundary.

## Backend Capability Matrix

| Capability | Docker | Podman | Apptainer | Boundary |
| --- | --- | --- | --- | --- |
| CLI/headless | Supported; app requests `linux/amd64` | Supported; app requests `linux/amd64` | Supported on amd64 Linux | Docker/Podman on arm64 use emulation, not native arm64 |
| GUI/noVNC | Host loopback `-p HOST:5801` | Host loopback `-p HOST:5801` | Host-network loopback, no `-p` | Use an unused host port; site firewall policy still applies |
| Session signals | App embeds `--init`; helper handles INT/TERM | Helper handles INT/TERM without a host `catatonit` dependency | Helper handles INT/TERM in the SIF | Complete critical-process cleanup is part of the smoke contract |
| Writable state | Current directory/output bind plus `/tmp` | Current directory/output bind plus `/tmp` | Current directory/output bind plus SIF runtime `/tmp` | GUI config, HOME, logs, and runtime state are redirected to session `/tmp` |

The container has only a native `linux/amd64` build because the official
upstream AppImage is an x86-64 ELF. The backend entries in `src/main.taf`
supply `--platform linux/amd64` to Docker and Podman, while `--init` is
Docker-only. Podman therefore does not require host `catatonit`; users do not
need to repeat these app-intrinsic arguments.

## Headless CLI

```sh
taf-bandage-ng bandage-ng info graph.gfa
taf-bandage-ng bandage-ng image graph.gfa graph.svg
taf-bandage-ng bandage-ng reduce graph.gfa reduced.gfa
taf-bandage-ng bandage-ng layout graph.gfa graph.layout
taf-bandage-ng bandage-ng querypaths graph.gfa queries.fa result
```

TAFFISH 0.11.0 automatic command mode removes ordinary shell quoting before
the container command is reconstructed. For an input or output path containing
spaces, preserve literal double quotes inside a shell-quoted argument. This
exact form is validated with the real Docker wrapper:

```sh
taf-bandage-ng bandage-ng image \
  '"graph with spaces.gfa"' '"output with spaces.svg"'
```

Draw the component containing node `a1`:

```sh
taf-bandage-ng bandage-ng image graph.gfa component.svg \
  --scope aroundcomponent --nodes a1
```

`--nodes`, `--path`, and `--walk` accept comma-separated seeds and can be
combined. At least one seed is required with `--scope aroundcomponent`.

Option-leading arguments for the default upstream executable go after the
TAFFISH separator:

```sh
taf-bandage-ng -- --version
taf-bandage-ng -- --helpall
```

Other packaged executables remain available through automatic command mode:

```sh
taf-bandage-ng makeblastdb -version
taf-bandage-ng minimap2 --version
taf-bandage-ng hmmsearch -h
```

## Inputs and Outputs

| Task | Input | Key output |
| --- | --- | --- |
| GUI/load, info, image, reduce, layout | GFA/FASTG graph | interactive view, text summary, `.svg`/`.png`/`.jpg`, GFA, `.layout`/`.tsv` |
| querypaths | graph plus query FASTA | TSV prefix and optional FASTA files |
| GUI Logan download | user-selected Logan accession and unitigs/contigs choice | one `.fa.zst` in a user-selected writable directory |

Run in a writable host directory or use an explicit backend bind for persistent
outputs. The helper itself stores only ephemeral configuration, HOME, logs, and
X runtime files under a per-session `/tmp/bandage-ng-gui-*` directory.

## Resources, Network, and Dependencies

No database, machine-learning artifact, taxonomy bundle, or reusable reference
package is required for ordinary BandageNG graph work. Its project graph inputs
do not need a personal or system-wide resource installer.

The GUI contains an upstream Logan download dialog. It performs an explicit,
user-triggered HTTPS request for one accession's unitigs or contigs and can save
that project input to a chosen directory. This is not automatic discovery, a
versioned shared database, or a reusable catalog; it is not invoked by smoke or
offline graph commands. Users must review the Logan data terms and select a
writable mounted destination.

BLAST+, minimap2, and HMMER remain installed because upstream source invokes
`makeblastdb`, `blastn`, `tblastn`, `minimap2`, `nhmmer`, and `hmmsearch` from
GUI search workflows. Removing them merely to shrink the image would leave
advertised upstream functionality incomplete.

## Image and Provenance

The Dockerfile uses the exact amd64 manifest for `debian:13-slim`, downloads
the official `BandageNG-Linux-17665e2.AppImage`, verifies SHA-256
`a522ad48a588fcefddbcda9dbc9e6d5d8bc829f80b2fe1330cb4fd17f27300cb`,
and extracts its SquashFS payload at offset `944632`. It records:

- upstream tag `v2026.9.1`;
- upstream commit `17665e2b57ad45138c8d809a77915b2aabfa3b24`;
- asset name, digest, and extraction offset;
- the pinned upstream GPL-3.0 license text.

The noVNC `1.7.0` and websockify `0.13.0` source archives are independently
checksummed. Debian build caches do not enter the final image, and apt lists are
removed in the same installation layers. The lightweight `twm` window manager
avoids pulling a larger desktop/rendering stack solely for window placement.

## Testing

The manifest smoke suite runs each command in a fresh offline container. It
checks identity/provenance, upstream and launcher versions, every packaged
external search executable, a tiny GFA info path, connected-component
`reduce`, connected-component SVG rendering, GUI starting-before-ready,
HTTP/window readiness, fitted geometry, TERM 143, startup INT 130, invalid
arguments, and window-manager failure before and after readiness.

The same exact commands are also run with a read-only image root and only an
explicit writable `/tmp`. Docker/Podman receipts, an actual read-only Apptainer
SIF derived from the same candidate OCI content, real-wrapper runs, browser
pointer/menu evidence, path-with-spaces handling, real GUI SVG export,
image-size profiling, and dry-run publication are final candidate gates; their
current result is reported in the release handoff rather than hard-coded into
this immutable project description.

Smoke proves packaging and a minimal functional path, not scientific
interpretation of a production assembly graph.

## Troubleshooting

- No URL yet: wait for `BandageNG GUI is ready.`; the earlier starting card is
  intentionally not a readiness claim.
- Port in use: change both the host mapping/host-network port and
  `--host-port`; for Apptainer also change `--port` to the same unused port.
- Blank or cropped desktop: use the printed geometry, try a larger
  `--geometry`, and keep `resize=scale`; only use `--no-fit-window` when native
  sizing is intentional.
- GUI closes unexpectedly: inspect the printed session log directory; the
  helper names the failed critical component and prints its log tail.
- Headless `bandage-ng` reports no display: use a CLI subcommand or launch
  `bandage-ng-gui`; bare BandageNG means desktop mode.

## License and Citation

TAFFISH packaging is Apache-2.0. BandageNG remains GPL-3.0-or-later and its
license text is preserved in the image. Upstream currently lists the BandageNG
citation as TBD. For the original Bandage publication, cite Wick et al. (2015),
*Bioinformatics*, DOI
[10.1093/bioinformatics/btv383](https://doi.org/10.1093/bioinformatics/btv383),
PMID 26099265.

- source: <https://github.com/asl/BandageNG>
- release: <https://github.com/asl/BandageNG/releases/tag/v2026.9.1>
- documentation: <https://github.com/asl/BandageNG/wiki>
