import time
from bcc import BPF
t0 = time.process_time()

program = """
TRACEPOINT_PROBE(syscalls, sys_enter_openat) {
    bpf_trace_printk("12aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\\n");
    return 0;
}
"""

bpf = BPF(text=program)
t1 = time.process_time()
print(f"[TIMING] BPF init: {t1-t0:.3f}s CPU")
bpf.trace_print()
