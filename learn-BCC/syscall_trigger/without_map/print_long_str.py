from bcc import BPF

program = """
TRACEPOINT_PROBE(syscalls, sys_enter_openat) {
    bpf_trace_printk("This is a very long string that demonstrates BCC's ability to print longer messages from BPF programs using enhanced printf support\\n");
    return 0;
}
"""

bpf = BPF(text=program)
bpf.trace_print()
