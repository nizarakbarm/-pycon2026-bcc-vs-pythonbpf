#!/bin/bash
set -e
echo "=== BCC strace ==="
rm -f /tmp/bcc_strace_out.txt /tmp/bcc_strace_sys.txt

strace -c -o /tmp/bcc_strace_sys.txt python3 /root/learn-BCC/sys_enter_openat/with_map/map_1_perf_timed.py > /tmp/bcc_strace_out.txt 2>&1 &
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
grep -E "\[TIMING\]|\[SUMMARY\]" /tmp/bcc_strace_out.txt
echo "=== STRACE -c ==="
cat /tmp/bcc_strace_sys.txt
