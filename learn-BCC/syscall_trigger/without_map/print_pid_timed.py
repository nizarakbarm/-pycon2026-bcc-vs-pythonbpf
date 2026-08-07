import time
from bcc import BPF
t0 = time.process_time()

program = """
TRACEPOINT_PROBE(syscalls, sys_enter_openat) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    bpf_trace_printk("PID %d\\n", pid);
    return 0;
}
"""

bpf = BPF(text=program)
t1 = time.process_time()
print(f"[TIMING] BPF init: {t1-t0:.3f}s CPU")
bpf.trace_print()
