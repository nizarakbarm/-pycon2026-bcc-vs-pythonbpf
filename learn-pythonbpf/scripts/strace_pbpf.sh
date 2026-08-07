#!/bin/bash
set -e

# Start Python
/root/learn-pythonbpf/.venv/bin/python3 /root/learn-pythonbpf/sys_enter_openat/with_map/map_1_perf_timed.py > /tmp/pbpf_strace_out.txt 2>&1 &
PY_PID=$!
echo "Python PID=$PY_PID"

# Wait for poll loop
sleep 2

# Attach strace
strace -c -p $PY_PID -o /tmp/pbpf_strace_c.txt &
STRACE_PID=$!
echo "Strace PID=$STRACE_PID"
sleep 0.5

# Trigger events
sudo -u radare2 /tmp/gen_fast 50000
echo "Gen done"

# Wait for events to process
sleep 4

# Kill Python with INT
kill -INT $PY_PID
sleep 2

# Kill strace
kill -INT $STRACE_PID 2>/dev/null
sleep 1

echo "=== TIMING ==="
grep -E "\[TIMING\]|\[SUMMARY\]" /tmp/pbpf_strace_out.txt

echo "=== STRACE -c ==="
cat /tmp/pbpf_strace_c.txt
