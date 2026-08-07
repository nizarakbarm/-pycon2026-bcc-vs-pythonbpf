#!/bin/bash
program="$1"
strace_out=$(strace -e bpf -T python3 $program 2>&1)

echo -e "$strace_out"

echo -e "time: $(grep -oP '<\K[^>]+' <<<"$strace_out" | awk '{s+=$1} END{print s" seconds"}')"
