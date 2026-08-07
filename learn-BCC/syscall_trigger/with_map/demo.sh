#!/bin/bash
# Demo for THIS directory. Usage: bash demo.sh <program> [events]
#   program: map_1_perf_timed_timing | map_1_perf_timed_count
# Runs BOTH frameworks, captures: python timing, raw output, strace -c, raw syscalls, xlated/jited.
set -u
BCC=/usr/bin/python3
PBPF=/root/learn-pythonbpf/.venv/bin/python3
GEN=/tmp/gen_fast
LOG=/root/learn-BCC/syscall_trigger/with_map/output/log
RAW=/root/learn-BCC/syscall_trigger/with_map/output/raw
mkdir -p "$LOG" "$RAW"

PROGNAME="${1:?usage: demo.sh <map_1_perf_timed_timing|map_1_perf_timed_count> [events]}"
NEVENTS="${2:-20}"
if [ ! -f "/root/learn-BCC/syscall_trigger/with_map/$PROGNAME.py" ]; then
  echo "unknown program: $PROGNAME"; exit 1
fi

for fw in BCC PBPF; do
  if [ "$fw" = BCC ]; then PY=$BCC; PROG=/root/learn-BCC/syscall_trigger/with_map/$PROGNAME.py; SL=2
  else PY=$PBPF; PROG=/root/learn-pythonbpf/syscall_trigger/with_map/$PROGNAME.py; SL=1; fi

  echo; echo "════ $PROGNAME — $fw ════"
  "$PY" -u "$PROG" >"$LOG/${PROGNAME}_$fw.log" 2>&1 &
  PID=$!
  sleep "$SL"
  sudo -u radare2 "$GEN" "$NEVENTS" 2>/dev/null
  sleep 1
  kill -INT "$PID" 2>/dev/null; wait "$PID" 2>/dev/null
  echo "── raw output + python timing:"
  grep -E "count:|TIMING" "$LOG/${PROGNAME}_$fw.log" | head -12

  echo "── syscall counts (strace -c):"
  timeout -s INT 8 strace -c -f -o "$RAW/${PROGNAME}_strace_$fw.txt" "$PY" "$PROG" >/dev/null 2>&1
  grep -E "syscall|read$|bpf$|ioctl$|mmap$|close$|poll$|epoll_wait|total" "$RAW/${PROGNAME}_strace_$fw.txt" | head -12

  echo "── raw syscalls → file (full, -s 256):"
  timeout -s INT 8 strace -f -s 256 -e trace=bpf,perf_event_open,ioctl,epoll_wait,epoll_ctl,poll,ppoll,read -o "$RAW/${PROGNAME}_raw_$fw.txt" "$PY" "$PROG" >/dev/null 2>&1
  echo "  saved: $RAW/${PROGNAME}_raw_$fw.txt ($(wc -l < "$RAW/${PROGNAME}_raw_$fw.txt") lines)"
  echo "  preview (attach + poll mechanism):"
  grep -E "BPF_PROG_LOAD|BPF_LINK_CREATE|perf_event_open|PERF_EVENT_IOC_SET_BPF|PERF_EVENT_IOC_ENABLE|epoll_wait|epoll_ctl|poll\(" "$RAW/${PROGNAME}_raw_$fw.txt" | head -10

  echo "── xlated + jited:"
  "$PY" -u "$PROG" >"$LOG/${PROGNAME}_x_$fw.log" 2>&1 &
  PID=$!; sleep "$SL"
  PROGID=$(bpftool prog list 2>/dev/null | grep -E "^[0-9]+:" | grep -iE "$([ "$fw" = BCC ] && echo tracepoint__syscalls__sys_enter_unlink || echo trace_unlink)" | head -1 | cut -d: -f1)
  echo "prog id: ${PROGID:-none}"
  if [ -n "${PROGID:-}" ]; then
    bpftool prog dump xlated id "$PROGID" 2>/dev/null | head -12
    echo "── jited:"; bpftool prog dump jited id "$PROGID" 2>/dev/null | head -12
  fi
  kill -INT "$PID" 2>/dev/null; wait "$PID" 2>/dev/null
done
echo; echo "Done. Logs in $LOG/, raw in $RAW/"
