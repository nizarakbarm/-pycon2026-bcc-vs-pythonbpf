#!/bin/bash
rm -f /tmp/pbpf_ltrace_out.txt /tmp/pbpf_ltrace_lib.txt
ltrace -c -o /tmp/pbpf_ltrace_lib.txt /root/learn-pythonbpf/.venv/bin/python3 /root/learn-pythonbpf/sys_enter_openat/with_map/map_1_perf_timed_e100.py > /tmp/pbpf_ltrace_out.txt 2>&1 &
TRACE_PID=$!
sleep 2
sudo -u radare2 /tmp/gen_fast 2000000
sleep 5
pkill -INT -f "map_1_perf_timed"
sleep 3
echo "=== PBPF ltrace ==="
grep -E "\[TIMING\]|\[SUMMARY\]" /tmp/pbpf_ltrace_out.txt
echo "=== LIBRARY CALLS (top by time) ==="
sort -t'|' -k2 -rn /tmp/pbpf_ltrace_lib.txt 2>/dev/null | head -20
