#!/bin/bash
set -e
echo "=== Starting BCC test ==="
rm -f /tmp/bcc_test_out.txt

python3 /root/learn-BCC/sys_enter_openat/with_map/map_1_perf_timed.py > /tmp/bcc_test_out.txt 2>&1 &
echo "Started, PID=$!"

sleep 2
echo "Triggering gen_fast..."
sudo -u radare2 /tmp/gen_fast 2000000

echo "Waiting for events..."
sleep 5

echo "Sending SIGINT..."
pkill -2 -f "map_1_perf_timed"
sleep 3

# Check if still alive, try harder
if pgrep -f "map_1_perf_timed" > /dev/null 2>&1; then
   echo "Still alive, trying SIGTERM..."
   pkill -15 -f "map_1_perf_timed" 2>/dev/null
   sleep 2
fi

echo "=== RESULTS ==="
grep -E "\[THREAD\]|\[TIMING\]|\[SUMMARY\]" /tmp/bcc_test_out.txt
echo "=== Done ==="
