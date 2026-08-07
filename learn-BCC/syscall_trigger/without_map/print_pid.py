from bcc import BPF

program = """
TRACEPOINT_PROBE(syscalls, sys_enter_openat) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    bpf_trace_printk("PID %d\\n", pid);
    return 0;
}
"""

bpf = BPF(text=program)
bpf.trace_print()
