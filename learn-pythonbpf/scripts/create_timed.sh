#!/bin/bash
# BCC timed versions
for prog in tracepoint_1 print_pid print_long_str; do
  src="/root/learn-BCC/sys_enter_openat/without_map/${prog}.py"
  dst="/root/learn-BCC/sys_enter_openat/without_map/${prog}_timed.py"
  cp "$src" "$dst"
  sed -i '1s/^/import time\n/' "$dst"
  sed -i '/^from bcc/a\t0 = time.process_time()' "$dst"
  sed -i "/^b = BPF\|^bpf = BPF/a\\t1 = time.process_time()\nprint(f\"[TIMING] BPF init: {t1-t0:.3f}s CPU\")" "$dst"
done
# PBPF timed versions
for prog in tracepoint_1 print_pid print_long_str; do
  src="/root/learn-pythonbpf/sys_enter_openat/without_map/${prog}.py"
  dst="/root/learn-pythonbpf/sys_enter_openat/without_map/${prog}_timed.py"
  cp "$src" "$dst"
  sed -i 's/^import time$/import time/' "$dst"
  sed -i "/^from ctypes/a\\import time\nt0 = time.process_time()" "$dst"
  sed -i "/^b = BPF()/a\\t1 = time.process_time()\nprint(f\"[TIMING] BPF init: {t1-t0:.3f}s CPU\")" "$dst"
done
echo "created"
