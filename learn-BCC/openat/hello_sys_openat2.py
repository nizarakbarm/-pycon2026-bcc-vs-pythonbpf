from bcc import BPF
import time

bpf_text = """
int hello(void *ctx) {
    bpf_trace_printk("hello\\n");
    return 0;
}
"""

b = BPF(text=bpf_text,cflags=["-O3"])
b.attach_kprobe(event="do_sys_openat2", fn_name="hello")
#b.trace_print()
time.sleep(100)
