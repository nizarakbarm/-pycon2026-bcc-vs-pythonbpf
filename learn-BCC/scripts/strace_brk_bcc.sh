#!/bin/bash
python3 /root/learn-BCC/sys_enter_openat/with_map/map_1_perf_timed.py > /tmp/bcc_brk_out.txt 2>&1 &
PY_PID=$!
sleep 2
strace -e trace=brk,mmap -c -p $PY_PID -o /tmp/bcc_brk_c.txt &
STRACE_PID=$!
sleep 0.5
sudo -u radare2 /tmp/gen_fast 200000
sleep 4
kill -INT $PY_PID
sleep 2
kill -INT $STRACE_PID 2>/dev/null
sleep 1
echo "=== TIMING ==="
grep -E "\[TIMING\]|\[SUMMARY\]" /tmp/bcc_brk_out.txt
echo "=== BRK/MMAP ==="
cat /tmp/bcc_brk_c.txt
