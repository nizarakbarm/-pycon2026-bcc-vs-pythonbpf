# PyCon 2026 — BCC vs Python-BPF eBPF Benchmark

Benchmark scripts and demo tooling for the talk **"BCC C-String Runtime vs Python-BPF AST AOT"** at PyCon ID 2026 (Aug 9) and PyCon Taiwan 2026 (Oct 17–18).

Compares two Python eBPF frameworks across **syscalls, CPU, memory, bytecode, and JIT** — starting from the simplest program and building up.

**Slides:** PyCon TW deck (vault `Spaces/PyCon-TW-2026/`) · **Scripts:** benchmark VM `vmdevnull`

---

## Environment

All scripts run on the benchmark VM (`vmdevnull`):

| | BCC | Python-BPF |
|:--|:----|:-----------|
| Location | `/root/learn-BCC/` | `/root/learn-pythonbpf/` |
| Interpreter | `/usr/bin/python3` | `/root/learn-pythonbpf/.venv/bin/python3` |
| Trigger | `/tmp/gen_fast` — fires N `unlink()` calls at uid=1002 | same |

Kernel 6.12.0 · openSUSE Leap 16.0 · single CPU.

---

## 1. Main scripts

Each benchmark program exists in **BCC + PBPF** pairs. `_timed` variants emit `[TIMING]` / `[SUMMARY]` lines for CPU measurement.

### Foundation — minimal program

| Program | BCC | PBPF | What it shows |
|:--------|:----|:-----|:--------------|
| `bpf_only_syscall` | `do_nanosleep/bcc_only_bpf_syscall.py` | `do_nanosleep/pythonbpf_only_bpf_syscall.py` | kprobe returns 0 — pure startup overhead |
| `bpf_only_syscall_timed` | `..._timed.py` | `..._timed.py` | adds `[TIMING]` output |

### Building Up — map + perf combination

| Program | BCC (`syscall_trigger/with_map/`) | PBPF | What it shows |
|:--------|:----------------------------------|:-----|:--------------|
| `map_1_perf_timed_timing` | `map_1_perf_timed_timing.py` | same | ❌ **WRONG pattern** — reads counter in callback → stale values |
| `map_1_perf_timed_count` | `map_1_perf_timed_count.py` | same | ✅ **CORRECT** — embedded counter at BPF time |
| `map_1_perf_timed` | `map_1_perf_timed.py` | same | with_map + full print (overflow trap source) |
| `map_1_perf_timed_empty` | `..._empty.py` | same | HashMap + perf, empty callback |
| `map_1_perf_timed_e100` | `..._e100.py` | same | print every 100th |
| `maps_with_struct_single` | — | `maps_with_struct_single.py` | struct-in-map-value (works, read-then-update) |
| `maps_with_struct_perf` | — | `maps_with_struct_perf.py` | struct-in-map-value (docs pattern — **llc crash**) |

### Per-event baseline — no HashMap in callback

| Program | BCC (`syscall_trigger/without_map/`) | PBPF | What it shows |
|:--------|:--------------------------------------|:-----|:--------------|
| `perf_timed` | `perf_timed.py` | same | perf buffer only — cleanest baseline |
| `perf_timed_empty` | `perf_timed_empty.py` | same | empty callback, struct parsing |
| `perf_empty_no_struct` | `perf_empty_no_struct.py` | same | empty callback, no struct → isolates struct_parser cost |
| `print_long_str_timed` | `print_long_str_timed.py` | same | format-string storage strategy (~100B) |
| `print_pid_timed` | `print_pid_timed.py` | same | short format string |

---

## 2. Running

### Without demo.sh — one command per framework

