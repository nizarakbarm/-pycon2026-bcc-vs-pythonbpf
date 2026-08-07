#!/bin/bash
set -e
echo "=== PBPF strace ==="
rm -f /tmp/pbpf_strace_out.txt /tmp/pbpf_strace_sys.txt

strace -c -o /tmp/pbpf_strace_sys.txt /root/learn-pythonbpf/.venv/bin/python3 /root/learn-pythonbpf/sys_enter_openat/with_map/map_1_perf_timed.py > /tmp/pbpf_strace_out.txt 2>&1 &
TRACE_PID=$!
echo "Strace PID=$TRACE_PID"

sleep 2
echo "Triggering gen_fast..."
sudo -u radare2 /tmp/gen_fast 2000000

echo "Waiting..."
sleep 5

echo "Sending SIGINT..."
pkill -2 -f "map_1_perf_timed"
sleep 3

echo "=== TIMING ==="
grep -E "\[THREAD\]|\[TIMING\]|\[SUMMARY\]" /tmp/pbpf_strace_out.txt
echo "=== STRACE -c ==="
cat /tmp/pbpf_strace_sys.txt
