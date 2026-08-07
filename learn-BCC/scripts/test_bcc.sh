#!/bin/bash
rm -f /tmp/bcc_test_out.txt /tmp/bcc_test_time.txt
python3 /root/learn-BCC/sys_enter_openat/with_map/map_1_perf_timed.py > /tmp/bcc_test_out.txt 2>&1 &
PY_PID=$!
echo "BCC PID=$PY_PID"
sleep 2
echo "Run: sudo -u radare2 /tmp/gen_fast 2000000"
echo "Then: kill -INT $PY_PID"
echo "Then: cat /tmp/bcc_test_out.txt | grep -E '\[TIMING\]|\[SUMMARY\]'"