```bash
# BCC (init ~0.5s → sleep 2 before trigger)
/usr/bin/python3 /root/learn-BCC/syscall_trigger/with_map/map_1_perf_timed_count.py \
  > /tmp/bcc_count.log 2>&1 &
sleep 2; sudo -u radare2 /tmp/gen_fast 20
sleep 1; pkill -INT -f map_1_perf_timed_count
cat /tmp/bcc_count.log

# PBPF (init ~0.02s → sleep 1)
/root/learn-pythonbpf/.venv/bin/python3 /root/learn-pythonbpf/syscall_trigger/with_map/map_1_perf_timed_count.py \
  > /tmp/pbpf_count.log 2>&1 &
sleep 1; sudo -u radare2 /tmp/gen_fast 20
sleep 1; pkill -INT -f map_1_perf_timed_count
cat /tmp/pbpf_count.log
```

Replace `20` with the event count (e.g. `2000000` for 2M). `pkill -INT` triggers the program's SIGINT handler for a clean summary.

### With demo.sh — one script per program directory

Three scripts, one per program group. Each runs **BOTH frameworks** and captures: python timing + raw output, `strace -c` counts, full raw syscalls, and xlated/jited dumps.

```bash
# Foundation (no arg — single program)
bash /root/learn-BCC/do_nanosleep/demo.sh

# Building Up — pick one program, optional event count
bash /root/learn-BCC/syscall_trigger/with_map/demo.sh map_1_perf_timed_count    # 20 events default
bash /root/learn-BCC/syscall_trigger/with_map/demo.sh map_1_perf_timed_timing
bash /root/learn-BCC/syscall_trigger/with_map/demo.sh map_1_perf_timed_count 2000000  # 2M

# Per-event baseline — pick one
bash /root/learn-BCC/syscall_trigger/without_map/demo.sh perf_timed
bash /root/learn-BCC/syscall_trigger/without_map/demo.sh print_long_str
```

---

## 3. Checking demo.sh output

Each script writes to `<program-dir>/output/`:

```
<program-dir>/output/
  log/   ← .log files (program run output, xlated capture session)
  raw/   ← .txt files (strace -c summaries, full raw syscalls)
```

Example (count program):

```
/root/learn-BCC/syscall_trigger/with_map/output/
  log/map_1_perf_timed_count_BCC.log        # [TIMING] + per-event callback lines
  log/map_1_perf_timed_count_PBPF.log
  log/map_1_perf_timed_count_x_BCC.log      # xlated capture session
  log/map_1_perf_timed_count_x_PBPF.log
  raw/map_1_perf_timed_count_strace_BCC.txt # strace -c summary
  raw/map_1_perf_timed_count_strace_PBPF.txt
  raw/map_1_perf_timed_count_raw_BCC.txt    # full raw syscalls (with args)
  raw/map_1_perf_timed_count_raw_PBPF.txt
```

Terminal shows: raw output + `[TIMING]` lines, `strace -c` top syscalls, raw syscall **file path + line count + preview**, and xlated/jited dump with prog ID.

---

## 4. Benchmarks not covered by demo.sh

These need manual commands (see the vault atomic notes for full methodology):

| Benchmark | How | Notes |
|:----------|:----|:------|
| `perf stat` (cycles/instructions) | `perf stat -e cycles,instructions <program>` | startup CPU efficiency |
| `perf record -F 199` + flamegraph | `perf record -F 199 --call-graph dwarf -o out.data <program>` → `perf script \| stackcollapse-perf.pl \| flamegraph.pl` | where CPU goes at 2M |
| `perf probe` (PyBytes counts) | `perf probe -a PyBytes_FromStringAndSize` | py::bytes alloc counts |
| Startup strace with `-T` | `strace -c -T -f <program>` | per-syscall timing |
| `pyinstrument` | `python3 -m pyinstrument <program>` | startup call tree (NOT the `pyinstrument` CLI — Python 3.13 null-byte bug) |
| `scalene` | `scalene run --outfile out.json <program>` | line-level memory/CPU |
| `/usr/bin/time -v` | wrap the program | RSS, page faults |
| `bpftool prog dump xlated/jited` | keep program alive, then dump by ID | bytecode comparison |
| JIT instruction cost | `/root/jit_measurement/` framework (measure.c + measure_all.sh, 100M iterations) | per-instruction cycle cost |
| `maps_with_struct_perf.py` | direct run (compiles but **llc crash** — docs write-through pattern) | struct-in-map-value bug demo |

