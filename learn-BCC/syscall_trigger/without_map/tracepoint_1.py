from bcc import BPF

program = """
TRACEPOINT_PROBE(syscalls, sys_enter_openat) {
    bpf_trace_printk("12aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\\n");
    return 0;
}
"""

bpf = BPF(text=program)
bpf.trace_print()
