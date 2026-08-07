#!/bin/bash
# Demo for THIS directory: bpf_only_syscall (kprobe/do_nanosleep, return 0)
# Runs BOTH frameworks, captures: python timing, strace -c, xlated/jited.
set -u
BCC=/usr/bin/python3
PBPF=/root/learn-pythonbpf/.venv/bin/python3
SIGWRAP='import signal,runpy,sys; signal.signal(signal.SIGINT, signal.SIG_DFL); runpy.run_path(sys.argv[1], run_name="__main__")'
LOG=/root/learn-BCC/do_nanosleep/output/log
RAW=/root/learn-BCC/do_nanosleep/output/raw
mkdir -p "$LOG" "$RAW"

for fw in BCC PBPF; do
  if [ "$fw" = BCC ]; then PY=$BCC; PROG=/root/learn-BCC/do_nanosleep/bcc_only_bpf_syscall_timed.py; SL=2.5
  else PY=$PBPF; PROG=/root/learn-pythonbpf/do_nanosleep/pythonbpf_only_bpf_syscall_timed.py; SL=2.5; fi
  echo; echo "════ $fw — python timing + raw output ════"
  timeout -s INT 5 "$PY" -u -c "$SIGWRAP" "$PROG" 2>&1 | grep -E "TIMING|Ready" || true

  echo; echo "════ $fw — syscall counts (strace -c, startup) ════"
  timeout -s INT 8 strace -c -f -o "$RAW/strace_$fw.txt" "$PY" "$PROG" >/dev/null 2>&1
  grep -E "syscall|read$|bpf$|ioctl$|mmap$|execve$|close$|total" "$RAW/strace_$fw.txt" | head -12


  echo "── raw syscalls → file (full, -s 256):"
  timeout -s INT 8 strace -f -s 256 -e trace=bpf,perf_event_open,ioctl,epoll_wait,epoll_ctl,poll,ppoll,read -o "$RAW/raw_$fw.txt" "$PY" "$PROG" >/dev/null 2>&1
  echo "  saved: $RAW/raw_$fw.txt ($(wc -l < "$RAW/raw_$fw.txt") lines)"
  echo "  preview (attach + poll mechanism):"
  grep -E "BPF_PROG_LOAD|BPF_LINK_CREATE|perf_event_open|PERF_EVENT_IOC_SET_BPF|PERF_EVENT_IOC_ENABLE|epoll_wait|epoll_ctl|poll\(" "$RAW/raw_$fw.txt" | head -10

  echo; echo "════ $fw — xlated + jited ════"
  "$PY" -u -c "$SIGWRAP" "$PROG" >"$LOG/x_$fw.log" 2>&1 &
  PID=$!; sleep "$SL"
  PROGID=$(bpftool prog list 2>/dev/null | grep -E "^[0-9]+:" | grep -iE "a04f5eef06a7f555" | head -1 | cut -d: -f1)
  echo "prog id: ${PROGID:-none}"
  if [ -n "${PROGID:-}" ]; then
    bpftool prog dump xlated id "$PROGID" 2>/dev/null | head -12
    echo "── jited:"; bpftool prog dump jited id "$PROGID" 2>/dev/null | head -12
  fi
  kill -INT "$PID" 2>/dev/null; wait "$PID" 2>/dev/null
done