Full results: vault notes `Atlas/Dots/Things/eBPF/Benchmarks/` (`Embedded Counter Benchmark.md`, `Perf Buffer Overflow Mechanics.md`, `Python-BPF Struct-in-Map Value — llc Bug & Benchmark.md`, `bpf Syscall Comparison...`).

---

## 5. Reading the output

### `[TIMING]` lines (in the `.log` files)

```
[TIMING] BPF init CPU: 0.024s  wall: 0.049s     ← compile + load (process_time vs wall)
[TIMING] Setup CPU: 0.000s  wall: 0.000s        ← buffer setup
[TIMING] Poll loop CPU: 14.496s  wall: 61.1s    ← per-event processing (the key metric)
[TIMING] Total CPU: 14.523s  wall: 61.2s        ← everything
[SUMMARY] Events in map: 2000001                ← counter value at end
```

**Read:** `Poll loop CPU` is the fair per-event comparison. `CPU ÷ delivered = ns/event`.

### Callback lines (per delivered event)

```
CPU [0] UID 1002, comm: gen_fast, count: 19     ← sequential = correct (embedded counter)
CPU [0] UID 1002 comm: gen_fast, count: 20      ← repeated/stale = WRONG pattern
```

**Count delivered:** `grep -vcE "TIMING|THREAD|Starting|SUMMARY|LOST|CB_TIME" <log>`

### `strace -c` summary (`.txt`)

```
 83.31  0.123563  11   10511    read       ← BCC: kernel header reads
  7.26  0.010762  10    1013  1 poll       ← BCC poll loop
100.00  0.127405  —    16300  432 total
```

**Read:** BCC's `read` ~10K = `/proc/kallsyms` + kernel headers. PBPF's `epoll_wait` replaces `poll`; PBPF `bpf` count higher (feature probes + LINK_CREATE).

### Raw syscalls (`.txt`)

```
BCC:  perf_event_open(...BPF_OUTPUT...) = 9
      poll([{fd=9, events=POLLIN}], 1, 1)        ← direct fd poll
PBPF: perf_event_open(...BPF_OUTPUT...) = 10
      epoll_ctl(9, EPOLL_CTL_ADD, 10, {EPOLLIN}) ← fd 10 registered into epoll 9
      epoll_wait(9, [], 1, 1)                    ← wait on epoll set
```

**Read:** BCC attaches via `ioctl(PERF_EVENT_IOC_SET_BPF)`; PBPF via `bpf(BPF_LINK_CREATE)`. PBPF wraps the perf fd in an epoll set; BCC polls it directly.

### xlated / jited

```
xlated (verifier): 0: (b7) r0 = 0 / 1: (95) exit     ← 2 insns, identical both
jited (native): endbr64; nopl×2; push rbp; ...        ← 9 insns, identical
```

**Read:** byte-for-byte identical for the same program — all runtime differences are userspace dispatch, not BPF quality. Count program differs: BCC `(*count)++` = 3 in-place insns vs PBPF `update_elem` helper call.

### Key gotchas

- **BCC overflow artifact:** if BCC delivered far fewer than N events (e.g. 58% under perf record), its CPU is *not* comparable — it did less work + paid overflow-drain overhead. Always check delivery.
- **BTF warning is harmless:** `libbpf: BTF loading error: -EINVAL ... Member exceeds struct_size` — PBPF emits malformed BTF for struct maps; program still loads (BTF optional).
- **`lost_cb` signature:** BCC takes one arg (`cnt`); PBPF takes `(cpu, cnt)`.
- **Perf buffer ≠ ring buffer:** we use `BPF_MAP_TYPE_PERF_EVENT_ARRAY` (perf buffer), not `BPF_MAP_TYPE_RINGBUF`.

---

## 6. Output artifacts — `out_temp_log/`

