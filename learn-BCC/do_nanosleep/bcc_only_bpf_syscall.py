from bcc import BPF
#import time

# Minimal program - just return 0
b = BPF(text="""
int mnop(void *ctx) {
    return 0;
}
""")

b.attach_kprobe(event="do_nanosleep", fn_name="mnop")
#time.sleep(13)
