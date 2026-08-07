import time
from bcc import BPF
t0 = time.process_time()

program = """
TRACEPOINT_PROBE(syscalls, sys_enter_unlink) {
    bpf_trace_printk("This is a very long string that demonstrates BCC's ability to print longer messages from BPF programs using enhanced printf support\\n");
    return 0;
}
"""

bpf = BPF(text=program)
t1 = time.process_time()
print(f"[TIMING] BPF init: {t1-t0:.3f}s CPU")