Selected by **measurement tool** from the full scratch dump (only files cited in the talk notes were kept — scratch variants dropped). Organized for slide evidence:

| Tool | Artifacts (prefix `bcc_` / `pbpf_`) | Read as |
|:-----|:----------------------------------|:--------|
| Program run (python timing) | `cnt2m.log`, `cnt2m_v3.log`, `pt2m_perf.log`, `wm_full_2m.log`, `pf_*_2m.log`, `wm_2m_fg.log`, `wm2m_perf.log`, `wm2k_perf.log` | `[TIMING]` CPU lines → ns/event |
| FlameGraph | `*_2m.folded`, `*_2k.folded`, `*.folded` | foldstack input to flamegraph.pl |
| perf record raw | `map_1_perf_timed_count_2m.data`, `wm*_perf.data`, `pt2m_perf.data` | `perf report` / `perf script` |
| perf stat | `map_1_perf_timed_count_perfstat.txt`, `perf_perfstat.txt` | cycles/instructions totals |
| strace -c | `map_1_perf_timed_count_strace.txt`, `cnt_strace.txt`, `perf_strace.txt`, `strace_with{out,}_attach.txt` | syscall counts + totals |
| bpftool dump | `cnt_xlated.txt`, `cnt_jited.txt`, `tp_xlated_*.txt`, `tp_jited_*.txt`, `jited_*.txt` | bytecode comparison |
| pyinstrument | `map_1_perf_timed_count_pyinstrument.txt` | startup call tree |
| /usr/bin/time -v | `cnt_timev.txt`, `perf_timev.txt` | RSS, page faults |
| perf probe | `empty_probe.txt`, `no_struct_probe.txt` | PyBytes alloc counts |
| ltrace | `ltrace_lib.txt`, `ltrace_out.txt`, `ltrace_detail.txt` | libc call traces |
| cycles | `cycles.txt`, `cycles_dso.txt` | cycle attribution |
| JIT | `jit_tracepoint_sysc.txt` | per-instruction cost traces |

> 37 cited files from notes are **not recoverable** (were never saved to disk — intermediate captures, e.g. `bcc_2k.folded`, `jit_dump.txt`). Re-run the corresponding benchmark to regenerate.

## Repo layout
```
pycon_2026/
├── README.md
├── learn-BCC/        ← full copies from /root/learn-BCC/
│   ├── do_nanosleep/     (foundation programs + demo.sh)
│   ├── syscall_trigger/  (with_map/ + without_map/ + demo.sh)
│   ├── openat/
│   ├── scripts/
│   └── out/
├── learn-pythonbpf/  ← full copies from /root/learn-pythonbpf/
└── out_temp_log/     ← curated benchmark output artifacts (see §6)
```

This repo mirrors the benchmark VM's program trees. The authoritative live copies run on `vmdevnull`; these are snapshots for reproducibility. Rerun `scp -r /root/learn-BCC /root/learn-pythonbpf .` on the VM to refresh after new experiments.

## 7. Knowledge map — the MOC

> **[BCC vs Python-BPF Comparisons MOC](https://github.com/nizarakbarm/knowledge-pipeline/blob/main/Atlas/Maps/BCC%20vs%20Python-BPF%20Comparisons%20MOC.md)** — `Atlas/Maps/BCC vs Python-BPF Comparisons MOC.md` in the `knowledge-pipeline` repo.
The MOC is the index: it links all comparison notes (per-benchmark writeups, compiler-internals dumps, BTF profiling, struct-map llc bug, JIT cost framework), grouped by investigation type and framework internals. `[[wikilinks]]` are Obsidian-native — they don't resolve in plain Markdown, so read them in Obsidian.

Why the split: this repo is the **runnable** half (programs + scripts + raw output artifacts, §6); the vault is the **analysis** half (notes + MOC + talk slides). The README documents what to run; the MOC documents what it means.

Related Space (talk planning, benchmarks, travel): `Spaces/PyCon-TW-2026/` in the same vault.
